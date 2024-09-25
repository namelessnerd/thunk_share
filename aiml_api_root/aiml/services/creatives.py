import json
import logging
import os
import traceback
from typing import List, Dict, Union, TypeVar, Optional, AsyncGenerator

from openai import OpenAI

import anthropic
from pydantic import BaseModel, ValidationError

from aiml.prompts.creatives.prompt_generator import generate_creatives_prompt
from aiml.prompts.dao.prompt42_prompt import Prompt42
from aiml.schemas import schema_utils
from aiml.schemas.dao.creatives import AdCreatives, AdCreative
from aiml.clients.client_registry import get_client
from clients.api_clients import ctgov_trials
from clients.api_clients.ctgov_trials import CTGovClientException
from utils.measurements import measure_execution_time
from service_config.service_registry import ServiceRegistry, AIServiceConfigException
from aiml.clients.openai_client import OpenAIClient
from aiml.clients.ai_client import AIClient
from aiml.clients.anthropic_client import AnthropicClient
from aiml.schemas.dao.creatives import AdCreatives
import asyncio




@measure_execution_time
async def get_creatives(prompt: Dict[str, str], ai_client: AIClient) -> AdCreatives:
    openai_client = ai_client.client
    return await ai_client.invoke(response_format=AdCreatives,
                            prompt=prompt)

@measure_execution_time
async def get_creatives_anthropic(prompt):
    ai_client =  get_client("anthropic", get_ai_models().get("anthropic"))
    return await ai_client.invoke(response_format=AdCreatives,
                            prompt=prompt)


async def generate(customer_id:str = "acmeinc",
            nct_id:str = None) -> AsyncGenerator[AdCreatives, None]:
    try:
        ct_res = ctgov_trials.get_desc_eligibility(nct_id)
        prompt = generate_creatives_prompt(customer_id=customer_id,
                              description=ct_res["brief_summary"],
                              eligibility=ct_res["eligibility"])

        ai_configs = ServiceRegistry(None).get_ai_service_configs(
                                                    customer=customer_id,
                                                    service="creatives"
                                                    )           
        ai_tasks = []
        for service_key in ai_configs:
            if isinstance(ai_configs[service_key], str):
                logging.error(ai_configs[service_key])
                continue
            ai_client = get_client(service_key, ai_configs[service_key])
            if ai_client:
                ai_tasks.append(get_creatives(prompt, ai_client))

        for current_task in asyncio.as_completed(ai_tasks):
            result = await current_task
            yield result

    except CTGovClientException:
        logging.error(f"Error getting trial for {nct_id} from CTGov")
    except AIServiceConfigException as e:
        logging.error(e)
    except Exception as e:
        traceback.print_exc()
        logging.error(e)
        logging.error(f"Exception occured during processing - {str(e)}")

@measure_execution_time
async def main():
    # Call the generate function with example parameters
    customer_id = "trialx"
    nct_id = "nct06585670"

    async for ad_creative in generate(customer_id=customer_id, nct_id=nct_id):
        print(ad_creative)

if __name__ == "__main__":
    # Run the main function
    asyncio.run(main())
