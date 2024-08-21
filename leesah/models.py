"""Models for the game."""

import uuid

from datetime import datetime
from pydantic import BaseModel

TYPE_QUESTION = "SPØRSMÅL"
TYPE_ANSWER = "SVAR"

"""Categories"""
ARITHMETIC = "aritmetikk"
BANK_ACCOUNT = "bankkonto"
BASE64 = "base64"
DEDUPLICATION = "deduplication"
GRUNNBELØP = "grunnbeløp"
MIN_MAX = "min-max"
NAV = "NAV"
PING_PONG = "ping-pong"
PRIME = "primtall"
TEAM_REGISTRATION = "team-registration"

"""NAIS categories"""
INGRESS = "ingress"
LOGG = "logg"
SERVICE_DISCOVERY = "service-discovery"


class Answer(BaseModel):
    """An answer to a question."""

    spørsmålId: str
    kategorinavn: str
    lagnavn: str = ""
    svar: str = ""
    svarId: str = str(uuid.uuid4())


class Question(BaseModel):
    """A question."""

    kategorinavn: str
    spørsmål: str
    svarformat: str
