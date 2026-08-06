from uuid import UUID
from sqlalchemy.orm import Session
from sqlalchemy import func
from infrastructure.database.models import DatasetModel, DocumentModel

class GetDatasetStatusUseCase:
    def __init__(self, db_session: Session):
        self.db_session = db_session

    def execute(self, dataset_id: UUID) -> dict:
        """
        Calcula as métricas de progresso de um dataset agregando os status
        diretamente via query SQL para otimização de memória.
        """
        # 1. Verifica se o dataset existe e pega o nome
        dataset = self.db_session.query(DatasetModel).filter(DatasetModel.id == dataset_id).first()
        if not dataset:
            raise ValueError(f"Dataset {dataset_id} não encontrado.")

        # 2. Executa a contagem agrupada por status no banco de dados
        status_counts = (
            self.db_session.query(DocumentModel.status, func.count(DocumentModel.id))
            .filter(DocumentModel.dataset_id == dataset_id)
            .group_by(DocumentModel.status)
            .all()
        )

        # 3. Consolida as métricas
        metrics = {
            "dataset_id": dataset.id,
            "name": dataset.name,
            "total_documents": 0,
            "pending_documents": 0,
            "processed_documents": 0,
            "failed_documents": 0
        }

        for status, count in status_counts:
            metrics["total_documents"] += count
            
            
            if status in ["uploaded", "pending"]:
                metrics["pending_documents"] += count
            elif status == "processed":
                metrics["processed_documents"] += count
            elif status == "failed":
                metrics["failed_documents"] += count

        return metrics