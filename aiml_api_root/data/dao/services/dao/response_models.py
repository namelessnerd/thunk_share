from typing import Optional

from pydantic import BaseModel

from aiml.schemas.dao.prescreener import Prescreener
from aiml.schemas.dao.study_website import StudyWebsite


class TrialInfo(BaseModel):
    description: str
    eligibility: str


# Define the wrapper class to contain the "data" key
class PrescreenerResponse(BaseModel):
    data: Prescreener

    @classmethod
    def from_existing_data(cls, questions: Prescreener = None,
                           err: Prescreener = None):
        if questions:
            return cls(data=questions)
        else:
            return cls(data=err)


class StudyWebsiteResponse(BaseModel):
    status: bool = True
    session_id: Optional[str] = None
    study_website_content: Optional[StudyWebsite] = None
    exception: Optional[str] = None
