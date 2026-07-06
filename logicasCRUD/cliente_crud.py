from bson.objectid import ObjectId

def registrar_cliente(db, rut, nombre, correo, telefono, direccion_inicial=None):
    """Registra un nuevo cliente con un arreglo de direcciones embebido."""
    if db.clientes.find_one({"rut": rut}):
        return False, "El RUT ya se encuentra registrado."
        
    direcciones = []
    if direccion_inicial:
        direccion_inicial["principal"] = True
        direcciones.append(direccion_inicial)
        
    nuevo_cliente = {
        "rut": rut,
        "nombre": nombre,
        "correo": correo,
        "telefono": telefono,
        "estado": "activo",
        "direcciones": direcciones
    }
    
    db.clientes.insert_one(nuevo_cliente)
    return True, "Cliente registrado exitosamente."

def buscar_cliente_por_rut(db, rut):
    """Busca un cliente específico por su RUT."""
    return db.clientes.find_one({"rut": rut})

def agregar_direccion_cliente(db, rut, nueva_direccion):
    """Agrega una nueva dirección al arreglo embebido del cliente."""
    nueva_direccion["principal"] = False
    resultado = db.clientes.update_one(
        {"rut": rut},
        {"$push": {"direcciones": nueva_direccion}}
    )
    return resultado.modified_count > 0