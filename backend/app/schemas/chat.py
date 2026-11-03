from typing import Literal
from pydantic import BaseModel, Field

Jurisdiction = Literal["US", "IN"]

LegalCategory = Literal[
    "immigration",
    "criminal",
    "civil",
    "family",
    "employment",
    "property",
    "business",
    "contracts",
    "other",
]


class ChatRequest(BaseModel):
    question: str = Field(min_length=5, max_length=5000)
    document_id: str | None = None
    jurisdiction: Jurisdiction
    category: LegalCategory
    state: str | None = Field(default=None, max_length=100)


class ChatResponse(BaseModel):
    answer: str
    jurisdiction: Jurisdiction
    category: LegalCategory
    state: str | None = None
    sources: list[str] = Field(default_factory=list)
    disclaimer: str
    status: str
document_id: str | None = None