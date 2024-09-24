import pytest
from unittest.mock import AsyncMock, patch, MagicMock
from aiml.clients import openai_client
from aiml.schemas.dao.creatives import AdCreatives
from openai.types.chat.parsed_chat_completion import ParsedChatCompletion, ParsedChoice
from pydantic import BaseModel


class TestModel(BaseModel):
    message: str


@pytest.fixture
def oai_client():
    # Create an instance of OpenAIClient with dummy values for api_key, model, and temperature
    return openai_client.OpenAIClient(api_key="dummy-api-key",
                    model="gpt-3.5-turbo", temperature=0.7, max_tokens=100)


def test_safe_get_parsed_no_choices(oai_client):
    """
    Test __safe_get_parsed when the completion has no choices.
    """


    # Mock a valid ParsedChatCompletion with all required fields
    mock_completion = ParsedChatCompletion(
        id="cc-123",
        created=1633092540,
        model="gpt-4o",
        object="chat.completion",
        choices=[]
    )
    
    result = oai_client._OpenAIClient__safe_get_parsed(mock_completion)
    assert result is None


def test_safe_get_parsed_no_message(oai_client):
    """
    Test __safe_get_parsed when the first choice has no message.
    """
    # Mock a valid ParsedChoice
    mock_choice = ParsedChoice(
        finish_reason="stop",
        index=0,
        message={"role": "assistant"}
    )

    # Mock a valid ParsedChatCompletion with all required fields
    mock_completion = ParsedChatCompletion(
        id="cc-123",
        created=1633092540,
        model="gpt-4o",
        object="chat.completion",
        choices=[mock_choice]
    )
    result = oai_client._OpenAIClient__safe_get_parsed(mock_completion)
    assert result is None


def test_safe_get_parsed_valid_choice(oai_client):
    """
    Test __safe_get_parsed with a valid message and choice.
    """
    # Mock a valid ParsedChoice
    mock_choice = ParsedChoice(
        finish_reason="stop",
        index=0,
        message={"role": "assistant", "content": "test response",
                 "parsed": "test response"}
    )

    # Mock a valid ParsedChatCompletion with all required fields
    mock_completion = ParsedChatCompletion(
        id="cc-123",
        created=1633092540,
        model="gpt-4o",
        object="chat.completion",
        choices=[mock_choice]
    )
    result = oai_client._OpenAIClient__safe_get_parsed(mock_completion)
    assert result is not None
    assert result == "test response"


@pytest.mark.asyncio
@patch("aiml.clients.openai_client.OpenAI") 
async def test_invoke_success(mock_openai):
    """
    Test the invoke method when OpenAI returns a valid completion.
    """
    oai_client = openai_client.OpenAIClient(api_key="dummy-key",
                                model="gpt-3.5",temperature=0.7)

    mock_parse = MagicMock()
    # Mock a valid ParsedChoice
        # Mock a valid ParsedChoice with an AdCreatives object
    mock_ad_creative = AdCreatives(
        creatives=[{
            "target_demo": ["test demo"],
            "headline": "Test Headline",
            "primary_text": "Test Primary Text",
            "description": "Test Description",
            "call_to_action": "Test Call to Action",
            "prompt_for_ad_image": "Test Prompt for Ad Image"
        }]
    )
    mock_choice = ParsedChoice(
        finish_reason="stop",
        index=0,
        message={"role": "assistant", "content": "test response",
                 "parsed": mock_ad_creative}
    )

    # Mock a valid ParsedChatCompletion with all required fields
    mock_completion_retval = ParsedChatCompletion(
        id="cc-123",
        created=1633092540,
        model="gpt-4o",
        object="chat.completion",
        choices=[mock_choice]
    )

    mock_parse.return_value = mock_completion_retval
    mock_openai.return_value.beta.chat.completions.parse = mock_parse

    prompt = {"system": "Generate ad creatives", "user": "Create an ad"}
    result = await oai_client.invoke(TestModel, prompt)
    
    assert result is not None
    assert result == mock_ad_creative


@pytest.mark.asyncio
@patch("openai.OpenAI")
async def test_invoke_no_completion(mock_openai, oai_client):
    """
    Test the invoke method when OpenAI returns no completion.
    """
    # Mock the OpenAI client's completion call
    mock_completion = AsyncMock(return_value=None)
    mock_openai.beta.chat.completions.parse = mock_completion

    prompt = {"system": "Generate ad creatives", "user": "Create an ad"}
    result = await oai_client.invoke(TestModel, prompt)
    
    assert result is None


@pytest.mark.asyncio
@patch("openai.OpenAI")
async def test_invoke_error_handling(mock_openai, oai_client):
    """
    Test the invoke method when an exception occurs.
    """
    # Mock the OpenAI client's completion call to raise an exception
    mock_openai.beta.chat.completions.parse.side_effect = Exception("API Error")

    prompt = {"system": "Generate ad creatives", "user": "Create an ad"}
    
    result = await oai_client.invoke(TestModel, prompt)
    
    assert result is None  # Expect None when an exception occurs
