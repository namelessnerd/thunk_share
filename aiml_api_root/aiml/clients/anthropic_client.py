import anthropic
from .client_registry import register_client
from .ai_client import AIClient
from typing import Dict, Optional, List, Type, TypeVar
from aiml.schemas.dao.creatives import AdCreative, AdCreatives
from pydantic import BaseModel, ValidationError
from aiml.schemas.schema_utils import get_json_schema_file
import traceback
import logging
import json

T = TypeVar('T', bound=BaseModel)

@register_client("anthropic")
class AnthropicClient(AIClient):
    def __init__(self, api_key, model, temperature, max_tokens = None):
        super().__init__(model, max_tokens, temperature)
        self.api_key = "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"
        self.client = anthropic.AsyncAnthropic(api_key=api_key)

    def customize_prompt(self, prompt42):
        """
        This method customizes a prompt42 to match the optimial promopting
        for the AI
        """
    pass        

    async def invoke(self, response_format: Type[T],
               prompt: dict[str, str], retry=False) -> Optional[T]:
        try:
            # Define the tool for Claude
            resp_tool_defn = response_format.get_schema()
            response = await self.client.messages.create(
                model=self.model,
                max_tokens=1000,
                temperature=self.temperature,
                tools=[resp_tool_defn],
                system=prompt["system"],
                messages=[
                    {"role": "user", "content": prompt["user"]}
                ]
            )
            if response:
                tool_use_block = None
                for content in response.content:
                    if isinstance(content, anthropic.types.tool_use_block.ToolUseBlock):
                        tool_use_block = content
                        break
                if tool_use_block and tool_use_block.input:
                    return response_format.process(tool_use_block.input)
            logging.error("No valid response content from the API.")
            return None
        except Exception as e:
            traceback.print_exc()
            logging.error(e)
            logging.error(f"Error getting Anthropic to generate creatives")