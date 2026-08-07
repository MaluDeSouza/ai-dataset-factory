import os
import re
from pathlib import Path
from dotenv import load_dotenv
from sqlalchemy import create_engine, text

# 1. Carrega as variáveis de ambiente do seu arquivo .env
load_dotenv()
db_url = os.getenv("DATABASE_URL", "postgresql://admin:adminpassword@127.0.0.1:5435/dataset_factory")

print("\n=== INICIANDO DIAGNÓSTICO E CORREÇÃO AUTOMÁTICA ===")

# 2. Corrigindo referências diretamente no PostgreSQL
try:
    engine = create_engine(db_url)
    with engine.connect() as conn:
        # Garante que a tabela de controle exista
        conn.execute(text("CREATE TABLE IF NOT EXISTS alembic_version (version_num VARCHAR(32) PRIMARY KEY)"))
        
        # Verifica o estado atual do banco
        result = conn.execute(text("SELECT version_num FROM alembic_version")).fetchall()
        if result:
            conn.execute(text("UPDATE alembic_version SET version_num = '488a052bb9f6'"))
            print(f"-> Sucesso no Banco: Tabela alembic_version atualizada de '{result}' para '488a052bb9f6'.")
        else:
            conn.execute(text("INSERT INTO alembic_version (version_num) VALUES ('488a052bb9f6')"))
            print("-> Sucesso no Banco: Registro de versão '488a052bb9f6' inserido.")
        
        # Confirma as alterações fisicamente no Postgres
        conn.commit()
except Exception as e:
    print(f"-> Erro ao conectar ou atualizar o Banco de Dados: {e}")

# 3. Corrigindo arquivos de migração que possam estar apontando para o ID quebrado
# Procura pelas pastas de migrações padrão do projeto
possible_paths = [Path("alembic/versions"), Path("migrations/versions")]
versions_dir = None
for p in possible_paths:
    if p.exists():
        versions_dir = p
        break

if versions_dir:
    print(f"-> Analisando arquivos físicos em: {versions_dir}")
    arquivos_corrigidos = 0
    for file_path in versions_dir.glob("*.py"):
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()
        
        if "fe098d22551c" in content:
            print(f"   [!] Encontrada referência quebrada no arquivo: {file_path.name}")
            # Substitui a referência quebrada pelo ID correto da baseline
            new_content = content.replace("fe098d22551c", "488a052bb9f6")
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(new_content)
            print(f"   -> Sucesso: Referência corrigida para '488a052bb9f6'!")
            arquivos_corrigidos += 1
            
    if arquivos_corrigidos == 0:
        print("-> Nenhum arquivo físico com referência quebrada foi encontrado (o problema era apenas no banco).")
else:
    print("-> Alerta: Pasta de migrações não encontrada localmente.")

print("\n=== PROCESSO CONCLUÍDO COM SUCESSO! ===")
print("Agora você pode rodar: alembic upgrade head")
print("=======================================\n")