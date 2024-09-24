import json
import logging
import traceback
from typing import Dict
from fastapi import APIRouter, Query
from aiml.schemas.dao.creatives import AdCreatives
from aiml.services import creatives
from data.utils.helpers import safe_getattr
from data.utils.logging.config import setup_logging
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from typing import AsyncGenerator
router = APIRouter()




@router.get("/generate/{customer_id}")
async def generate_creatives(customer_id: str,
                             nct_id: str = Query(...,
                                                 description="The NCT ID associated with the campaign")) -> StreamingResponse:
    """
    Generate ad creatives for a given customer and NCT ID.
    Starts a new AI session and streams the AdCreatives as soon as they are available.
    This solves the issue with waiting for all AI's to finish, causing timeouts.

    - **customer_id**: The ID of the customer
    - **nct_id**: The NCT ID for the prescreener
    """
    try:
        # generator to stream AdCreatives results
        async def result_generator() -> AsyncGenerator[str, None]:
            try:
                async for result in creatives.generate(customer_id=customer_id, nct_id=nct_id):
                    # Yield the AdCreatives object as JSON, one at a time
                    yield result.json() + "\n"  # Each AdCreative will be serialized to JSON
            except Exception as e:
                traceback.print_exc()
                logging.error(f"Error generating creatives: {str(e)}")
                yield f'{{"error": "{str(e)}"}}\n'

        # Stream the response with AdCreatives objects as JSON
        return StreamingResponse(result_generator(), media_type="application/json")

    except Exception as e:
        traceback.print_exc()
        logging.error(e)
        return {"error": "An error occurred while generating creatives"}
