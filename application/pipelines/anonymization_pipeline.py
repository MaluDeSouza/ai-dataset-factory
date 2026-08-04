import logging
from domain.entities import Document
from infrastructure.providers.llm_provider import LLMProvider

logger = logging.getLogger(__name__)

class ContextualAnonymizationPipeline:
    def __init__(self, llm_provider: LLMProvider):
        self.llm = llm_provider

    def process(self, document: Document) -> Document:
        """
        Usa o LLM para remover dados sensíveis complexos (endereços, nomes) 
        e ruídos semânticos (saudações) que passaram pela Regex.
        """
        if not document.cleaned_content:
            return document

        system_prompt = (
            "Você é um especialista corporativo em sanitização de dados para sistemas de Inteligência Artificial. "
            "Sua tarefa é analisar o texto fornecido e retornar O MESMO TEXTO, mas aplicando as seguintes regras: "
            "1. Substitua nomes próprios de pessoas físicas por [NOME]. "
            "2. Substitua endereços físicos completos por [ENDERECO]. "
            "3. Remova completamente ruídos semânticos de conversação (como saudações, cumprimentos e despedidas). "
            "Mantenha o contexto técnico, as informações úteis e a formatação intactas. "
            "Não adicione comentários, aspas ou explicações na sua resposta. Retorne APENAS o texto sanitizado."
        )

        user_prompt = f"Texto original:\n{document.cleaned_content}"

        try:
            
            sanitized_text = self.llm.generate_text(system_prompt, user_prompt, temperature=0.0)
            document.cleaned_content = sanitized_text
            document.status = "anonymized_and_cleaned"
        except Exception as e:
            logger.error(f"Erro na anonimização contextual do documento {document.id}: {e}")
            document.status = "anonymization_failed_regex_fallback"

        return document