from bson.objectid import ObjectId

def crear_producto(db, nombre, categoria, precio, stock):
    """Inserta un nuevo producto al catálogo."""
    producto = {
        "nombre_producto": nombre,
        "categoria": category,
        "precio_unitario": int(precio),
        "stock": int(stock),
        "estado": "disponible"
    }
    db.productos.insert_one(producto)
    return True, "Producto creado correctamente."

def listar_productos_disponibles(db):
    """Retorna todos los productos con stock mayor a cero."""
    return list(db.productos.find({"stock": {"$gt": 0}}))

def buscar_productos_por_nombre(db, texto_busqueda):
    """Búsqueda parcial e insensible a mayúsculas para cumplir con los filtros."""
    query = {"nombre_producto": {"$regex": texto_busqueda, "$options": "i"}}
    return list(db.productos.find(query))

def actualizar_stock(db, id_producto, cantidad_cambio):
    """Incrementa o decrementa el stock de forma atómica."""
    db.productos.update_one(
        {"_id": ObjectId(id_producto)},
        {"$inc": {"stock": cantidad_cambio}}
    )