import os
from dotenv import load_dotenv

# Carrega as variáveis do .env IMEDIATAMENTE antes de importar outras coisas
load_dotenv() 
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

from api.routers.datasets import router as datasets_router

app = FastAPI(
    title="AI Dataset Factory",
    description="Pipeline de preparação de dados corporativos para IA (Fine Tuning & RAG)",
    version="1.0.0"
)

# Configuração de CORS para permitir que a API converse com outros domínios sem ser bloqueada
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Em produção, travaremos isso para os domínios específicos
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.include_router(datasets_router)

@app.get("/health", tags=["Health"])
def health_check():
    return {"status": "online", "message": "Motor ligado e rotas mapeadas."}

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)