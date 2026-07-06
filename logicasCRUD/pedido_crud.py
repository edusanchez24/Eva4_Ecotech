from bson.objectid import ObjectId
from datetime import datetime

def crear_pedido(db, rut_cliente, items_carrito, direccion_entrega):
    """
    items_carrito: lista de dicts [{'id_producto': str, 'cantidad': int, 'precio_unitario': int, 'nombre': str}]
    """
    # 1. Validar Stock de todos los productos primero
    for item in items_carrito:
        prod = db.productos.find_one({"_id": ObjectId(item['id_producto'])})
        if not prod or prod['stock'] < item['cantidad']:
            return False, f"Stock insuficiente para: {item['nombre']}"

    # 2. Descontar Stock y construir subdocumentos de detalle
    total_pedido = 0
    detalle_final = []
    
    for item in items_carrito:
        # Decrementar stock de forma atómica en MongoDB
        db.productos.update_one(
            {"_id": ObjectId(item['id_producto'])},
            {"$inc": {"stock": -item['cantidad']}}
        )
        
        subtotal = item['cantidad'] * item['precio_unitario']
        total_pedido += subtotal
        
        detalle_final.append({
            "id_producto": ObjectId(item['id_producto']),
            "nombre_producto": item['nombre'],
            "cantidad": item['cantidad'],
            "precio_unitario": item['precio_unitario'],
            "subtotal": subtotal
        })

    # 3. Guardar el documento Pedido
    nuevo_pedido = {
        "id_cliente": rut_cliente,
        "fecha_pedido": datetime.now(),
        "estado_pedido": "Ingresado",
        "total_pedido": total_pedido,
        "direccion_entrega": direccion_entrega,
        "detalle_productos": detalle_final
    }
    
    db.pedidos.insert_one(nuevo_pedido)
    return True, "Pedido procesado y registrado con éxito."

def listar_pedidos_por_cliente(db, rut_cliente):
    return list(db.pedidos.find({"id_cliente": rut_cliente}))

def listar_todos_los_pedidos(db):
    return list(db.pedidos.find())

def actualizar_estado_pedido(db, id_pedido, nuevo_estado):
    """Permite al administrador cambiar el estado (Ingresado -> En Proceso -> Entregado)."""
    db.pedidos.update_one(
        {"_id": ObjectId(id_pedido)},
        {"$set": {"estado_pedido": nuevo_estado}}
    )
    return True