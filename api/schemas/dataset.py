from pydantic import BaseModel, ConfigDict
from uuid import UUID
from datetime import datetime

class DatasetResponse(BaseModel):
    """
    Representação pública de um Dataset (usado no retorno de criação/listagem).
    Oculta a lista de documentos para manter o payload leve.
    """
    id: UUID
    name: str
    created_at: datetime
    
    model_config = ConfigDict(from_attributes=True)


class DatasetStatusResponse(BaseModel):
    """
    Estrutura consolidada que representa a saúde do processamento do dataset.
    """
    dataset_id: UUID
    name: str
    total_documents: int
    pending_documents: int
    processed_documents: int
    failed_documents: int