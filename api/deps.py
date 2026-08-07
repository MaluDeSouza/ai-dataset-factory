from typing import Generator
from fastapi import Depends
from sqlalchemy.orm import Session
from infrastructure.database.session import SessionLocal

# Provedores de Infraestrutura
from infrastructure.storage.local_storage import LocalStorageProvider
from infrastructure.providers.llm_provider import LLMProvider
from infrastructure.providers.embedding_provider import EmbeddingProvider

# Casos de Uso (Use Cases)
from application.use_cases.import_dataset_use_case import ImportDatasetUseCase
from application.use_cases.get_dataset_status_use_case import GetDatasetStatusUseCase
from application.use_cases.process_document_use_case import ProcessDocumentUseCase
from application.use_cases.process_dataset_async_use_case import ProcessDatasetAsyncUseCase
from application.use_cases.export_dataset_use_case import ExportDatasetUseCase

# Pipelines de Processamento e Auditoria
from application.pipelines.import_pipeline import ImportPipeline
from application.pipelines.cleaning_pipeline import CleaningPipeline
from application.pipelines.classification_pipeline import ClassificationPipeline
from application.pipelines.anonymization_pipeline import ContextualAnonymizationPipeline
from application.pipelines.chunking_pipeline import ChunkingPipeline
from application.pipelines.embedding_pipeline import EmbeddingPipeline
from application.pipelines.validation_pipeline import ValidationPipeline
from application.pipelines.export_pipeline import ExportPipeline


def get_db() -> Generator[Session, None, None]:
    """Gerencia o ciclo de vida da sessão do banco de dados por requisição."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def get_storage_provider() -> LocalStorageProvider:
    """Injeta o provedor de storage local para gravação física de uploads e exportações."""
    return LocalStorageProvider()


def get_llm_provider() -> LLMProvider:
    """Injeta o provedor de modelos de linguagem (Gemini/OpenAI) com fallback automático."""
    return LLMProvider()


def get_embedding_provider() -> EmbeddingProvider:
    """Injeta o provedor dedicado para geração de vetores."""
    return EmbeddingProvider()


def get_validation_pipeline() -> ValidationPipeline:
    """Injeta o pipeline de validação de qualidade e duplicidade de chunks."""
    return ValidationPipeline()


def get_export_pipeline() -> ExportPipeline:
    """Injeta o pipeline de formatação estruturada de arquivos (JSONL, JSON, CSV)."""
    return ExportPipeline()


def get_import_dataset_use_case(
    db: Session = Depends(get_db),
    storage: LocalStorageProvider = Depends(get_storage_provider)
) -> ImportDatasetUseCase:
    """Injeta o caso de uso de importação de arquivos."""
    return ImportDatasetUseCase(db_session=db, storage_provider=storage)


def get_dataset_status_use_case(
    db: Session = Depends(get_db)
) -> GetDatasetStatusUseCase:
    """Injeta o caso de uso de consolidação de status e progresso."""
    return GetDatasetStatusUseCase(db_session=db)


def get_process_document_use_case(
    db: Session = Depends(get_db),
    storage: LocalStorageProvider = Depends(get_storage_provider),
    llm: LLMProvider = Depends(get_llm_provider),
    embedding: EmbeddingProvider = Depends(get_embedding_provider)
) -> ProcessDocumentUseCase:
    """
    Monta o maestro de processamento síncrono de documentos com todos os seus pipelines.
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


def get_process_dataset_async_use_case(
    db: Session = Depends(get_db),
    process_doc_use_case: ProcessDocumentUseCase = Depends(get_process_document_use_case),
    validation: ValidationPipeline = Depends(get_validation_pipeline)
) -> ProcessDatasetAsyncUseCase:
    """
    Injeta o caso de uso de processamento em background (lote de dataset).
    Reutiliza a estrutura de processamento de documentos individuais para garantir conformidade.
    """
    return ProcessDatasetAsyncUseCase(
        db_session=db,
        process_document_use_case=process_doc_use_case,
        validation_pipeline=validation
    )


def get_export_dataset_use_case(
    db: Session = Depends(get_db),
    storage: LocalStorageProvider = Depends(get_storage_provider),
    validation: ValidationPipeline = Depends(get_validation_pipeline),
    export: ExportPipeline = Depends(get_export_pipeline)
) -> ExportDatasetUseCase:
    """Injeta o caso de uso de exportação de datasets higienizados."""
    return ExportDatasetUseCase(
        db_session=db,
        storage_provider=storage,
        validation_pipeline=validation,
        export_pipeline=export
    )