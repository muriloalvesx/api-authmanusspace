# app/main.py (com a correção do CORS)

from fastapi import FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware  # <--- 1. IMPORTE O MIDDLEWARE

from .database import get_user_collection
from .models import EduzzWebhookPayload, LoginRequest
from . import utils
from . import email_service

app = FastAPI(
    title="API Eduzz Webhook",
    description="API para processar webhooks de vendas da Eduzz e autenticar usuários.",
    version="1.2.0" # Atualizei a versão para refletir a mudança
)

# --- 2. ADICIONE O CÓDIGO DO CORS AQUI ---
# Este código permite que outros domínios (como o da Eduzz) acessem sua API.
origins = ["*"]  # Para testes, permitir todas as origens é aceitável.

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"], # Permitir todos os métodos (GET, POST, etc.)
    allow_headers=["*"], # Permitir todos os cabeçalhos
)
# --- FIM DO CÓDIGO DO CORS ---


# O resto do seu código continua igual...
@app.post("/eduzz/webhook")
async def eduzz_webhook(payload: EduzzWebhookPayload):
    # ... (seu código aqui)
    pass

@app.post("/auth/login")
async def auth_login(login_data: LoginRequest):
    # ... (seu código aqui)
    pass

@app.get("/", include_in_schema=False)
def root():
    return {"message": "API Eduzz Webhook está no ar!"}