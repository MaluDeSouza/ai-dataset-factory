import os
import pytest
from uuid import uuid4

from domain.entities import Dataset as DatasetEntity, Document as DocumentEntity
from infrastructure.database.models import DatasetModel, DocumentModel
from infrastructure.database.session import SessionLocal
from infrastructure.storage.local_storage import LocalStorageProvider


@pytest.fixture
def db_session():
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()


@pytest.fixture
def storage_provider():
    return LocalStorageProvider(base_path="./temp/test_uploads")

def test_end_to_end_fase2(db_session, storage_provider):
    
    dataset_entity = DatasetEntity(name="Dataset de Teste Backend")
    
   
    file_content = b"Conteudo limpo do arquivo PDF processado."
    filename = f"test_document_{uuid4()}.txt"
    saved_path = storage_provider.save_file(filename, file_content)
    
   
    assert os.path.exists(saved_path)
    
    
    doc_entity = DocumentEntity(
        dataset_id=dataset_entity.id,
        filename=filename,
        original_content=storage_provider.read_file(saved_path)
    )
    dataset_entity.documents.append(doc_entity)
    
  
    db_dataset = DatasetModel(id=dataset_entity.id, name=dataset_entity.name)
    db_document = DocumentModel(
        id=doc_entity.id,
        dataset_id=doc_entity.dataset_id,
        filename=doc_entity.filename,
        original_content=doc_entity.original_content
    )
    
    
    db_session.add(db_dataset)
    db_session.add(db_document)
    db_session.commit()
    
   
    saved_dataset = db_session.query(DatasetModel).filter_by(id=dataset_entity.id).first()
    
    assert saved_dataset is not None
    assert saved_dataset.name == "Dataset de Teste Backend"
    assert len(saved_dataset.documents) == 1
    assert saved_dataset.documents[0].filename == filename
    assert saved_dataset.documents[0].original_content == "Conteudo limpo do arquivo PDF processado."
    
    
    db_session.delete(saved_dataset)
    db_session.commit()
    
    if os.path.exists(saved_path):
        os.remove(saved_path)