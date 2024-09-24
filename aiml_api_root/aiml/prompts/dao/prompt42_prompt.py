import logging
from typing import List, Optional, Any, Dict, Union

from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from pydantic import BaseModel, Field, validator, ValidationError, field_validator, BeforeValidator, model_validator
import json
import jsonschema
from jsonschema.exceptions import ValidationError as JSONSchemaValidationError


class ProblemDefinition(BaseModel):
    description: str
    subproblems: List[str] = Field(default_factory=list, description="List of smaller, manageable subproblems.")

    def __str__(self):
        subproblems = '\n'.join(self.subproblems)
        return f"{self.description}\n{subproblems}"

    @field_validator('description', mode="before")
    @classmethod
    def normalize_description(cls, v: Union[str, List[str]]) -> str:
        if isinstance(v, list):
            return ' '.join(v)
        return v

    class Config:
        json_schema_extra = {
            "properties": {
                "description": {
                    "anyOf": [
                        {"type": "string"},
                        {"type": "array", "items": {"type": "string"}}
                    ]
                }
            }
        }


class InputElement(BaseModel):
    key: str = Field(..., description="The key or name of the input.")
    type: str = Field("str", description="Type of the input. Defaults to 'str'.")
    input_schema: Optional[str] = Field(None,
                                        description="Optional JSON schema for validating the input value.",
                                        alias="schema")
    value: Any = Field(None, description="The actual value of the input.")

    def __str__(self) -> str:
        """
        Returns: teh string as <key>value</key>
        Does not support schema and datatypes yet.
        """
        return "<{0}>{1}</{0}>".format(self.key, self.value)

    @field_validator('input_schema')
    @classmethod
    def validate_json_schema(cls, value: str) -> Union[None, str]:
        if value is None:
            return value
        try:
            # Try loading the schema as JSON to validate its format
            loaded_schema = json.loads(value)
            # Validate if it's a valid JSON schema
            jsonschema.Draft7Validator.check_schema(loaded_schema)
        except (json.JSONDecodeError, JSONSchemaValidationError) as e:
            raise ValueError(f"Invalid JSON schema: {str(e)}")
        return value


class OutputSpecification(BaseModel):
    expected_format: str = Field("JSON", description="Expected format of the output.")
    output_schema: Optional[str] = Field(None, description="Schema that the output should adhere to.",
                                         alias="schema")
    examples: List[str] = Field(default_factory=list,
                                description="Examples to guide the AI in generating correct outputs.")

    def __str__(self) -> str:
        output = """
                <output>
                    <format> {format} </format>
                    <schema> {schema} </schema>
                </output>                    
                """.format(format=self.expected_format, schema=self.output_schema)
        if self.examples:
            output += """
                      <output_examples>
                            {examples}
                      </output_examples>
                      """.format(examples="\n".join(self.examples))
        return output


class BehavioralConstraints(BaseModel):
    behavioral_constraints: List[str] = Field(default_factory=list, description="Rules governing AI behavior.")
    content_constraints: List[str] = Field(default_factory=list,
                                           description="Content that the AI should avoid or prohibit.")
    default_responses: List[str] = Field(default_factory=list,
                                         description="Fallback actions if the AI encounters conflicts or is unable to fulfill a request.")


class QualityGuidelines(BaseModel):
    guidelines_for_quality: List[str] = Field(default_factory=list,
                                              description="Guidelines for ensuring the quality of the AI's outputs.")
    norms_for_assumptions: List[str] = Field(default_factory=list,
                                             description="Explicit norms for assumptions the AI can make.")
    extra_configs: Optional[Dict[str, Any]] = Field(default_factory=list, description="additional behavior configs.")


class TaskExample(BaseModel):
    example_task: str = Field("Provide an example task here", description="A task example to guide the AI.")

    @field_validator('example_task', mode="before")
    @classmethod
    def normalize_description(cls, v: Union[str, List[str]]) -> str:
        if isinstance(v, list):
            return '\n'.join(v)
        return v


