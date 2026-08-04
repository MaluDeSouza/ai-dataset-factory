import logging
from domain.entities import Document
from infrastructure.providers.embedding_provider import EmbeddingProvider

logger = logging.getLogger(__name__)

class EmbeddingPipeline:
    def __init__(self, embedding_provider: EmbeddingProvider):
        self.provider = embedding_provider

    def process(self, document: Document) -> Document:
        """
        Itera sobre todos os chunks fatiados do documento e gera seus respectivos vetores.
        """
        if not document.chunks:
            return document

        for chunk in document.chunks:
            try:
            
                chunk.embedding = self.provider.generate_embedding(chunk.content)
            except Exception as e:
                logger.error(f"Erro ao gerar embedding para chunk {chunk.id}: {e}")
                
        document.status = "embedded"
        return document