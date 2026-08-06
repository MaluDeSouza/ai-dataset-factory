from typing import Generator
from fastapi import Depends
from sqlalchemy.orm import Session
from infrastructure.database.session import SessionLocal 

from infrastructure.storage.local_storage import LocalStorageProvider
from infrastructure.providers.llm_provider import LLMProvider
from infrastructure.providers.embedding_provider import EmbeddingProvider

from application.use_cases.import_dataset_use_case import ImportDatasetUseCase
from application.use_cases.get_dataset_status_use_case import GetDatasetStatusUseCase
from application.use_cases.process_document_use_case import ProcessDocumentUseCase

# Import dos pipelines necessários para orquestrar o processamento
from application.pipelines.import_pipeline import ImportPipeline
from application.pipelines.cleaning_pipeline import CleaningPipeline
from application.pipelines.classification_pipeline import ClassificationPipeline
from application.pipelines.anonymization_pipeline import ContextualAnonymizationPipeline
from application.pipelines.chunking_pipeline import ChunkingPipeline
from application.pipelines.embedding_pipeline import EmbeddingPipeline


def get_db() -> Generator[Session, None, None]:
    """Gerencia o ciclo de vida da sessão do banco de dados por requisição."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def get_storage_provider() -> LocalStorageProvider:
    """Injeta o provedor de storage. Se fôssemos para a nuvem, trocaríamos aqui."""
    return LocalStorageProvider()


def get_llm_provider() -> LLMProvider:
    """Injeta o provedor de modelos de linguagem (Gemini/OpenAI)."""
    return LLMProvider()


def get_embedding_provider() -> EmbeddingProvider:
    """Injeta o provedor dedicado para geração de vetores."""
    return EmbeddingProvider()


def get_import_dataset_use_case(
    db: Session = Depends(get_db),
    storage: LocalStorageProvider = Depends(get_storage_provider)
) -> ImportDatasetUseCase:
    return ImportDatasetUseCase(db_session=db, storage_provider=storage)


def get_dataset_status_use_case(
    db: Session = Depends(get_db)
) -> GetDatasetStatusUseCase:
    return GetDatasetStatusUseCase(db_session=db)


def get_process_document_use_case(
    db: Session = Depends(get_db),
    storage: LocalStorageProvider = Depends(get_storage_provider),
    llm: LLMProvider = Depends(get_llm_provider),
    embedding: EmbeddingProvider = Depends(get_embedding_provider)
) -> ProcessDocumentUseCase:
    """
    Monta o maestro de processamento com todos os seus pipelines.
    Injeta as dependências de infraestrutura estritamente onde são necessárias.
    """
    return ProcessDocumentUseCase(
        import_pipeline=ImportPipeline(storage_provider=storage), 
        cleaning_pipeline=CleaningPipeline(),
        classification_pipeline=ClassificationPipeline(llm_provider=llm),
        anonymization_pipeline=ContextualAnonymizationPipeline(llm_provider=llm),
        chunking_pipeline=ChunkingPipeline(),
        embedding_pipeline=EmbeddingPipeline(embedding_provider=embedding),
        db_session=db
    )