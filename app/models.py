# app/models.py (CORRIGIDO PARA O NOVO WEBHOOK)

from pydantic import BaseModel, EmailStr, Field

class EduzzWebhookPayload(BaseModel):
    # Alterado de 'event' para 'event_name' para corresponder à nova documentação
    event_name: str
    
    customer_name: str = Field(..., alias='cus_name')
    customer_email: EmailStr = Field(..., alias='cus_email')

class LoginRequest(BaseModel):
    email: EmailStr
    password: str