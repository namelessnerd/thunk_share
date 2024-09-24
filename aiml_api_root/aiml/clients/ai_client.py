from abc import ABC, abstractmethod

from typing import Type, TypeVar, Optional
from pydantic import BaseModel


# Define a generic type for Pydantic models
# these are used for structured output.
T = TypeVar('T', bound=BaseModel)

class AIClient(ABC):
    def __init__(self, model, max_tokens, temperature):
        self.model = model
        self.max_tokens = max_tokens
        self.temperature = temperature

    @abstractmethod
    def customize_prompt(self, prompt42):
        """
        This method customizes a prompt42 to match the optimial promopting
        for the AI
        """
        pass

    @abstractmethod
    async def invoke(self, response_format: Type[T], prompt: str, retry=False) -> T:
        """
        Method to invoke the AI with a given prompt. Retry is default 
        set to false. 
        """
        pass
