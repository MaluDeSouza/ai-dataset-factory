import re
import unicodedata
from domain.entities import Document

class CleaningPipeline:
    def process(self, document: Document) -> Document:
        """
        Recebe um Documento importado, higieniza o texto, remove PII e preenche o cleaned_content.
        """
        if not document.original_content:
            document.cleaned_content = ""
            document.status = "cleaned_empty"
            return document

        text = document.original_content

        # 1. Normalização Unicode 
        text = unicodedata.normalize("NFKC", text)

        # 2. Remoção de URLs
        url_pattern = re.compile(r'https?://\S+|www\.\S+')
        text = url_pattern.sub('', text)

        # 3. Anonimização: E-mails
        email_pattern = re.compile(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,7}\b')
        text = email_pattern.sub('[EMAIL]', text)

        # 4. Anonimização: CNPJ e CPF
        cnpj_pattern = re.compile(r'\b\d{2}\.\d{3}\.\d{3}/\d{4}-\d{2}\b')
        text = cnpj_pattern.sub('[CNPJ]', text)
        
        cpf_pattern = re.compile(r'\b\d{3}\.\d{3}\.\d{3}-\d{2}\b')
        text = cpf_pattern.sub('[CPF]', text)

        # 5. Anonimização: Telefones (Captura formatos como +55483333-4444, (48) 99999-1234, etc.)
        phone_pattern = re.compile(r'(?:\+55\s?)?(?:\(?\d{2}\)?[\s-]?)?\d{4,5}[-\s]?\d{4}\b')
        text = phone_pattern.sub('[TELEFONE]', text)

        # 6. Redução de Ruído: Pontuações exageradas (ex: !!! -> !, ??? -> ?)
        text = re.sub(r'!{2,}', '!', text)
        text = re.sub(r'\?{2,}', '?', text)

        # 7. Limpeza estrutural: reduz múltiplas quebras de linha e espaços para um só
        text = re.sub(r'\n{2,}', '\n', text)
        text = re.sub(r'[ \t]+', ' ', text)
        
        # 8. Remove espaços em branco nas bordas de cada linha e ignora linhas totalmente vazias
        cleaned_lines = [line.strip() for line in text.split('\n') if line.strip()]
        text = "\n".join(cleaned_lines)

        
        document.cleaned_content = text
        document.status = "cleaned"

        return document