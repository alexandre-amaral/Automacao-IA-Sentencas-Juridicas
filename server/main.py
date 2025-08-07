from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
import os

# Carrega variáveis de ambiente
load_dotenv()

# Inicializa a aplicação FastAPI
app = FastAPI(
    title="Sistema de Automação de Sentenças Judiciais",
    description="API para automatizar a geração de sentenças judiciais com IA",
    version="1.0.0"
)

# Configuração do CORS para permitir requisições do frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # URL do Next.js
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    """Endpoint raiz da API"""
    return {
        "message": "Sistema de Automação de Sentenças Judiciais",
        "status": "online",
        "version": "1.0.0"
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)