"""Modeller for spillet."""

import uuid

from datetime import datetime
from pydantic import BaseModel

TYPE_SPØRSMÅL = "SPØRSMÅL"
TYPE_SVAR = "SVAR"


class Svar(BaseModel):
    """Et svar til et spørsmål."""

    spørsmålId: str
    kategorinavn: str
    lagnavn: str = ""
    svar: str = ""
    svarId: str = str(uuid.uuid4())


class Spørsmål(BaseModel):
    """Et spørsmål som venter på et svar."""

    id: str
    kategorinavn: str
    spørsmål: str
    svarformat: str
