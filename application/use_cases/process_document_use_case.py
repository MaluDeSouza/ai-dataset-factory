from uuid import UUID
from sqlalchemy.orm import Session

from application.pipelines.import_pipeline import ImportPipeline
from application.pipelines.cleaning_pipeline import CleaningPipeline
from application.pipelines.classification_pipeline import ClassificationPipeline
from application.pipelines.anonymization_pipeline import ContextualAnonymizationPipeline
from application.pipelines.chunking_pipeline import ChunkingPipeline
from application.pipelines.embedding_pipeline import EmbeddingPipeline
from infrastructure.database.models import DocumentModel, ChunkModel


class ProcessDocumentUseCase:
    def __init__(
        self,
        import_pipeline: ImportPipeline,
        cleaning_pipeline: CleaningPipeline,
        classification_pipeline: ClassificationPipeline,
        anonymization_pipeline: ContextualAnonymizationPipeline,
        chunking_pipeline: ChunkingPipeline,
        embedding_pipeline: EmbeddingPipeline,
        db_session: Session
    ):
        self.import_pipeline = import_pipeline
        self.cleaning_pipeline = cleaning_pipeline
        self.classification_pipeline = classification_pipeline
        self.anonymization_pipeline = anonymization_pipeline
        self.chunking_pipeline = chunking_pipeline
        self.embedding_pipeline = embedding_pipeline
        self.db_session = db_session

    def execute(self, document_id: UUID, dataset_id: UUID, filepath: str) -> DocumentModel:
        """
        Orquestra o ciclo de vida completo de um documento: leitura, limpeza, 
        classificação, anonimização, fatiamento, vetorização e atualização no banco.
        """
        
        doc = self.import_pipeline.process(document_id=document_id, dataset_id=dataset_id, filepath=filepath)
        doc = self.cleaning_pipeline.process(document=doc)
        doc = self.classification_pipeline.process(document=doc)
        doc = self.anonymization_pipeline.process(document=doc)
        doc = self.chunking_pipeline.process(document=doc)
        doc = self.embedding_pipeline.process(document=doc)

        
        doc.status = "processed"

        
        db_document = self.db_session.query(DocumentModel).filter(DocumentModel.id == document_id).first()
        
        if not db_document:
            raise ValueError(f"Documento {document_id} não encontrado no banco de dados para atualização.")

        
        db_document.original_content = doc.original_content
        db_document.cleaned_content = doc.cleaned_content
        db_document.category = doc.category
        db_document.status = doc.status

        
        for chunk_entity in doc.chunks:
            db_chunk = ChunkModel(
                id=chunk_entity.id,
                document_id=chunk_entity.document_id,
                content=chunk_entity.content,
                token_count=chunk_entity.token_count,
                embedding=chunk_entity.embedding
            )
            db_document.chunks.append(db_chunk)

        self.db_session.commit()
        self.db_session.refresh(db_document)

        return db_document