import os
import logging
import google.generativeai as genai
from openai import OpenAI

logger = logging.getLogger(__name__)

class EmbeddingProvider:
    def __init__(self):
        self.active_providers = []
        
        # Prioridade 1: Gemini
        gemini_key = os.getenv("GEMINI_API_KEY")
        if gemini_key:
            genai.configure(api_key=gemini_key)
            self.active_providers.append("gemini")
            
        # Prioridade 2: OpenAI (Fallback)
        openai_key = os.getenv("OPENAI_API_KEY")
        if openai_key:
            self.openai_client = OpenAI(api_key=openai_key)
            self.active_providers.append("openai")

        if not self.active_providers:
            raise ValueError("Nenhuma chave de API encontrada para embeddings no .env")

    def generate_embedding(self, text: str) -> list[float]:
        """Gera a representação vetorial do texto usando o provedor disponível."""
        for provider in self.active_providers:
            try:
                if provider == "gemini":
                    return self._call_gemini(text)
                elif provider == "openai":
                    return self._call_openai(text)
            except Exception as e:
                logger.warning(f"Provedor de embedding '{provider}' falhou: {e}. Tentando o próximo...")
                continue
                
        raise RuntimeError("Todos os provedores de embedding falharam ou estão indisponíveis.")

    def _call_gemini(self, text: str) -> list[float]:
        result = genai.embed_content(
            model="models/text-embedding-004",
            content=text,
            task_type="retrieval_document"
        )
        return result['embedding']

    def _call_openai(self, text: str) -> list[float]:
        response = self.openai_client.embeddings.create(
            input=text,
            model="text-embedding-3-small"
        )
        return response.data[0].embedding