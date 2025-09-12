from typing import Optional
from pydantic import BaseModel, Field

class VectorQueryInput(BaseModel):
    query: str = Field(..., description="The semantic search term to use for vector lookup.")
    top_k: Optional[int] = Field(5, description="The number of top results to retrieve from the vector database.")