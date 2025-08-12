from fastapi import FastAPI, HTTPException, status, BackgroundTasks, Request, Response
from fastapi.middleware.cors import CORSMiddleware

from .database import get_user_collection
from .models import EduzzWebhookPayload, LoginRequest
from . import utils
from . import email_service

app = FastAPI(
    title="API Eduzz Webhook",
    description="API para processar webhooks de vendas da Eduzz e autenticar usuários.",
    version="2.0.2" # Versão Mais Robusta
)

# Configuração do CORS
origins = ["*"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

user_collection = get_user_collection()

async def process_sale_in_background(name: str, email: str):
    """Cria o usuário e envia o e-mail de boas-vindas."""
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
    """
    if payload.event not in ["sale.approved", "invoice_paid"]:
        return {"status": "event_ignored", "event": payload.event}
    
    background_tasks.add_task(
        process_sale_in_background, 
        payload.customer_name, 
        payload.customer_email
    )
    return {"status": "success - processing in background"}


@app.post("/auth/login")
async def auth_login(login_data: LoginRequest):
    """Endpoint para autenticação de usuários."""
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

# --- ENDPOINT RAIZ ATUALIZADO ---
# Agora ele aceita explicitamente GET e HEAD.
@app.api_route("/", methods=["GET", "HEAD"], include_in_schema=False)
def root(request: Request):
    if request.method == "HEAD":
        # Para requisições HEAD, retornamos apenas o status 200 OK sem corpo.
        return Response(status_code=status.HTTP_200_OK)
    # Para requisições GET, retornamos a mensagem normal.
    return {"message": "API Eduzz Webhook está no ar!"}