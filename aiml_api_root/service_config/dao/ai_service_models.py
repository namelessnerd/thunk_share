from pydantic import BaseModel, Field
from typing import Optional

class AIServiceConfig(BaseModel):
    provider: str = Field(..., description="The AI service provider, e.g., 'openAI', 'anthropic', 'replicate'")
    model: str = Field(..., description="The model name or ID used by the AI service")
    temperature: Optional[float] = Field(None, description="The temperature parameter for controlling the creativity of the model")
    api_key: str = Field(..., description="The API key for authenticating with the AI service")
