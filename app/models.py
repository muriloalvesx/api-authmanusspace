from pydantic import BaseModel, EmailStr, Field

# Removemos os modelos antigos e criamos um que corresponde
# à estrutura "plana" do webhook da Eduzz.
class EduzzWebhookPayload(BaseModel):
    event: str
    
    # Usamos 'Field(alias=...)' para mapear os campos do JSON da Eduzz
    # (com 'cus_') para nomes mais amigáveis em Python.
    customer_name: str = Field(..., alias='cus_name')
    customer_email: EmailStr = Field(..., alias='cus_email')


# O modelo de login não precisa de alterações.
class LoginRequest(BaseModel):
    email: EmailStr
    password: str