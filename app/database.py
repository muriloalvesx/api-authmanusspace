import os
from dotenv import load_dotenv
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorCollection

# Carrega as variáveis de ambiente do arquivo .env
load_dotenv()

MONGO_URL = os.getenv("MONGO_URL")
if not MONGO_URL:
    raise ValueError("A variável de ambiente MONGO_URL não foi definida.")

# --- Conexão com o banco MongoDB ---
# O cliente é criado uma vez e reutilizado em toda a aplicação
# para otimizar o número de conexões.
client = AsyncIOMotorClient(MONGO_URL)
database = client.eduzz
user_collection: AsyncIOMotorCollection = database.users

def get_user_collection() -> AsyncIOMotorCollection:
    """Retorna a coleção de usuários do MongoDB."""
    return user_collection