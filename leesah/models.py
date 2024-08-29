"""Models for the game."""

import uuid

from datetime import datetime
from pydantic import BaseModel

TYPE_QUESTION = "SPØRSMÅL"
TYPE_ANSWER = "SVAR"


class Answer(BaseModel):
    """An answer to a question."""

    spørsmålId: str
    kategorinavn: str
    lagnavn: str = ""
    svar: str = ""
    svarId: str = str(uuid.uuid4())


class Question(BaseModel):
    """A question."""

    id: str
    kategorinavn: str
    spørsmål: str
    svarformat: str
