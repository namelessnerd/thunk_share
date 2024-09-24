import json
from typing import Optional, List, Union, Dict

import requests
from requests import HTTPError

from cache.redis_client import RedisClient, RedisConfig
from data.utils import parser_utils
from clients.api_clients.dao.ctgov_data_models import ClinicalTrialData
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type, RetryError
import logging

from enum import Enum

from data.utils.helpers import safe_getattr


class ResponseFormat(Enum):
    JSON = "json"
    CSV = "csv"
    FHIR = "fhir.json"
    JSON_ZIP = "json.zip"


class CTGovClientException(Exception):
    def __init__(self, message: str):
        self.message = message
        super().__init__(self.message)


class CTGovTrialClient:
    api_end_point = "https://clinicaltrials.gov/api/v2/"

    def __init__(self, response_format: ResponseFormat = ResponseFormat.JSON):
        self.response_format = response_format

    @staticmethod
    def is_404_exception(exception: requests.exceptions.RequestException):
        if isinstance(exception, requests.exceptions.H) and exception.status_code == 404:
            return False
        return True

    @retry(
        stop=stop_after_attempt(5),
        wait=wait_exponential(multiplier=1, min=4, max=60),
        retry=retry_if_exception_type()
    )
    def _get_with_retry(self, url: str, params: dict) -> requests.Response:
        response = requests.get(url, params=params)
        response.raise_for_status()
        return response

    """
    Gets details for the trial with the NCT id. 
    """

    def get_trial_with_nct_id(self, nct_id: str,
                              fields: Optional[List[str]] = None) -> Union[
            any, CTGovClientException]:
        query_params = {"format": self.response_format.value}

        if fields:
            query_params["fields"] = "|".join(fields)
        end_point = CTGovTrialClient.api_end_point + "/studies/" + nct_id
        try:
            res = self._get_with_retry(end_point, params=query_params)
            return res.json()
        except RetryError as e:
            last_exception = e.last_attempt.exception()
            return CTGovClientException("Retry exception from tenacity " +
                                        str(last_exception))
        except HTTPError as e:
            if e.response.status_code == 404:
                return CTGovClientException("No result found for the provided NCT ID")
        except Exception as e:
            raise CTGovClientException(f"An unexpected error occurred: {str(e)}") from e


def get_trials(nct_id: str) -> Optional[ClinicalTrialData]:
    redis_client = RedisClient(RedisConfig())
    with redis_client.get_connection() as redis_conn:
        logging.info(f"NCT ID {nct_id}")
        trial_data_from_cache = redis_conn.get(nct_id)
        try:
            trial_data = json.loads(trial_data_from_cache)
            logging.info(f"Trial id {nct_id} found in cache.")
        except TypeError as e:
            logging.info(f"Trial id {nct_id} not found in cache. fetching from api")
            trial_data = CTGovTrialClient().get_trial_with_nct_id(nct_id=nct_id)
            redis_conn.set(nct_id, json.dumps(trial_data))
        except (redis.ConnectionError, redis.TimeoutError) as e:
            logging.error(f"Redis error: {e}")
    if trial_data:
        return parser_utils.from_dict(ClinicalTrialData, trial_data)
    return None


def get_desc_eligibility(nct_id: str) -> Dict[str, str]:
    logging.info(f"NCT ID {nct_id}")
    parsed_trial = get_trials(nct_id)
    protocol_section = parsed_trial.protocol_section
    brief_summary = safe_getattr(protocol_section, ["description_module", "brief_summary"])
    eligibility = safe_getattr(protocol_section, ["eligibility_module"])
    if not (brief_summary and eligibility):
        raise CTGovClientException(f"Either one of Brief summary and"
                                   f" eligibility or both are missing"
                                   f" for : {nct_id}")
    return {"brief_summary" : brief_summary, "eligibility": eligibility}
