# app/email_service.py (VERSÃO COMPLETA E CORRIGIDA)

import os
import logging
import aiosmtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from dotenv import load_dotenv

# Carrega as variáveis de ambiente (essencial para o código funcionar)
load_dotenv()

# Configuração básica de logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# ---> ESTAS LINHAS SÃO ESSENCIAIS E PROVAVELMENTE ESTAVAM FALTANDO <---
# Elas pegam os dados do painel do Render e os colocam em variáveis Python.
SMTP_SERVER = os.getenv("SMTP_SERVER")
SMTP_PORT = int(os.getenv("SMTP_PORT", 465)) # Usando a porta 465 como padrão
SMTP_USERNAME = os.getenv("SMTP_USERNAME")
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD")
# ---> FIM DAS LINHAS ESSENCIAIS <---


async def send_access_email(name: str, email: str, password: str):
    """
    Monta e envia um e-mail com os dados de acesso para o comprador.
    Esta versão usa uma conexão TLS implícita, ideal para a porta 465.
    """
    # Esta verificação agora vai funcionar, pois as variáveis acima existem.
    if not all([SMTP_SERVER, SMTP_PORT, SMTP_USERNAME, SMTP_PASSWORD]):
        logging.error("Variáveis de ambiente SMTP não configuradas. O e-mail não será enviado.")
        return

    body = f"""
    <html>
    <body>
        <h2>Olá, {name}!</h2>
        <p>Sua compra foi aprovada com sucesso. Seja bem-vindo(a)!</p>
        <p>Aqui estão seus dados para acessar nossa plataforma:</p>
        <ul>
            <li><strong>Link de Acesso:</strong> <a href="https://usiggfuq.manus.space">https://usiggfuq.manus.space</a></li>
            <li><strong>Usuário:</strong> {email}</li>
            <li><strong>Senha:</strong> {password}</li>
        </ul>
        <p>Recomendamos que você altere sua senha no primeiro acesso.</p>
        <p>Atenciosamente,<br>Equipe Fresley.</p>
    </body>
    </html>
    """
    msg = MIMEMultipart()
    msg['From'] = SMTP_USERNAME
    msg['To'] = email
    msg['Subject'] = "Seus dados de acesso"
    msg.attach(MIMEText(body, 'html'))

    try:
        async with aiosmtplib.SMTP(hostname=SMTP_SERVER, port=SMTP_PORT, use_tls=True) as server:
            await server.login(SMTP_USERNAME, SMTP_PASSWORD)
            await server.send_message(msg)
        
        logging.info(f"E-mail de acesso enviado com sucesso para: {email}")

    except Exception as e:
        logging.error(f"Falha ao enviar e-mail para {email}: {e}")