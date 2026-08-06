from typing import List, Tuple
from sqlalchemy.orm import Session
from infrastructure.database.models import DatasetModel, DocumentModel
from infrastructure.storage.local_storage import LocalStorageProvider

class ImportDatasetUseCase:
    def __init__(self, db_session: Session, storage_provider: LocalStorageProvider):
        self.db_session = db_session
        self.storage_provider = storage_provider

    def execute(self, dataset_name: str, files: List[Tuple[str, bytes]]) -> DatasetModel:
        """
        Cria o Dataset e itera sobre os arquivos, salvando no disco físico e registrando 
        os Documentos no banco. Retorna o modelo atualizado.
        """
        dataset = DatasetModel(name=dataset_name)
        self.db_session.add(dataset)
        
        self.db_session.flush()

        for filename, content in files:
            
            safe_filename = f"{dataset.id}_{filename}"
            file_path = self.storage_provider.save_file(
                filename=safe_filename, 
                content=content
            )
            
            
            doc = DocumentModel(
                dataset_id=dataset.id,
                filename=filename,
                original_content=file_path, 
                status="uploaded"
            )
            self.db_session.add(doc)

        self.db_session.commit()
        self.db_session.refresh(dataset)
        
        return dataset