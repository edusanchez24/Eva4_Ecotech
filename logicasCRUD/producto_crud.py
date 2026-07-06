from pymongo import MongoClient
from bson.objectid import ObjectId

class ProductoCRUD:
    def __init__(self):
        # Conexión nativa a MongoDB en Windows 11 (Puerto por defecto)
        self.client = MongoClient("mongodb://localhost:27017/", serverSelectionTimeoutMS=2000)
        self.db = self.client["comerciotech"]
        self.coleccion = self.db["producto"]

    def obtener_todo_producto(self):
        """Recupera el catálogo completo de productos activos en el sistema."""
        return list(self.coleccion.find())

    def buscar_por_id(self, id_producto):
        """Busca un producto específico mediante su clave NoSQL (_id)."""
        try:
            id_filtro = ObjectId(id_producto) if len(str(id_producto)) == 24 else id_producto
            return self.coleccion.find_one({"_id": id_filtro})
        except Exception:
            return None

    def buscar_por_codigo(self, codigo_prod):
        """Busca un producto por su código de barra interno o SKU (Clave natural)."""
        return self.coleccion.find_one({"codigo_producto": codigo_prod.strip()})

    def crear_producto(self, datos_producto):
        """Inserta un nuevo artículo en la colección singular 'producto'."""
        return self.coleccion.insert_one(datos_producto).inserted_id

    def actualizar_producto(self, id_producto, nuevos_datos):
        """Modifica características generales, precios o descripciones del producto."""
        try:
            id_filtro = ObjectId(id_producto) if len(str(id_producto)) == 24 else id_producto
            resultado = self.coleccion.update_one({"_id": id_filtro}, {"$set": nuevos_datos})
            return resultado.modified_count > 0
        except Exception:
            return False

    def eliminar_producto(self, id_producto):
        """Remueve físicamente un documento de producto del catálogo."""
        try:
            id_filtro = ObjectId(id_producto) if len(str(id_producto)) == 24 else id_producto
            resultado = self.coleccion.delete_one({"_id": id_filtro})
            return resultado.deleted_count > 0
        except Exception:
            return False

    def filtrar_por_categoria(self, categoria):
        """Filtra el catálogo según la clasificación del producto."""
        if not categoria or categoria == "Todas":
            return self.obtener_todo_producto()
        return list(self.coleccion.find({"categoria_producto": categoria.strip()}))

    def modificar_stock_atomico(self, id_producto, cantidad):
        """
        UTILIDAD CRÍTICA DE INTEGRIDAD: Resta o suma stock directamente en el motor NoSQL.
        Usa el operador '$inc' con valores negativos para descontar de forma segura,
        evitando que dos clientes compren el mismo artículo si no quedan existencias.
        """
        try:
            id_filtro = ObjectId(id_producto) if len(str(id_producto)) == 24 else id_producto
            
            # Si la cantidad es negativa (descuento), validamos que haya stock suficiente primero
            filtro = {"_id": id_filtro}
            if cantidad < 0:
                filtro["stock_producto"] = {"$gte": abs(cantidad)}
            
            resultado = self.coleccion.update_one(
                filtro,
                {"$inc": {"stock_producto": cantidad}}
            )
            return resultado.modified_count > 0
        except Exception:
            return False