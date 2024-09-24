import json
import logging
from pathlib import Path
from typing import List, Dict

from langchain_core.prompts import ChatPromptTemplate

from aiml import settings
from aiml.prompts.dao.prompt42_prompt import Prompt42, ProblemDefinition, InputElement, OutputSpecification, \
    BehavioralConstraints, QualityGuidelines, TaskExample
from aiml.schemas import schema_utils


def get_creatives_template() -> dict:
    prompt_template_root = settings.prompts["creatives"]["templates"]
    generator_prompt = settings.prompts["creatives"]["prompt42"]["generator"]
    prompt_template_file = (f"{Path(settings.__file__).parent}/"
                            f"{prompt_template_root}{generator_prompt}")
    with open(prompt_template_file, 'r') as file:
        return json.load(file)


def generate_creatives_prompt(
        customer_id: str,
        description: str,
        eligibility: str,
        output_examples: List[Dict[str, str]] = None,
        examples: List[Dict[str, str]] = None
) -> Dict[str, str]:
    if not (customer_id and description and eligibility):
        raise (RuntimeError("""Cannot create a prompt without description, eligibility, 
                            or customer_id. Refer to the prompt template"""))

    prompt42_template = get_creatives_template()
    problem_definition = ProblemDefinition(**prompt42_template["problem_definition"])
    logging.debug(problem_definition)
    requirements_for_inputs = [
        InputElement(
            key="description",
            type="str",
            schema=None,
            value=description
        ),
        InputElement(
            key="eligibility",
            type="str",
            schema=None,
            value=eligibility
        )
    ]
    output_spec = get_output_spec(customer_id)
    output_ex = prompt42_template.get(
                        "output_specifications", {}).get("examples", None)
    if output_ex or output_examples:
        output_spec.examples = [str(ex) for ex in output_ex]
    constraints = prompt42_template["manage_constraints"]
    manage_constraints = BehavioralConstraints(
        behavioral_constraints=constraints["behavioral_constraints"],
        content_constraints=constraints["content_constraints"],
        default_responses=constraints["default_responses"]
    )
    behavior_params = prompt42_template["parameterize_behavior"]
    parameterize_behavior = QualityGuidelines(
        guidelines_for_quality=behavior_params["guidelines_for_quality"],
        norms_for_assumptions=behavior_params["norms_for_assumptions"]
    )
    task_examples_from_prompt = prompt42_template["task_examples"]
    task_examples = [
        TaskExample(example_task=f"{k}: {v}")
        for task in task_examples_from_prompt for k, v in task.items()
    ]
    if examples:
        task_examples.extend([
            TaskExample(example_task=f"{k}: {v}")
            for task in examples for k, v in task.items()
        ])
    prompt = Prompt42(
        problem_definition=problem_definition,
        requirements_for_inputs=requirements_for_inputs,
        output_specifications=output_spec,
        manage_constraints=manage_constraints,
        parameterize_behavior=parameterize_behavior,
        task_examples=task_examples
    )
    return prompt.create_prompt()


def get_output_spec(customer_id: str):
    schema_file_name = f"{customer_id}.creatives.output.schema.json"
    return OutputSpecification(
        expected_format="JSON",
        schema=schema_utils.get_schema_file(f"creatives/{schema_file_name}"),
        examples=[]
    )
