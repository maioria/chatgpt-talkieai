from enum import Enum
from typing import List, Dict

from pydantic import BaseModel, constr

class UpdateLanguageDTO(BaseModel):
    language: constr(min_length=1)


class FeedbackDTO(BaseModel):
    content: constr(min_length=1)
    contact: str = None