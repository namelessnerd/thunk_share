from typing import Optional, List

from pydantic import BaseModel
from aiml.schemas.schema_utils import get_json_schema_file
from typing import Dict, Optional, List

class AdCreative(BaseModel):
    target_demo: List[str]
    headline: str
    primary_text: str
    description: str
    call_to_action: str
    prompt_for_ad_image: str


class AdCreatives(BaseModel):
    source: Optional[str] = None
    creatives: list[AdCreative]

    @classmethod
    def get_schema(cls) -> Optional[Dict]:
        return get_json_schema_file("creatives/acmeinc.creatives.output.schema.json")

    @classmethod
    def process(cls, creatives: Dict[str, List[Dict[str, str]]]) -> Optional["AdCreatives"]:
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
                    ad_creatives.append(ant_creative)
                except ValidationError:
                    logging.error(f"Ignoring {creative} due to validation error")
            return AdCreatives(source = "anthropic", creatives=ad_creatives)

