import os
from pathlib import Path

class LocalStorageProvider:
    def __init__(self, base_path: str = "./temp/uploads"):
        self.base_path = Path(base_path)
        self.base_path.mkdir(parents=True, exist_ok=True)

    def save_file(self, filename: str, content: bytes) -> str:
        """Salva um arquivo fisicamente e retorna o caminho completo."""
        file_path = self.base_path / filename
        with open(file_path, "wb") as f:
            f.write(content)
        return str(file_path)

    def read_file(self, filepath: str) -> str:
        """Lê o conteúdo de um arquivo."""
        with open(filepath, "r", encoding="utf-8") as f:
            return f.read()