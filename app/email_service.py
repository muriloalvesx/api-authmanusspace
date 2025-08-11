import os
import logging
import aiosmtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from dotenv import load_dotenv

# Carrega as variáveis de ambiente
load_dotenv()

# Configuração básica de logging para vermos os logs no console
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Carrega as configurações de SMTP do arquivo .env
SMTP_SERVER = os.getenv("SMTP_SERVER")
SMTP_PORT = int(os.getenv("SMTP_PORT", 587))
SMTP_USERNAME = os.getenv("SMTP_USERNAME")
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD")

async def send_access_email(name: str, email: str, password: str):
    """
    Monta e envia um e-mail com os dados de acesso para o comprador.

    Esta função é assíncrona e não levanta exceções para o chamador,
    apenas registra o resultado (sucesso ou falha) no log.
    """
    if not all([SMTP_SERVER, SMTP_PORT, SMTP_USERNAME, SMTP_PASSWORD]):
        logging.error("Variáveis de ambiente SMTP não configuradas. O e-mail não será enviado.")
        return

    # Corpo do e-mail em formato HTML
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
        <p>Atenciosamente,<br>Equipe Eduzz</p>
    </body>
    </html>
    """

    # Criação do objeto do e-mail
    msg = MIMEMultipart()
    msg['From'] = SMTP_USERNAME
    msg['To'] = email
    msg['Subject'] = "Seus dados de acesso"
    msg.attach(MIMEText(body, 'html'))

    try:
        # Conexão e envio do e-mail de forma assíncrona
        async with aiosmtplib.SMTP(hostname=SMTP_SERVER, port=SMTP_PORT, use_tls=False) as server:
            await server.starttls()
            await server.login(SMTP_USERNAME, SMTP_PASSWORD)
            await server.send_message(msg)
        
        # Confirmação de que o e-mail foi enviado com sucesso
        logging.info(f"E-mail de acesso enviado com sucesso para: {email}")

    except Exception as e:
        # Se o envio falhar, o erro é registrado, mas a API não para.
        logging.error(f"Falha ao enviar e-mail para {email}: {e}")