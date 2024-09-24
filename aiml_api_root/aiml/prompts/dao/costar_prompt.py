from typing import List, Optional
from pydantic import BaseModel, Field


class Context(BaseModel):
    trial_description: str = Field(..., description="Description of the clinical trial.")
    eligibility_criteria: str = Field(..., description="Eligibility criteria for the clinical trial.")
    guidelines: str = Field(..., description="Guidelines the AI must adhere to when generating the prescreener.")
    constraints: str = Field(..., description="Constraints that the AI must follow in generating the prescreener.")


class Requirement(BaseModel):
    step: str = Field(..., description="Step number in the sequence.")
    action: str = Field(..., description="Action that the AI should take.")
    input: Optional[str] = Field(None, description="Input data or source that the AI should use.")
    requirements: Optional[List[str]] = Field(None, description="Specific requirements the AI must meet.")


class TaskExample(BaseModel):
    example: str = Field(..., description="An example of how to apply the task.")


class Results(BaseModel):
    expected_output: str = Field(..., description="Description of the expected output.")


class CoSTARPrompt(BaseModel):
    context: Context
    objective: Requirement
    steps: List[Requirement]
    task_examples: List[TaskExample]
    results: Results
