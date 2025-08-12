from fastapi import FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware

from .database import get_user_collection
from .models import EduzzWebhookPayload, LoginRequest
from . import utils
from . import email_service

app = FastAPI(
    title="API Eduzz Webhook",
    description="API para processar webhooks de vendas da Eduzz e autenticar usuários.",
    version="1.2.0"
)

# Configuração do CORS para permitir requisições de outras origens (como a Eduzz)
origins = ["*"]  # Permite todas as origens

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

user_collection = get_user_collection()

@app.post("/eduzz/webhook")
async def eduzz_webhook(payload: EduzzWebhookPayload):
    """
    Endpoint para receber webhooks da Eduzz.
    Processa eventos de 'sale.approved', cria o usuário e envia e-mail de acesso.
    """
    try:
        if payload.event != "sale.approved":
            return {"status": "event_ignored", "event": payload.event}

        customer = payload.data.customer
        name = customer.name
        email = customer.email

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

        return {"status": "success"}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"status": "error", "message": str(e)}
        )

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

@app.get("/", include_in_schema=False)
def root():
    return {"message": "API Eduzz Webhook está no ar!"}