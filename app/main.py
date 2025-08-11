from fastapi import FastAPI, HTTPException, status
from .database import get_user_collection
from .models import EduzzWebhookPayload, LoginRequest
from . import utils
from . import email_service  # <--- 1. Importar o novo serviço de e-mail

app = FastAPI(
    title="API Eduzz Webhook",
    description="API para processar webhooks de vendas da Eduzz e autenticar usuários.",
    version="1.1.0"
)

user_collection = get_user_collection()

@app.post("/eduzz/webhook")
async def eduzz_webhook(payload: EduzzWebhookPayload):
    try:
        if payload.event != "sale.approved":
            return {"status": "event_ignored", "event": payload.event}

        customer = payload.data.customer
        name = customer.name
        email = customer.email

        # Gera a senha em texto plano (não criptografada)
        random_password = utils.generate_random_password()
        
        # Criptografa a senha para salvar no banco
        hashed_password = utils.hash_password(random_password)
        
        user_document = {
            "name": name,
            "email": email,
            "password": hashed_password
        }

        await user_collection.insert_one(user_document)

        # --- 2. ENVIAR E-MAIL PARA O COMPRADOR ---
        # A função é chamada com a senha em texto plano (random_password).
        # O 'await' garante que a tarefa seja executada de forma assíncrona.
        # A função email_service trata os próprios erros, então não precisamos
        # de um try/except aqui. O fluxo da API continuará normalmente.
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

# O endpoint /auth/login continua o mesmo, sem alterações.
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

@app.get("/", include_in_schema=False)
def root():
    return {"message": "API Eduzz Webhook está no ar!"}