class Prompt42(BaseModel):
    problem_definition: ProblemDefinition = Field(default_factory=ProblemDefinition)
    requirements_for_inputs: List[InputElement] = Field(default_factory=list,
                                                        description="List of input elements required for the task.")
    output_specifications: OutputSpecification = Field(default_factory=OutputSpecification)
    manage_constraints: BehavioralConstraints = Field(default_factory=BehavioralConstraints)
    parameterize_behavior: QualityGuidelines = Field(default_factory=QualityGuidelines)
    task_examples: List[TaskExample] = Field(default_factory=list, description="List of example tasks to guide the AI.")

    def create_prompt(self, include_output: bool= False) -> Dict[str, str]:
        system_instructions = (f"""{str(self.problem_definition)} 
                               {str(self.output_specifications) 
                                    if include_output else ""}""")
        if self.task_examples:
            system_instructions += f"""
                                    {[str(ex) for ex in self.task_examples]}                       
                                    """
        user_message = " ".join([str(ip) for ip in self.requirements_for_inputs])
        return {"system": system_instructions, "user": user_message}


def create_lc_prompt(generated_prompt: Prompt42) -> ChatPromptTemplate:
    logging.info(generated_prompt.manage_constraints.behavioral_constraints)
    system_prompt_text = f""" {generated_prompt.problem_definition.json} 
                            {generated_prompt.manage_constraints.behavioral_constraints}
                            {generated_prompt.manage_constraints.content_constraints}
    """
    logging.info(system_prompt_text)
    prompt = ChatPromptTemplate.from_messages(
        [
            (
                "system",
                system_prompt_text,
            ),
            MessagesPlaceholder(variable_name="messages"),
        ]
    )
    return prompt




#
#
# # Example template JSON
# template_prompt42 = Prompt42(
#     problem_definition=ProblemDefinition(
#         description="Generate a prescreener for a clinical trial based on the provided information and constraints.",
#         subproblems=[
#             "1. Retrieve the trial description from the 'description' field within the requirements for inputs.",
#             "2. Retrieve the eligibility criteria from the 'eligibility' field within the requirements for inputs.",
#             "3. Ensure the generated prescreener adheres to the constraints specified in the 'manage_constraints' field.",
#             "4. Follow the guidelines outlined in the 'parameterize_behavior' field when generating the prescreener.",
#             "5. Output the result as a JSON object that conforms to the output specification:",
#             "   - The prescreener must conform to the prescreener schema defined in 'output_specifications.schema.prescreener_schema'.",
#             "   - The response must conform to the prescreener response schema defined in 'output_specifications.schema.prescreener_response_schema'."
#         ]
#     ),
#     requirements_for_inputs=[
#         InputElement(
#             key="input_1",
#             type="str",
#             schema=None,
#             value="Example value or reference to the input"
#         ),
#         InputElement(
#             key="input_2",
#             type="JSON",
#             schema=None,
#             value="{}"  # Placeholder for a JSON object
#         )
#     ],
#     output_specifications=OutputSpecification(
#         expected_format="JSON",
#         schema={
#                 "prescreener_response": "prescreener_response_schema.json",
#                 "prescreener": "prescreener_schema.json",
#             },
#         examples=[
#             "Example 1: Describe the output structure.",
#             "Example 2: Another example output."
#         ]
#     ),
#     manage_constraints=BehavioralConstraints(
#         behavioral_constraints=[
#             "Behavioral constraint 1: Define how the AI should behave.",
#             "Behavioral constraint 2: Another behavioral guideline."
#         ],
#         content_constraints=[
#             "Content constraint 1: Content to avoid or prohibit.",
#             "Content constraint 2: Another content restriction."
#         ],
#         default_responses=[
#             "Default response 1: Action if a conflict occurs.",
#             "Default response 2: Another fallback action."
#         ]
#     ),
#     parameterize_behavior=QualityGuidelines(
#         guidelines_for_quality=[
#             "Guideline 1: Ensure clarity in output.",
#             "Guideline 2: Maintain consistency."
#         ],
#         norms_for_assumptions=[
#             "Norm 1: Assumptions AI can make.",
#             "Norm 2: Another assumption guideline."
#         ]
#     ),
#     task_examples=[
#         TaskExample(
#             example_task="Example task 1: Describe a simple task."
#         ),
#         TaskExample(
#             example_task="Example task 2: Describe a more complex task."
#         )
#     ]
# )
