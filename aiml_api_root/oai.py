import json
import logging
import os
from typing import List, Dict, Union, TypeVar, Optional

from openai import OpenAI
from openai.types.chat.parsed_chat_completion import ParsedChatCompletion, ParsedChoice
import anthropic
from pydantic import BaseModel, ValidationError

from aiml.prompts.creatives.prompt_generator import generate_creatives_prompt
from aiml.prompts.dao.prompt42_prompt import Prompt42
from aiml.schemas import schema_utils
from aiml.schemas.dao.creatives import AdCreatives, AdCreative
from utils.measurements import measure_execution_time

openai_client = OpenAI(
    api_key=os.getenv("OPENAI_AUTH_TOKEN")
)

T = TypeVar('T')

def safe_get_parsed(completion: ParsedChatCompletion[T]) -> Optional[T]:
    try:
        if not completion.choices:
            logging.warning("No choices in completion")
            return None

        first_choice: ParsedChoice[T] = completion.choices[0]
        if not first_choice.message:
            logging.warning("No message in first choice")
            return None
        return first_choice.message.parsed
    except AttributeError as e:
        logging.error(f"Unexpected structure in completion: {e}")
        return None


@measure_execution_time
def get_creatives_openai(prompt: Dict[str, str]) -> AdCreatives:
    completion = openai_client.beta.chat.completions.parse(
        model="gpt-4o-2024-08-06",
        messages=[
            {"role": "system", "content": prompt["system"]},
            {"role": "user", "content": prompt["user"]},
        ],
        response_format=AdCreatives,
        temperature=0.7
    )
    if completion:
        oai_creatives = safe_get_parsed(completion)
        for creative in oai_creatives.creatives:
            creative.source = "openAI"
        return oai_creatives




anthropic_client = anthropic.Anthropic(
    # defaults to os.environ.get("ANTHROPIC_API_KEY")
)


def create_ad_creatives(creatives: Dict[str, List[Dict[str, str]]]) -> Optional[AdCreatives]:
    """
    Create ad creatives for a clinical trial.

    :param creatives: A list of dictionaries, each representing an ad creative with the following keys:
        - target_demo: List[str]
        - headline: str
        - primary_text: str
        - description: str
        - call_to_action: str
    :return: A confirmation message
    """
    # Here you would typically process or store the creatives
    # For this example, we'll just return a confirmation
    creatives_from_ai = creatives.get("creatives", None)
    if creatives_from_ai:
        ad_creatives: List[AdCreative] = []
        for creative in creatives_from_ai:
            try:
                ant_creative = AdCreative(**creative)
                ant_creative.source = "anthropic"
                ad_creatives.append(ant_creative)
            except ValidationError:
                logging.error(f"Ignoring {creative} due to validation error")
        print(ad_creatives)
        return AdCreatives(creatives=ad_creatives)



# Define the tool for Claude
ad_creative_tool = {
    "name": "create_ad_creatives",
    "description": "Create ad creatives for a clinical trial",
    "input_schema": {
        "type": "object",
        "properties": {
            "creatives": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "target_demo": {
                            "type": "array",
                            "items": {"type": "string"}
                        },
                        "headline": {"type": "string"},
                        "primary_text": {"type": "string"},
                        "description": {"type": "string"},
                        "call_to_action": {"type": "string"}
                    },
                    "required": ["target_demo", "headline", "primary_text", "description", "call_to_action"]
                }
            }
        },
        "required": ["creatives"]
    }
}

@measure_execution_time
def get_creatives_anthropic(prompt: Dict[str, str]) -> Optional[AdCreatives]:
    response = anthropic_client.messages.create(
        model="claude-3-5-sonnet-20240620",
        max_tokens=1000,
        temperature=0.7,
        tools=[ad_creative_tool],
        system=prompt["system"],
        messages=[
               {"role": "user", "content": prompt["user"]}
        ]
    )
    tool_use_block = None
    for content in response.content:
        if isinstance(content, anthropic.types.tool_use_block.ToolUseBlock):
            tool_use_block = content
            break
    if tool_use_block and tool_use_block.input:
        return create_ad_creatives(tool_use_block.input)


def get_creatives(description: str, eligibility: str):
    prompt = generate_creatives_prompt(customer_id="acmeinc",
                          description=description,
                          eligibility=eligibility)
    claude_creatives = get_creatives_anthropic(prompt)
    print(claude_creatives)
    oai_creatives = get_creatives_openai(prompt)
    print(oai_creatives)
    if oai_creatives and claude_creatives:
        oai_creatives.creatives.extend(claude_creatives.creatives)
        return oai_creatives
    elif oai_creatives:
        return oai_creatives
    elif claude_creatives:
        return claude_creatives
