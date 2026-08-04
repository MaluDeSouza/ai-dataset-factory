import os
import pytest
from uuid import uuid4

from infrastructure.storage.local_storage import LocalStorageProvider
from application.pipelines.import_pipeline import ImportPipeline
from application.pipelines.cleaning_pipeline import CleaningPipeline


@pytest.fixture
def storage_provider():
    return LocalStorageProvider(base_path="./temp/test_pipeline_uploads")


def test_import_and_cleaning_pipeline(storage_provider):
    
    dataset_id = uuid4()
    raw_text = (
        "  Este é um documento de teste com lixo.   \n\n\n"
        "Acesse o site https://example.com para mais detalhes.  \n"
        "Contato direto pelo e-mail suporte@empresa.com.br para duvidas.  \n\n"
        "Linha   com    muitos   espacos.  "
    )
    filename = f"documento_sujo_{uuid4()}.txt"
    saved_path = storage_provider.save_file(filename, raw_text.encode("utf-8"))

    
    import_pipeline = ImportPipeline(storage_provider=storage_provider)
    cleaning_pipeline = CleaningPipeline()

    
    imported_document = import_pipeline.process(dataset_id=dataset_id, filepath=saved_path)
    cleaned_document = cleaning_pipeline.process(imported_document)

    
    assert cleaned_document.status == "cleaned"
    assert cleaned_document.cleaned_content is not None
    assert "https://example.com" not in cleaned_document.cleaned_content
    assert "suporte@empresa.com.br" not in cleaned_document.cleaned_content
    assert "[EMAIL]" in cleaned_document.cleaned_content
    assert "Linha com muitos espacos." in cleaned_document.cleaned_content

    
    if os.path.exists(saved_path):
        os.remove(saved_path)