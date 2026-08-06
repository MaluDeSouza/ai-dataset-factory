from typing import List, Any
from uuid import UUID
from fastapi import APIRouter, Depends, UploadFile, File, Form, HTTPException
from sqlalchemy.orm import Session

from api.schemas.dataset import DatasetResponse, DatasetStatusResponse
from api.deps import (
    get_import_dataset_use_case,
    get_dataset_status_use_case,
    get_process_document_use_case,
    get_db
)
from application.use_cases.import_dataset_use_case import ImportDatasetUseCase
from application.use_cases.get_dataset_status_use_case import GetDatasetStatusUseCase
from application.use_cases.process_document_use_case import ProcessDocumentUseCase
from infrastructure.database.models import DocumentModel

# --- A Magia para enganar o Swagger ---
class SwaggerUploadFile(UploadFile):
    @classmethod
    def __get_pydantic_json_schema__(cls, core_schema: Any, handler: Any) -> dict[str, Any]:
        return {"type": "string", "format": "binary"}


router = APIRouter(prefix="/datasets", tags=["Datasets"])

@router.post("/", response_model=DatasetResponse, status_code=201)
async def upload_dataset(
    name: str = Form(...),
    files: List[SwaggerUploadFile] = File(...),
    use_case: ImportDatasetUseCase = Depends(get_import_dataset_use_case)
):
    """
    Recebe um lote de arquivos, extrai os bytes e despacha para a camada de domínio.
    """
    try:
        file_tuples = []
        for file in files:
            content = await file.read()
            file_tuples.append((file.filename or "unknown_file", content))
            
        dataset = use_case.execute(dataset_name=name, files=file_tuples)
        return dataset
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{dataset_id}/status", response_model=DatasetStatusResponse)
def get_dataset_status(
    dataset_id: UUID,
    use_case: GetDatasetStatusUseCase = Depends(get_dataset_status_use_case)
):
    """
    Devolve as métricas em tempo real do processamento do dataset.
    """
    try:
        metrics = use_case.execute(dataset_id=dataset_id)
        return metrics
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.post("/{dataset_id}/process", status_code=200)
def process_dataset(
    dataset_id: UUID,
    use_case: ProcessDocumentUseCase = Depends(get_process_document_use_case),
    db: Session = Depends(get_db)
):
    """
    Busca os documentos do dataset e dispara o motor inteligente.
    Execução síncrona, conectada na infra real.
    """
    documents = db.query(DocumentModel).filter(
        DocumentModel.dataset_id == dataset_id,
        DocumentModel.status.in_(["uploaded", "pending"])
    ).all()
    
    if not documents:
        raise HTTPException(status_code=404, detail="Nenhum documento pendente encontrado para processar neste dataset.")
        
    processed_count = 0
    for doc in documents:
        try:
            # O doc.original_content guarda o caminho físico que salvamos no upload
            use_case.execute(dataset_id=dataset_id, filepath=doc.original_content)
            
            doc.status = "processed"
            processed_count += 1
        except Exception as e:
            doc.status = "failed"
            print(f"Erro ao processar documento {doc.id}: {e}")
            
        db.commit()
        
    return {
        "message": "Processamento finalizado.",
        "processed_documents": processed_count,
        "failed_documents": len(documents) - processed_count
    }