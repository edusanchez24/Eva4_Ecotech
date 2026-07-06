from bson.objectid import ObjectId
from datetime import datetime

def crear_pedido(db, rut_cliente, items_carrito, direccion_entrega):
    """
    Crea un nuevo pedido, descuenta stock de forma atómica y actualiza el estado 
    del producto a 'sin stock' si este llega a 0.
    """
    # 1. Validar Stock de todos los productos primero
    for item in items_carrito:
        prod = db.productos.find_one({"_id": ObjectId(item['id_producto'])})
        if not prod or prod.get('stock', 0) < item['cantidad']:
            return False, f"Stock insuficiente para: {item['nombre_producto']}"

    # 2. Descontar Stock y construir subdocumentos de detalle
    total_pedido = 0
    detalle_final = []
    
    for item in items_carrito:
        id_p = ObjectId(item['id_producto'])
        
        # Decrementar stock de forma atómica
        db.productos.update_one(
            {"_id": id_p},
            {"$inc": {"stock": -item['cantidad']}}
        )
        
        # LOGICA AUTOMÁTICA DE ESTADO: Verificar si bajó a 0 o menos
        prod_verificar = db.productos.find_one({"_id": id_p})
        if prod_verificar and prod_verificar.get("stock", 0) <= 0:
            db.productos.update_one(
                {"_id": id_p},
                {"$set": {"estado": "sin stock", "stock": 0}}
            )
        
        subtotal = item['cantidad'] * item['precio_unitario']
        total_pedido += subtotal
        
        detalle_final.append({
            "id_producto": id_p,
            "nombre_producto": item['nombre_producto'],
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


def eliminar_pedido_cliente(db, id_pedido):
    """
    Elimina un pedido en estado 'Ingresado' y devuelve el stock completo a los productos,
    restableciendo su estado a 'disponible' si correspondiera.
    """
    try:
        pedido = db.pedidos.find_one({"_id": ObjectId(id_pedido)})
        if not pedido:
            return False, "Pedido no encontrado."
            
        if pedido.get("estado_pedido") != "Ingresado":
            return False, "Solo se pueden eliminar pedidos en estado 'Ingresado'."
            
        # Devolver stock de cada producto embebido en el detalle
        for item in pedido.get("detalle_productos", []):
            id_p = ObjectId(item["id_producto"])
            cant_devuelta = item["cantidad"]
            
            # Incrementar stock
            db.productos.update_one(
                {"_id": id_p},
                {"$inc": {"stock": cant_devuelta}}
            )
            
            # LÓGICA AUTOMÁTICA DE ESTADO: Si vuelve a tener stock, pasa a disponible
            prod_verificar = db.productos.find_one({"_id": id_p})
            if prod_verificar and prod_verificar.get("stock", 0) > 0:
                db.productos.update_one(
                    {"_id": id_p},
                    {"$set": {"estado": "disponible"}}
                )
                
        # Eliminar físicamente el documento de la colección
        db.pedidos.delete_one({"_id": ObjectId(id_pedido)})
        return True, "Pedido eliminado y stock restablecido con éxito."
    except Exception as e:
        return False, f"Error al eliminar: {str(e)}"