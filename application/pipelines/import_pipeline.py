import os
from uuid import UUID
from pypdf import PdfReader

from domain.entities import Document
from infrastructure.storage.local_storage import LocalStorageProvider


class ImportPipeline:
    def __init__(self, storage_provider: LocalStorageProvider):
        self.storage_provider = storage_provider

    def process(self, document_id: UUID, dataset_id: UUID, filepath: str) -> Document:
        """
        Lê o arquivo físico e converte para a entidade Document de domínio.
        """
        if not os.path.exists(filepath):
            raise FileNotFoundError(f"Arquivo não encontrado no storage: {filepath}")

        filename = os.path.basename(filepath)
        extension = filename.split(".")[-1].lower()

        if extension == "txt":
            # Usa o provider para ler o TXT respeitando o encoding
            content = self.storage_provider.read_file(filepath)
        elif extension == "pdf":
            # Usa o pypdf para extrair texto
            content = self._extract_text_from_pdf(filepath)
        else:
            raise ValueError(f"Formato de arquivo não suportado para ingestão: {extension}")

        # Retorna a entidade pura mantendo o ID original para não duplicar no banco
        return Document(
            id=document_id,
            dataset_id=dataset_id,
            filename=filename,
            original_content=content,
            status="imported"
        )

    def _extract_text_from_pdf(self, filepath: str) -> str:
        """
        Extrai o texto de um PDF página por página.
        """
        reader = PdfReader(filepath)
        text_pages = []
        
        for page in reader.pages:
            extracted = page.extract_text()
            if extracted:
                text_pages.append(extracted)
                
        return "\n".join(text_pages)