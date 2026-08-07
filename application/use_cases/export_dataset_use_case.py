import os
import logging
from uuid import UUID, uuid4
from datetime import datetime
from pathlib import Path
from sqlalchemy.orm import Session

from domain.entities import Chunk, Document, ExportArtifact
from application.pipelines.validation_pipeline import ValidationPipeline
from application.pipelines.export_pipeline import ExportPipeline
from infrastructure.storage.local_storage import LocalStorageProvider
from infrastructure.database.models import DatasetModel, DocumentModel, ChunkModel, ExportArtifactModel

logger = logging.getLogger(__name__)

class ExportDatasetUseCase:
    """
    Caso de Uso responsável por filtrar os dados válidos de um dataset,
    formatá-los conforme as especificações solicitadas e salvar o arquivo físico resultante.
    """
    def __init__(
        self,
        db_session: Session,
        storage_provider: LocalStorageProvider,
        validation_pipeline: ValidationPipeline,
        export_pipeline: ExportPipeline
    ):
        self.db_session = db_session
        self.storage_provider = storage_provider
        self.validation_pipeline = validation_pipeline
        self.export_pipeline = export_pipeline

    def execute(self, dataset_id: UUID, format_type: str = "jsonl", export_style: str = "text") -> ExportArtifact:
        """
        Executa a exportação do dataset.
        
        Args:
            dataset_id: ID do dataset a ser exportado.
            format_type: Formato do arquivo físico resultante ("jsonl", "json", "csv").
            export_style: Estilo do dataset para treinamento ("text", "instruction", "prompt_completion").
            
        Retorna:
            ExportArtifact: Entidade de domínio representando o ativo gerado.
        """
        logger.info(f"Iniciando exportação do dataset {dataset_id} no formato {format_type} (estilo: {export_style})")

        
        dataset = self.db_session.query(DatasetModel).filter(DatasetModel.id == dataset_id).first()
        if not dataset:
            raise ValueError(f"Dataset com ID {dataset_id} não encontrado.")

        
        db_documents = self.db_session.query(DocumentModel).filter(
            DocumentModel.dataset_id == dataset_id
        ).all()
        
        if not db_documents:
            raise ValueError(f"Não há documentos vinculados ao dataset {dataset_id} para exportar.")

        
        documents_map: dict[str, Document] = {}
        for doc in db_documents:
            documents_map[str(doc.id)] = Document(
                id=doc.id,
                dataset_id=doc.dataset_id,
                filename=doc.filename,
                original_content=doc.original_content,
                cleaned_content=doc.cleaned_content,
                category=doc.category,
                status=doc.status,
                created_at=doc.created_at,
                updated_at=doc.updated_at
            )

        
        doc_ids = [doc.id for doc in db_documents]
        db_chunks = self.db_session.query(ChunkModel).filter(
            ChunkModel.document_id.in_(doc_ids)
        ).all()

        if not db_chunks:
            raise ValueError(f"Não existem blocos fatiados (chunks) para os documentos do dataset {dataset_id}.")

        
        domain_chunks = [
            Chunk(
                id=c.id,
                document_id=c.document_id,
                content=c.content,
                token_count=c.token_count,
                embedding=c.embedding
            )
            for c in db_chunks
        ]

        
        valid_chunks, _ = self.validation_pipeline.process(dataset_id=dataset_id, chunks=domain_chunks)
        
        if not valid_chunks:
            raise ValueError("Nenhum trecho de texto deste dataset passou nos critérios de qualidade para exportação.")

        
        serialized_data = self.export_pipeline.serialize(
            chunks=valid_chunks,
            documents_map=documents_map,
            format_type=format_type,
            export_style=export_style
        )

        
        base_storage_path = Path(self.storage_provider.base_path)
        exports_dir = base_storage_path.parent / "exports"
        exports_dir.mkdir(parents=True, exist_ok=True)

        filename = f"dataset_{dataset_id}_{export_style}.{format_type.lower()}"
        file_path = exports_dir / filename

        with open(file_path, "w", encoding="utf-8") as f:
            f.write(serialized_data)

        logger.info(f"Arquivo físico de exportação gravado com sucesso em: {file_path}")

        
        artifact_id = uuid4()
        artifact_model = ExportArtifactModel(
            id=artifact_id,
            dataset_id=dataset_id,
            filename=filename,
            file_path=str(file_path),
            format=format_type.lower(),
            created_at=datetime.utcnow()
        )

        self.db_session.add(artifact_model)
        self.db_session.commit()

        
        return ExportArtifact(
            id=artifact_id,
            dataset_id=dataset_id,
            filename=filename,
            file_path=str(file_path),
            format=format_type.lower(),
            created_at=artifact_model.created_at
        )