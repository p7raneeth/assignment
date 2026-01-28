from pydantic import BaseModel, Field
from typing import List, Optional


# ========== Schemas ==========
class QueryRequest(BaseModel):
    query: str = Field(..., min_length=1, max_length=5000, description="User's question")
    conversation_history: Optional[List[dict]] = Field(default=[], description="Previous messages")
    top_k: Optional[int] = Field(default=3, ge=1, le=10, description="Number of chunks to retrieve")


class Source(BaseModel):
    content: str
    score: float
    chunk_id: str
    page_number: Optional[int] = None


class QueryResponse(BaseModel):
    answer: str
    sources: List[Source] = []
    query: str