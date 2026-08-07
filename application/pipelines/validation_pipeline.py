import hashlib
import json
from typing import List, Tuple, Dict, Any
from uuid import UUID, uuid4
from datetime import datetime
from domain.entities import Chunk, ValidationReport

class ValidationPipeline:
    """
    Pipeline de engenharia de dados responsável por auditar a qualidade de fatiamento (chunks).
    Garante a eliminação de duplicidades, ruídos de formatação e desvios de tamanho.
    """
    def __init__(self, min_token_count: int = 10, max_token_count: int = 800):
        self.min_token_count = min_token_count
        self.max_token_count = max_token_count

    def process(self, dataset_id: UUID, chunks: List[Chunk]) -> Tuple[List[Chunk], ValidationReport]:
        """
        Processa e filtra chunks inválidos ou redundantes de um dataset.
        
        Retorna:
            Tuple[List[Chunk], ValidationReport]: Lista contendo apenas chunks aprovados 
            e o relatório consolidado de auditoria pronto para persistência.
        """
        total_chunks = len(chunks)
        valid_chunks: List[Chunk] = []
        invalid_details: List[Dict[str, Any]] = []
        
       
        seen_hashes = set()

        for chunk in chunks:
            reasons = []
            content_stripped = chunk.content.strip()

            # 1. Validação de conteúdo vazio
            if not content_stripped:
                reasons.append("Conteúdo puramente vazio ou composto apenas de caracteres de controle")

            # 2. Validação de limites de tokens
            elif chunk.token_count < self.min_token_count:
                reasons.append(f"Densidade de informação abaixo do limite ({chunk.token_count} < {self.min_token_count} tokens)")
            elif chunk.token_count > self.max_token_count:
                reasons.append(f"Tamanho do bloco acima do limite permitido ({chunk.token_count} > {self.max_token_count} tokens)")

            # 3. Validação de duplicidade textual estrutural
        
            normalized_content = " ".join(content_stripped.lower().split())
            content_hash = hashlib.sha256(normalized_content.encode("utf-8")).hexdigest()
            
            if content_hash in seen_hashes:
                reasons.append("Bloco de texto duplicado no escopo do processamento")
            else:
                
                if not reasons:
                    seen_hashes.add(content_hash)

            
            if not reasons:
                valid_chunks.append(chunk)
            else:
                invalid_details.append({
                    "chunk_id": str(chunk.id),
                    "document_id": str(chunk.document_id),
                    "token_count": chunk.token_count,
                    "reasons": reasons,
                    "preview": content_stripped[:100] + "..." if len(content_stripped) > 100 else content_stripped
                })

        valid_count = len(valid_chunks)
        invalid_count = total_chunks - valid_count

        
        if total_chunks == 0:
            summary = "Nenhum bloco de texto foi fornecido para validação de qualidade."
        else:
            success_rate = (valid_count / total_chunks) * 100
            summary = (
                f"Auditoria concluída com sucesso. Taxa de aprovação: {success_rate:.2f}% "
                f"({valid_count} aprovados, {invalid_count} rejeitados de um total de {total_chunks})."
            )

        
        details_str = json.dumps(invalid_details, ensure_ascii=False, indent=2) if invalid_details else "[]"

        report = ValidationReport(
            id=uuid4(),
            dataset_id=dataset_id,
            total_chunks=total_chunks,
            valid_chunks=valid_count,
            invalid_chunks=invalid_count,
            summary=summary,
            details=details_str,
            created_at=datetime.utcnow()
        )

        return valid_chunks, report
