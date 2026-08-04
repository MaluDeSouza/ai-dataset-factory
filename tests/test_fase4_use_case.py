import pytest
from uuid import uuid4
from unittest.mock import MagicMock

from application.use_cases.process_document_use_case import ProcessDocumentUseCase
from application.pipelines.import_pipeline import ImportPipeline
from application.pipelines.cleaning_pipeline import CleaningPipeline
from application.pipelines.classification_pipeline import ClassificationPipeline
from application.pipelines.anonymization_pipeline import ContextualAnonymizationPipeline
from application.pipelines.chunking_pipeline import ChunkingPipeline
from application.pipelines.embedding_pipeline import EmbeddingPipeline
from infrastructure.storage.local_storage import LocalStorageProvider

@pytest.fixture
def mock_dependencies():
    # 1. Mock do Storage e DB
    storage_provider = LocalStorageProvider(base_path="./temp/test_use_case")
    db_session_mock = MagicMock()

    # 2. Mock dos Provedores de IA 
    llm_provider_mock = MagicMock()
    # Simula o LLM devolvendo uma categoria e o texto anonimizado
    llm_provider_mock.generate_text.side_effect = [
        "TECNICO", 
        "Texto anonimizado pelo [NOME] para o teste."
    ]

    embedding_provider_mock = MagicMock()
    # Simula um vetor de 3 dimensões (o real teria 768 ou 1536)
    embedding_provider_mock.generate_embedding.return_value = [0.1, 0.2, 0.3]

    return storage_provider, db_session_mock, llm_provider_mock, embedding_provider_mock

def test_process_document_use_case(mock_dependencies):
    storage_provider, db_session_mock, llm_provider_mock, embedding_provider_mock = mock_dependencies

    # Instancia os pipelines com as dependências mockadas
    import_pipeline = ImportPipeline(storage_provider)
    cleaning_pipeline = CleaningPipeline()
    classification_pipeline = ClassificationPipeline(llm_provider_mock)
    anonymization_pipeline = ContextualAnonymizationPipeline(llm_provider_mock)
    chunking_pipeline = ChunkingPipeline(chunk_size=10, chunk_overlap=2)
    embedding_pipeline = EmbeddingPipeline(embedding_provider_mock)

    use_case = ProcessDocumentUseCase(
        import_pipeline, cleaning_pipeline, classification_pipeline,
        anonymization_pipeline, chunking_pipeline, embedding_pipeline,
        db_session_mock
    )

    # Cria um arquivo temporário simulando o upload
    dataset_id = uuid4()
    filename = f"teste_usecase_{uuid4()}.txt"
    filepath = storage_provider.save_file(filename, b"Conteudo original com nome Joao para testar.")

    # Executa o orquestrador
    db_document = use_case.execute(dataset_id=dataset_id, filepath=filepath)

    # Validações estruturais do Use Case
    assert db_document.status == "embedded"
    assert db_document.category == "TECNICO"
    assert len(db_document.chunks) > 0
    assert db_document.chunks[0].embedding == [0.1, 0.2, 0.3]

    
    db_session_mock.add.assert_called_once()
    db_session_mock.commit.assert_called_once()
    db_session_mock.refresh.assert_called_once()