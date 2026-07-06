import os
import urllib.parse
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure, ConfigurationError
from dotenv import load_dotenv

load_dotenv()

def obtener_db():
    """
    Gestiona la conexión parametrizada a MongoDB Atlas.
    Retorna el objeto de la base de datos si la conexión es exitosa.
    """
    user = os.getenv("MONGODB_USER")
    password = os.getenv("MONGODB_PASS")
    host = os.getenv("MONGODB_HOST")
    db_name = os.getenv("MONGODB_DB")

    if not all([user, password, host, db_name]):
        print("Error: Faltan variables de entorno. Verifica tu archivo .env.")
        return None
    
    #Codificar credenciales (seguridad para caracteres especiales)
    user_enc = urllib.parse.quote_plus(user)
    pass_enc = urllib.parse.quote_plus(password)

    # 3. Construir el string de conexión dinámico
    uri = f"mongodb+srv://{user_enc}:{pass_enc}@{host}/{db_name}?retryWrites=true&w=majority"

    try:
        client = MongoClient(uri, serverSelectionTimeoutMS=5000)
        # Forzar una prueba de conexión (ping)
        client.admin.command('ping')
        print(f"Conexión modular exitosa a la base de datos: {db_name}")
        return client[db_name]
    except Exception as e:
        print(f"Error al conectar a MongoDB: {e}")
        return None

# Bloque de prueba
if __name__ == "__main__":
    db = obtener_db()
    if db is not None:
        print("Módulo de conexión verificado y listo.") 