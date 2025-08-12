from fastapi import FastAPI, HTTPException, status, BackgroundTasks, Request, Response
from fastapi.middleware.cors import CORSMiddleware
import logging # Importando logging para mensagens informativas

from .database import get_user_collection
from .models import EduzzWebhookPayload, LoginRequest
from . import utils
from . import email_service

app = FastAPI(
    title="API Eduzz Webhook",
    description="API para processar webhooks de vendas da Eduzz e autenticar usuários.",
    version="2.1.0" # Versão Idempotente
)

# ... (código do CORS e da instância do app continua igual) ...
origins = ["*"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

user_collection = get_user_collection()

# --- FUNÇÃO DE BACKGROUND ATUALIZADA ---
async def process_sale_in_background(name: str, email: str):
    """
    Cria o usuário e envia e-mail, mas ANTES verifica se o usuário já existe.
    """
    # VERIFICAÇÃO DE IDEMPOTÊNCIA: O usuário já existe?
    existing_user = await user_collection.find_one({"email": email})
    if existing_user:
        logging.info(f"Usuário com e-mail {email} já existe. Ignorando a criação duplicada.")
        return  # Para a execução aqui se o usuário já foi criado.

    # Se o código continuar, significa que o usuário é novo.
    random_password = utils.generate_random_password()
    hashed_password = utils.hash_password(random_password)
    
    user_document = {
        "name": name,
        "email": email,
        "password": hashed_password
    }

    await user_collection.insert_one(user_document)

    await email_service.send_access_email(
        name=name, 
        email=email, 
        password=random_password
    )

@app.post("/eduzz/webhook")
async def eduzz_webhook(payload: EduzzWebhookPayload, background_tasks: BackgroundTasks):
    """
    Recebe o webhook, responde imediatamente e processa a venda em segundo plano.
    Atualizado para a nova estrutura de webhooks da Eduzz (usando event_name).
    """
    # Verificando o campo 'event_name' e o valor 'invoice_paid'
    if payload.event_name != "invoice_paid":
        return {"status": "event_ignored", "event": payload.event_name}
    
    background_tasks.add_task(
        process_sale_in_background, 
        payload.customer_name, 
        payload.customer_email
    )
    
    return {"status": "success - processing in background"}

# ... (o resto do código, como /auth/login, continua o mesmo) ...
@app.post("/auth/login")
async def auth_login(login_data: LoginRequest):
    try:
        user = await user_collection.find_one({"email": login_data.email})
        if not user or not utils.verify_password(login_data.password, user["password"]):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail={"status": "invalid_credentials"}
            )
        return {"status": "success"}
    except HTTPException as http_exc:
        raise http_exc
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"status": "error", "message": str(e)}
        )

@app.api_route("/", methods=["GET", "HEAD"], include_in_schema=False)
def root(request: Request):
    if request.method == "HEAD":
        return Response(status_code=status.HTTP_200_OK)
    return {"message": "API Eduzz Webhook está no ar!"}