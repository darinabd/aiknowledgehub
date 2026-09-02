from typing import List

from pydantic import BaseModel, Field


class AskQuestionRequest(BaseModel):
    question: str = Field(
        ...,
        min_length=2,
        max_length=1000,
    )


class SourceChunk(BaseModel):
    chunk_index: int
    content: str
    score: float


class AskQuestionResponse(BaseModel):
    document_id: int
    question: str
    answer: str
    sources: List[SourceChunk]