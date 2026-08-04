import re
import unicodedata
from domain.entities import Document

class CleaningPipeline:
    def process(self, document: Document) -> Document:
        """
        Recebe um Documento importado, higieniza o texto e preenche o cleaned_content.
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

        # 3. Anonimização Básica: E-mails
        email_pattern = re.compile(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,7}\b')
        text = email_pattern.sub('[EMAIL]', text)

        # 4. Limpeza estrutural: reduz múltiplas quebras de linha e espaços para um só
        text = re.sub(r'\n{2,}', '\n', text)
        text = re.sub(r'[ \t]+', ' ', text)
        
        # 5. Remove espaços em branco nas bordas de cada linha e ignora linhas totalmente vazias
        cleaned_lines = [line.strip() for line in text.split('\n') if line.strip()]
        text = "\n".join(cleaned_lines)

        document.cleaned_content = text
        document.status = "cleaned"

        return document