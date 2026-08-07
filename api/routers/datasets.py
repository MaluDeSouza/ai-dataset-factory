import os
from typing import List, Any
from uuid import UUID
from fastapi import APIRouter, Depends, UploadFile, File, Form, HTTPException, BackgroundTasks
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session

from api.schemas.dataset import DatasetResponse, DatasetStatusResponse
from api.deps import (
    get_import_dataset_use_case,
    get_dataset_status_use_case,
    get_process_dataset_async_use_case,
    get_export_dataset_use_case,
    get_db
)
from application.use_cases.import_dataset_use_case import ImportDatasetUseCase
from application.use_cases.get_dataset_status_use_case import GetDatasetStatusUseCase
from application.use_cases.process_dataset_async_use_case import ProcessDatasetAsyncUseCase
from application.use_cases.export_dataset_use_case import ExportDatasetUseCase
from infrastructure.database.models import ExportArtifactModel



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
    Recebe um lote de arquivos, extrai os bytes e despacha para o armazenamento local.
    """
    try:
        file_tuples = []
        for file in files:
            content = await file.read()
            file_tuples.append((file.filename or "unknown_file", content))
        
        
        dataset = use_case.execute(dataset_name=name, files=file_tuples)
        return dataset
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Falha ao realizar upload do lote: {str(e)}")


@router.get("/{dataset_id}/status", response_model=DatasetStatusResponse)
def get_dataset_status(
    dataset_id: UUID,
    use_case: GetDatasetStatusUseCase = Depends(get_dataset_status_use_case)
):
    """
    Devolve as métricas de saúde e progresso do dataset em tempo real.
    """
    try:
        metrics = use_case.execute(dataset_id=dataset_id)
        return metrics
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao buscar status: {str(e)}")


@router.post("/{dataset_id}/process", status_code=202)
def process_dataset(
    dataset_id: UUID,
    background_tasks: BackgroundTasks,
    use_case: ProcessDatasetAsyncUseCase = Depends(get_process_dataset_async_use_case)
):
    """
    Dispara o motor de processamento inteligente do dataset em background.
    Retorna imediatamente HTTP 202 Accepted para evitar timeouts na requisição síncrona.
    """
    try:
        
        background_tasks.add_task(use_case.execute, dataset_id=dataset_id)
        
        return {
            "message": "Processamento do dataset iniciado com sucesso em segundo plano.",
            "dataset_id": dataset_id
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao registrar tarefa em segundo plano: {str(e)}")


@router.post("/{dataset_id}/export", status_code=201)
def export_dataset(
    dataset_id: UUID,
    format_type: str = "jsonl",
    export_style: str = "text",
    use_case: ExportDatasetUseCase = Depends(get_export_dataset_use_case)
):
    """
    Gera o ativo final de exportação (JSONL, JSON, CSV) apenas com dados que passaram
    no pipeline de validação de qualidade e auditoria.
    """
    try:
        artifact = use_case.execute(
            dataset_id=dataset_id,
            format_type=format_type,
            export_style=export_style
        )
        return {
            "artifact_id": artifact.id,
            "dataset_id": artifact.dataset_id,
            "filename": artifact.filename,
            "format": artifact.format,
            "created_at": artifact.created_at
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro interno ao exportar dataset: {str(e)}")


@router.get("/export/{artifact_id}/download", response_class=FileResponse)
def download_export_file(
    artifact_id: UUID,
    db: Session = Depends(get_db)
):
    """
    Realiza o download físico do arquivo de exportação gerado no servidor.
    """
    artifact = db.query(ExportArtifactModel).filter(ExportArtifactModel.id == artifact_id).first()
    if not artifact:
        raise HTTPException(status_code=404, detail="Artefato de exportação não encontrado.")

    if not os.path.exists(artifact.file_path):
        raise HTTPException(
            status_code=404, 
            detail="Arquivo físico de exportação não encontrado no disco local do servidor."
        )

    
    return FileResponse(
        path=artifact.file_path,
        filename=artifact.filename,
        media_type="application/octet-stream"
    )

@router.delete("/reset-db", status_code=200)
def reset_database(db: Session = Depends(get_db)):
    """
    Rota utilitária para limpar todo o banco de dados durante os testes locais.
    """
    from infrastructure.database.models import DatasetModel
    
    try:
        datasets = db.query(DatasetModel).all()
        for ds in datasets:
            db.delete(ds)
            
        db.commit()
        return {"message": f"Banco limpo com sucesso! {len(datasets)} datasets e seus arquivos foram apagados."}
    except Exception as e:
        db.rollback()
        return {"error": f"Erro ao limpar banco: {str(e)}"}