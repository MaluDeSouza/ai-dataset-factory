import logging
from domain.entities import Document
from infrastructure.providers.llm_provider import LLMProvider

logger = logging.getLogger(__name__)

class ClassificationPipeline:
    def __init__(self, llm_provider: LLMProvider):
        self.llm = llm_provider

    def process(self, document: Document) -> Document:
        """
        Analisa uma amostra do documento e define a sua categoria principal usando IA.
        """
        if not document.cleaned_content:
            document.category = "VAZIO"
            return document

    
        sample_text = document.cleaned_content[:1500]

        system_prompt = (
            "Você é um classificador automático de documentos altamente preciso para um sistema RAG. "
            "Analise o texto fornecido e classifique-o ESTRITAMENTE em uma das seguintes categorias: "
            "FINANCEIRO, TECNICO, RECURSOS_HUMANOS, ATENDIMENTO_CLIENTE, JURIDICO, AGRICULTURA, OUTROS. "
            "Sua resposta deve conter APENAS o nome da categoria exata, sem pontuações ou explicações adicionais."
        )

        user_prompt = f"Documento:\n{sample_text}"

        try:
            
            category = self.llm.generate_text(system_prompt, user_prompt, temperature=0.0)
            
            document.category = category.strip().upper()
        except Exception as e:
            logger.error(f"Erro ao classificar documento {document.id}: {e}")
            document.category = "ERRO_CLASSIFICACAO"

        return document