import logging
from uuid import UUID
from sqlalchemy.orm import Session

from application.use_cases.process_document_use_case import ProcessDocumentUseCase
from application.pipelines.validation_pipeline import ValidationPipeline
from infrastructure.database.models import DocumentModel, ChunkModel
from domain.entities import Chunk

logger = logging.getLogger(__name__)

class ProcessDatasetAsyncUseCase:
    """
    Caso de Uso responsável por coordenar o processamento em lote de um dataset
    de forma assíncrona, executando a limpeza, classificação, anonimização,
    fatiamento e geração de embeddings para cada documento, seguido da validação de qualidade.
    """
    def __init__(
        self,
        db_session: Session,
        process_document_use_case: ProcessDocumentUseCase,
        validation_pipeline: ValidationPipeline
    ):
        self.db_session = db_session
        self.process_document_use_case = process_document_use_case
        self.validation_pipeline = validation_pipeline

    def execute(self, dataset_id: UUID) -> None:
        """
        Executa o pipeline completo de processamento para todos os documentos pendentes de um dataset.
        """
        logger.info(f"Iniciando processamento assíncrono do dataset {dataset_id}")
        
        # 1. Recupera os documentos pendentes ou enviados do dataset
        documents = self.db_session.query(DocumentModel).filter(
            DocumentModel.dataset_id == dataset_id,
            DocumentModel.status.in_(["uploaded", "pending"])
        ).all()
        
        if not documents:
            logger.warning(f"Nenhum documento pendente encontrado para o dataset {dataset_id}")
            return

        # 2. Processa cada documento individualmente
        for doc in documents:
            logger.info(f"Processando documento individual: {doc.filename} ({doc.id})")
            try:
                # Passa o ID do documento para rastrear e atualizar a mesma linha no banco
                self.process_document_use_case.execute(
                    document_id=doc.id,
                    dataset_id=doc.dataset_id,
                    filepath=doc.original_content
                )
            except Exception as e:
                logger.error(f"Erro ao processar o documento {doc.id} ({doc.filename}): {str(e)}", exc_info=True)
                doc.status = "failed"
                self.db_session.commit()
                continue

        # 3. Executa a validação de qualidade em lote para todo o dataset após processar todos os documentos
        logger.info(f"Iniciando validação de qualidade (ValidationPipeline) para o dataset {dataset_id}")
        try:
            doc_ids = [d.id for d in documents]
            db_chunks = self.db_session.query(ChunkModel).filter(
                ChunkModel.document_id.in_(doc_ids)
            ).all()
            
            if not db_chunks:
                logger.warning(f"Nenhum bloco de texto (chunk) gerado para o dataset {dataset_id}. Pulando validação.")
                return

            # Converte chunks do SQLAlchemy para entidades de domínio
            domain_chunks = [
                Chunk(
                    id=c.id,
                    document_id=c.document_id,
                    content=c.content,
                    token_count=c.token_count,
                    embedding=c.embedding
                )
                for c in db_chunks
            ]
            
            # Executa o pipeline de validação para gravar o relatório no banco de dados
            self.validation_pipeline.process(dataset_id=dataset_id, chunks=domain_chunks)
            logger.info(f"Validação de qualidade do dataset {dataset_id} concluída com sucesso.")
            
        except Exception as e:
            logger.error(f"Erro ao executar a validação de qualidade do dataset {dataset_id}: {str(e)}", exc_info=True)