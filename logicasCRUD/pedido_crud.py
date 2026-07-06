from pymongo import MongoClient
from bson.objectid import ObjectId

class PedidoCRUD:
    def __init__(self):
        self.client = MongoClient("mongodb://localhost:27017/", serverSelectionTimeoutMS=2000)
        self.db = self.client["comerciotech"]
        self.coleccion = self.db["pedido"]

    def obtener_todo_pedido(self):
        """Recupera el historial completo de transacciones"""
        return list(self.coleccion.find())

    def filtrar_pedido_admin(self, estado=None, fecha=None):
        """Construye queries dinámicas para filtros simultáneos en la UI"""
        query = {}
        if estado and estado != "Todos":
            query["estado_pedido"] = estado
        if fecha:
            query["fecha_pedido"] = fecha.strip()
        return list(self.coleccion.find(query))

    def buscar_pedidos_por_cliente(self, rut_cliente):
        """Cruza información usando el RUT como clave foránea NoSQL"""
        return list(self.coleccion.find({"rut_cliente": rut_cliente.strip()}))

    def cambiar_estado_pedido(self, id_pedido, nuevo_estado):
        """Modifica de forma atómica el estado de una orden"""
        try:
            id_filtro = ObjectId(id_pedido) if len(str(id_pedido)) == 24 else id_pedido
            resultado = self.coleccion.update_one(
                {"_id": id_filtro},
                {"$set": {"estado_pedido": nuevo_estado}}
            )
            return resultado.modified_count > 0
        except Exception:
            return False

    def crear_pedido(self, datos_pedido):
        """Registra un nuevo carro de compras procesado"""
        return self.coleccion.insert_one(datos_pedido).inserted_id