from pydantic import BaseModel, Field, ConfigDict
from typing import List, Optional
from datetime import datetime, timezone
from uuid import UUID, uuid4

class Chunk(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID = Field(default_factory=uuid4)
    document_id: UUID
    content: str
    token_count: int = 0
    embedding: Optional[list[float]] = None

class Document(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID = Field(default_factory=uuid4)
    dataset_id: UUID
    filename: str
    original_content: Optional[str] = None
    cleaned_content: Optional[str] = None
    category: Optional[str] = None
    status: str = "pending"
    chunks: List[Chunk] = Field(default_factory=list)

class Dataset(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID = Field(default_factory=uuid4)
    name: str
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    documents: List[Document] = Field(default_factory=list)