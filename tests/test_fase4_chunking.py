import pytest
from uuid import uuid4

from domain.entities import Document
from application.pipelines.chunking_pipeline import ChunkingPipeline


def test_chunking_pipeline_precision_and_tokens():
    
    dataset_id = uuid4()
    doc = Document(
        dataset_id=dataset_id,
        filename="manual_arquitetura_rag.txt",
        cleaned_content=(
            "A arquitetura RAG (Retrieval-Augmented Generation) combina a capacidade de recuperação "
            "de informação de um sistema de busca vetorial com a capacidade de geração de linguagem natural "
            "dos LLMs modernos. Isso permite que a IA responda com base em documentos privados, "
            "reduzindo drasticamente a incidência de alucinações e garantindo rastreabilidade do conhecimento. "
            "Na primeira fase do pipeline, fazemos a ingestão e limpeza do texto para remover ruídos. "
            "Na segunda fase, o fatiamento (chunking) divide o texto em segmentos menores preservando a semântica. "
            "Na terceira fase, geramos vetores (embeddings) para cada chunk e os armazenamos em um banco vetorial."
        ),
        status="cleaned"
    )

    
    chunk_size = 30  
    chunk_overlap = 5
    pipeline = ChunkingPipeline(chunk_size=chunk_size, chunk_overlap=chunk_overlap)

    
    processed_doc = pipeline.process(doc)

    assert processed_doc.status == "chunked"
    assert len(processed_doc.chunks) > 1

    for chunk in processed_doc.chunks:
        
        assert chunk.token_count <= chunk_size
        
        assert chunk.document_id == processed_doc.id
        
        assert len(chunk.content.strip()) > 0

    
    first_chunk_text = processed_doc.chunks[0].content
    actual_tokens = pipeline._token_length(first_chunk_text)
    assert processed_doc.chunks[0].token_count == actual_tokens