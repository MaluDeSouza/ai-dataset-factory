import csv
import io
import json
from typing import List, Dict, Any
from domain.entities import Chunk, Document

class ExportPipeline:
    """
    Pipeline de engenharia de dados responsável por formatar e serializar chunks 
    e documentos aprovados na validação para formatos prontos para treinamento (Hugging Face).
    """
    def serialize(self, chunks: List[Chunk], documents_map: Dict[str, Document], format_type: str = "jsonl", export_style: str = "text") -> str:
        """
        Converte a lista de chunks validados no formato de exportação desejado.
        
        Args:
            chunks: Lista de chunks aprovados no ValidationPipeline.
            documents_map: Dicionário mapeando a string do ID do documento para o objeto Document do domínio.
            format_type: Formato de arquivo desejado ("jsonl", "json", "csv").
            export_style: Estilo do dataset ("text", "instruction", "prompt_completion").
            
        Retorna:
            str: String serializada pronta para ser gravada em disco.
        """
        format_type = format_type.lower()
        export_style = export_style.lower()

        if format_type == "jsonl":
            return self._to_jsonl(chunks, documents_map, export_style)
        elif format_type == "json":
            return self._to_json(chunks, documents_map, export_style)
        elif format_type == "csv":
            return self._to_csv(chunks, documents_map, export_style)
        else:
            raise ValueError(f"Formato de exportação '{format_type}' não suportado. Use 'jsonl', 'json' ou 'csv'.")

    def _format_item(self, chunk: Chunk, doc: Document, style: str) -> Dict[str, Any]:
        """
        Aplica o mapeamento de campos do dataset de acordo com o estilo de fine-tuning.
        """
        if style == "instruction":
            
            instruction = "Com base no trecho de texto fornecido, responda às dúvidas com exatidão científica."
            if doc.category:
                instruction = f"Você é um assistente especialista na categoria: {doc.category}. Extraia e responda de forma clara as informações do trecho a seguir."
            
            return {
                "instruction": instruction,
                "input": f"Documento: {doc.filename}\n\nTrecho:\n{chunk.content}",
                "output": chunk.content  
            }
            
        elif style == "prompt_completion":
            
            prompt = f"Documento de origem: {doc.filename} | Categoria: {doc.category or 'Geral'}\nTrecho de referência: {chunk.content[:150]}...\nRetorne o texto integral de referência:"
            return {
                "prompt": prompt,
                "completion": f" {chunk.content}"  
            }
            
        else:
            
            return {
                "text": chunk.content,
                "metadata": {
                    "document_id": str(doc.id),
                    "filename": doc.filename,
                    "category": doc.category,
                    "token_count": chunk.token_count
                }
            }

    def _to_jsonl(self, chunks: List[Chunk], documents_map: Dict[str, Document], style: str) -> str:
        lines = []
        for chunk in chunks:
            doc = documents_map.get(str(chunk.document_id))
            if not doc:
                continue
            item = self._format_item(chunk, doc, style)
            
            lines.append(json.dumps(item, ensure_ascii=False))
        return "\n".join(lines)

    def _to_json(self, chunks: List[Chunk], documents_map: Dict[str, Document], style: str) -> str:
        items = []
        for chunk in chunks:
            doc = documents_map.get(str(chunk.document_id))
            if not doc:
                continue
            items.append(self._format_item(chunk, doc, style))
        return json.dumps(items, ensure_ascii=False, indent=2)

    def _to_csv(self, chunks: List[Chunk], documents_map: Dict[str, Document], style: str) -> str:
        if not chunks:
            return ""

        output = io.StringIO()
        
        
        first_doc = documents_map.get(str(chunks.document_id))
        if not first_doc:
            return ""
            
        first_item = self._format_item(chunks, first_doc, style)
        
        
        fieldnames = []
        for key, val in first_item.items():
            if isinstance(val, dict):
                for sub_key in val.keys():
                    fieldnames.append(f"metadata_{sub_key}")
            else:
                fieldnames.append(key)

        writer = csv.DictWriter(output, fieldnames=fieldnames)
        writer.writeheader()

        for chunk in chunks:
            doc = documents_map.get(str(chunk.document_id))
            if not doc:
                continue
            item = self._format_item(chunk, doc, style)
            
            
            row = {}
            for key, val in item.items():
                if isinstance(val, dict):
                    for sub_key, sub_val in val.items():
                        row[f"metadata_{sub_key}"] = sub_val
                else:
                    row[key] = val
            writer.writerow(row)

        return output.getvalue()