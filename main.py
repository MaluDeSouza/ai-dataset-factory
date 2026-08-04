from fastapi import FastAPI
import uvicorn

app = FastAPI(
    title="AI Dataset Factory",
    description="Pipeline de preparação de dados corporativos para IA (Fine Tuning & RAG)",
    version="1.0.0"
)

@app.get("/health")
def health_check():
    return {"status": "online", "message": "Motor ligado."}

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)