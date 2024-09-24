from openai import OpenAI
from openai.types.chat.parsed_chat_completion import ParsedChatCompletion, ParsedChoice
from .client_registry import register_client
from .ai_client import AIClient
from aiml.schemas.dao.creatives import AdCreatives
import logging
import traceback
from typing import Type, TypeVar, Optional
from pydantic import BaseModel


# Define a generic type for Pydantic models
# these are used for structured output.
T = TypeVar('T', bound=BaseModel)

@register_client("openAI")
class OpenAIClient(AIClient):

    def __init__(self, api_key, model, temperature, max_tokens = None):
        super().__init__(model, max_tokens, temperature)
        self.api_key = api_key
        self.client = OpenAI(api_key=api_key)

    def customize_prompt(self, prompt42):
        """
        This method customizes a prompt42 to match the optimial promopting
        for the AI
        """
        pass

    
    def __safe_get_parsed(self, 
                          completion: ParsedChatCompletion[T]) -> Optional[T]:
        """
        Parses the response from openAI and sends the expected type back
        """
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

    async def invoke(self, response_format: Type[T],
               prompt: dict[str, str], retry=False) -> Optional[T]:
        try:
            completion = self.client.beta.chat.completions.parse(
                model=self.model,
                messages=[
                    {"role": "system", "content": prompt["system"]},
                    {"role": "user", "content": prompt["user"]},
                ],
                response_format=response_format,
                temperature=self.temperature
            )
            if completion:
                oai_response = self.__safe_get_parsed(completion)
                if oai_response:
                    oai_response.source = "openAI"
                    return oai_response
            logging.error("OpenAI call was successful but no results were obtained")                  
            return None
        except Exception as e:
            traceback.print_exc()
            logging.error(e)
            logging.error(f"Error getting Anthropic to generate creatives")
