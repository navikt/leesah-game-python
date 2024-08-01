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
    spørsmål: str = ""
    opprettet: str = datetime.now().isoformat()
    svarId: str = str(uuid.uuid4())
    type: str = TYPE_ANSWER


class Question(BaseModel):
    """A question."""

    kategorinavn: str
    spørsmål: str
