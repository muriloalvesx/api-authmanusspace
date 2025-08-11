from pydantic import BaseModel, EmailStr

# --- Modelos para o Webhook da Eduzz ---
# Valida a estrutura esperada do JSON do webhook
class EduzzCustomer(BaseModel):
    name: str
    email: EmailStr

class EduzzData(BaseModel):
    customer: EduzzCustomer

class EduzzWebhookPayload(BaseModel):
    event: str
    data: EduzzData

# --- Modelo para o Login ---
# Valida os dados recebidos no endpoint de login
class LoginRequest(BaseModel):
    email: EmailStr
    password: str