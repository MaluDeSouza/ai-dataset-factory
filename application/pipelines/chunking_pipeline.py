import tiktoken
from langchain_text_splitters import RecursiveCharacterTextSplitter
from domain.entities import Document, Chunk

class ChunkingPipeline:
    def __init__(self, chunk_size: int = 500, chunk_overlap: int = 50, model_name: str = "gpt-4o"):
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        
        
        try:
            self.encoding = tiktoken.encoding_for_model(model_name)
        except KeyError:
            self.encoding = tiktoken.get_encoding("cl100k_base")
            
        
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=self.chunk_size,
            chunk_overlap=self.chunk_overlap,
            length_function=self._token_length,
            separators=["\n\n", "\n", ".", " ", ""]
        )

    def _token_length(self, text: str) -> int:
        """Calcula a quantidade real de tokens de um texto."""
        return len(self.encoding.encode(text))

    def process(self, document: Document) -> Document:
        """Fatia o conteúdo limpo em chunks e anexa à entidade do documento."""
        if not document.cleaned_content:
            document.status = "chunked_empty"
            return document

        
        raw_chunks = self.text_splitter.split_text(document.cleaned_content)
        
        
        for text_chunk in raw_chunks:
            token_count = self._token_length(text_chunk)
            
            chunk_entity = Chunk(
                document_id=document.id,
                content=text_chunk,
                token_count=token_count
            )
            document.chunks.append(chunk_entity)

        document.status = "chunked"
        return document