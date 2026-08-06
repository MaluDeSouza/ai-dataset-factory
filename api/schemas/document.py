from pydantic import BaseModel, ConfigDict
from uuid import UUID
from typing import Optional

class DocumentResponse(BaseModel):
    """
    Schema de saída para detalhamento do documento na camada HTTP.
    Oculta campos pesados como original_content e foca em metadados e status.
    """
    id: UUID
    dataset_id: UUID
    filename: str
    category: Optional[str] = None
    status: str

    model_config = ConfigDict(from_attributes=True)