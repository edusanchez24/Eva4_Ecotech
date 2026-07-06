from pymongo import MongoClient
from bson.objectid import ObjectId

class ClienteCRUD:
    def __init__(self):
        # Conexión persistente local en Windows 11
        self.client = MongoClient("mongodb://localhost:27017/", serverSelectionTimeoutMS=2000)
        self.db = self.client["comerciotech"]
        self.coleccion = self.db["cliente"]

    def buscar_por_rut(self, rut_cliente):
        """Busca un único documento por su clave natural RUT"""
        return self.coleccion.find_one({"rut": rut_cliente.strip()})

    def obtener_todo_cliente(self):
        """Retorna todos los documentos de la colección cliente"""
        return list(self.coleccion.find())

    def crear_cliente(self, datos_cliente):
        """Inserta un nuevo documento estructurado en el motor"""
        return self.coleccion.insert_one(datos_cliente).inserted_id

    def actualizar_cliente(self, id_cliente, nuevos_datos):
        """Actualiza campos específicos mediante su _id de MongoDB"""
        id_filtro = ObjectId(id_cliente) if len(str(id_cliente)) == 24 else id_cliente
        resultado = self.coleccion.update_one({"_id": id_filtro}, {"$set": nuevos_datos})
        return resultado.modified_count > 0

    def eliminar_cliente(self, id_cliente):
        """Remueve permanentemente un registro de la base de datos"""
        id_filtro = ObjectId(id_cliente) if len(str(id_cliente)) == 24 else id_cliente
        resultado = self.coleccion.delete_one({"_id": id_filtro})
        return resultado.deleted_count > 0