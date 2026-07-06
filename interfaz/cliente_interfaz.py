import tkinter as tk
from tkinter import messagebox, ttk
from bson.objectid import ObjectId
from datetime import datetime
from logicasCRUD.cliente_crud import registrar_cliente, buscar_cliente_por_rut
from logicasCRUD.producto_crud import listar_productos_disponibles, buscar_productos_por_nombre
from logicasCRUD.pedido_crud import crear_pedido, listar_pedidos_por_cliente, eliminar_pedido_cliente

class VentanaCliente:
    def __init__(self, root, db, rut_cliente):
        self.root = root
        self.db = db
        self.rut_cliente = rut_cliente
        self.carrito_actual = [] # Guarda los productos del pedido en construcción (Módulo 3)
        
        self.root.title(f"EcoTech - Panel de Cliente ({self.rut_cliente})")
        self.root.geometry("850x600")
        
        # Control de Pestañas para los 3 Módulos
        self.tab_control = ttk.Notebook(root)
        
        self.tab_perfil = ttk.Frame(self.tab_control)
        self.tab_catalogo = ttk.Frame(self.tab_control)
        self.tab_gestion_pedidos = ttk.Frame(self.tab_control)
        
        self.tab_control.add(self.tab_perfil, text="Módulo 1: Mi Perfil e Historial")
        self.tab_control.add(self.tab_catalogo, text="Módulo 2: Catálogo y Búsqueda")
        self.tab_control.add(self.tab_gestion_pedidos, text="Módulo 3: Gestión de Pedidos")
        
        self.tab_control.pack(expand=1, fill="both")
        
        # Inicializar las interfaces de cada módulo
        self.crear_modulo_1_perfil()
        self.crear_modulo_2_catalogo()
        self.crear_modulo_3_pedidos()

    # =========================================================================
    # MÓDULO 1: GESTIÓN DE PERFIL E HISTORIAL
    # =========================================================================
    def crear_modulo_1_perfil(self):
        tk.Label(self.tab_perfil, text="Mis Datos Personales", font=("Arial", 12, "bold")).pack(pady=10)
        
        frame_datos = tk.Frame(self.tab_perfil)
        frame_datos.pack(pady=5)
        
        tk.Label(frame_datos, text="Nombre:").grid(row=0, column=0, padx=5, pady=5, sticky="e")
        self.ent_nom = tk.Entry(frame_datos, width=30)
        self.ent_nom.grid(row=0, column=1, padx=5, pady=5)
        
        tk.Label(frame_datos, text="Correo:").grid(row=1, column=0, padx=5, pady=5, sticky="e")
        self.ent_cor = tk.Entry(frame_datos, width=30)
        self.ent_cor.grid(row=1, column=1, padx=5, pady=5)
        
        tk.Label(frame_datos, text="Teléfono:").grid(row=2, column=0, padx=5, pady=5, sticky="e")
        self.ent_tel = tk.Entry(frame_datos, width=30)
        self.ent_tel.grid(row=2, column=1, padx=5, pady=5)
        
        frame_btn_perfil = tk.Frame(self.tab_perfil)
        frame_btn_perfil.pack(pady=10)
        
        tk.Button(frame_btn_perfil, text="Registrar / Guardar Datos", bg="#4CAF50", fg="white", command=self.guardar_perfil).pack(side="left", padx=5)
        tk.Button(frame_btn_perfil, text="Consultar / Cargar Mis Datos", bg="#2196F3", fg="white", command=self.cargar_perfil).pack(side="left", padx=5)
        
        tk.Label(self.tab_perfil, text="Historial General de Pedidos", font=("Arial", 11, "bold")).pack(pady=10)
        self.tabla_historial = ttk.Treeview(self.tab_perfil, columns=("ID", "Fecha", "Total", "Estado"), show="headings", height=6)
        self.tabla_historial.heading("ID", text="ID Pedido")
        self.tabla_historial.heading("Fecha", text="Fecha")
        self.tabla_historial.heading("Total", text="Total")
        self.tabla_historial.heading("Estado", text="Estado")
        self.tabla_historial.pack(fill="x", padx=20)
        
        self.cargar_perfil()

    def guardar_perfil(self):
        # Registra, actualiza o modifica los datos del cliente mediante upsert
        nombre = self.ent_nom.get().strip()
        correo = self.ent_cor.get().strip()
        telefono = self.ent_tel.get().strip()
        
        if not all([nombre, correo, telefono]):
            messagebox.showwarning("Atención", "Complete todos los campos de perfil.")
            return
            
        self.db.clientes.update_one(
            {"rut": self.rut_cliente},
            {"$set": {"nombre": nombre, "correo": correo, "telefono": telefono, "estado": "activo"}},
            upsert=True
        )
        messagebox.showinfo("Éxito", "Perfil guardado/actualizado de manera correcta.")
        self.cargar_historial_pedidos()

    def cargar_perfil(self):
        cliente = self.db.clientes.find_one({"rut": self.rut_cliente})
        if cliente:
            self.ent_nom.delete(0, tk.END); self.ent_nom.insert(0, cliente.get("nombre", ""))
            self.ent_cor.delete(0, tk.END); self.ent_cor.insert(0, cliente.get("correo", ""))
            self.ent_tel.delete(0, tk.END); self.ent_tel.insert(0, cliente.get("telefono", ""))
        self.cargar_historial_pedidos()

    def cargar_historial_pedidos(self):
        self.tabla_historial.delete(*self.tabla_historial.get_children())
        pedidos = list(self.db.pedidos.find({"id_cliente": self.rut_cliente}))
        for ped in pedidos:
            fecha_str = ped["fecha_pedido"].strftime("%Y-%m-%d %H:%M") if "fecha_pedido" in ped else "N/A"
            self.tabla_historial.insert("", "end", values=(str(ped["_id"]), fecha_str, f"${ped.get('total_pedido', 0)}", ped.get("estado_pedido", "Ingresado")))

    # =========================================================================
    # MÓDULO 2: CATÁLOGO, BÚSQUEDA Y DETALLE
    # =========================================================================
    def crear_modulo_2_catalogo(self):
        tk.Label(self.tab_catalogo, text="Catálogo Avanzado de Productos", font=("Arial", 12, "bold")).pack(pady=10)
        
        frame_busqueda = tk.Frame(self.tab_catalogo)
        frame_busqueda.pack(pady=5, fill="x", padx=20)
        
        tk.Label(frame_busqueda, text="Filtrar por (Nombre/Categoría/Marca):").pack(side="left", padx=5)
        self.ent_buscar_cat = tk.Entry(frame_busqueda, width=30)
        self.ent_buscar_cat.pack(side="left", padx=5)
        
        tk.Button(frame_busqueda, text="Buscar", bg="#2196F3", fg="white", command=self.buscar_productos).pack(side="left", padx=5)
        tk.Button(frame_busqueda, text="Restablecer", command=self.restablecer_catalogo).pack(side="left", padx=5)
        
        self.tabla_productos = ttk.Treeview(self.tab_catalogo, columns=("ID", "Nombre", "Categoria", "Precio", "Stock"), show="headings", height=10)
        self.tabla_productos.heading("ID", text="ID")
        self.tabla_productos.heading("Nombre", text="Nombre")
        self.tabla_productos.heading("Categoria", text="Categoría")
        self.tabla_productos.heading("Precio", text="Precio")
        self.tabla_productos.heading("Stock", text="Stock")
        self.tabla_productos.pack(fill="both", expand=True, padx=20, pady=10)
        
        frame_acciones_cat = tk.Frame(self.tab_catalogo)
        frame_acciones_cat.pack(pady=10)
        
        tk.Button(frame_acciones_cat, text="Ver Detalle Extendido", bg="#9C27B0", fg="white", command=self.consultar_detalle_producto).pack(side="left", padx=10)
        tk.Button(frame_acciones_cat, text="Añadir a mi Orden (Valida Stock)", bg="#FF9800", fg="white", command=self.pre_anadir_producto).pack(side="left", padx=10)
        
        self.restablecer_catalogo()

    def buscar_productos(self):
        termino = self.ent_buscar_cat.get().strip()
        self.tabla_productos.delete(*self.tabla_productos.get_children())
        # Filtro multi-campo usando el operador OR de MongoDB
        query = {
            "stock": {"$gt": 0},
            "$or": [
                {"nombre_producto": {"$regex": termino, "$options": "i"}},
                {"categoria": {"$regex": termino, "$options": "i"}},
                {"marca": {"$regex": termino, "$options": "i"}}
            ]
        }
        for p in self.db.productos.find(query):
            self.tabla_productos.insert("", "end", values=(str(p["_id"]), p.get("nombre_producto"), p.get("categoria", "General"), p.get("precio_unitario"), p.get("stock")))

    def restablecer_catalogo(self):
        self.ent_buscar_cat.delete(0, tk.END)
        self.tabla_productos.delete(*self.tabla_productos.get_children())
        for p in self.db.productos.find({"stock": {"$gt": 0}}):
            self.tabla_productos.insert("", "end", values=(str(p["_id"]), p.get("nombre_producto"), p.get("categoria", "General"), p.get("precio_unitario"), p.get("stock")))

    def consultar_detalle_producto(self):
        sel = self.tabla_productos.selection()
        if not sel:
            messagebox.showwarning("Atención", "Seleccione un producto del catálogo.")
            return
        id_p = self.tabla_productos.item(sel)['values'][0]
        p = self.db.productos.find_one({"_id": ObjectId(id_p)})
        
        detalle = f"ID: {p['_id']}\nNombre: {p['nombre_producto']}\nCategoría: {p.get('categoria','N/A')}\nMarca: {p.get('marca','N/A')}\nPrecio: ${p['precio_unitario']}\nStock Disponible: {p['stock']}\nDescripción: {p.get('descripcion','Sin descripción adicional.')}"
        messagebox.showinfo("Detalle de Producto", detalle)

    def pre_anadir_producto(self):
        sel = self.tabla_productos.selection()
        if not sel:
            messagebox.showwarning("Atención", "Seleccione un producto para añadir.")
            return
        valores = self.tabla_productos.item(sel)['values']
        id_p, nombre, precio, stock_disp = valores[0], valores[1], int(valores[3]), int(valores[4])
        
        # VALIDACIÓN REQUERIDA: Verificar stock antes de añadir al pedido
        if stock_disp <= 0:
            messagebox.showerror("Sin Unidades", "No queda stock disponible de este producto.")
            return
            
        # Comprobar si ya está en el pedido simulado para no sobrepasar el stock
        cant_ya_en_carrito = sum(item['cantidad'] for item in self.carrito_actual if item['id_producto'] == id_p)
        if cant_ya_en_carrito + 1 > stock_disp:
            messagebox.showerror("Límite de Stock", "No puedes añadir más unidades de las disponibles en el stock actual.")
            return
            
        self.carrito_actual.append({
            "id_producto": id_p,
            "nombre_producto": nombre,
            "precio_unitario": precio,
            "cantidad": 1
        })
        messagebox.showinfo("Añadido", f"Se agregó 1 unidad de '{nombre}' al borrador de tu pedido (Módulo 3).")
        self.actualizar_vista_carrito()

    # =========================================================================
    # MÓDULO 3: OPERACIONES DE PEDIDOS (CREAR, CALCULAR, MODIFICAR, ELIMINAR)
    # =========================================================================
    def crear_modulo_3_pedidos(self):
        tk.Label(self.get_tab_pedidos_frame(), text="Borrador del Nuevo Pedido Actual", font=("Arial", 11, "bold")).pack(pady=5)
        
        self.tabla_carrito = ttk.Treeview(self.get_tab_pedidos_frame(), columns=("Nombre", "Precio Unitario", "Cantidad", "Subtotal"), show="headings", height=4)
        self.tabla_carrito.heading("Nombre", text="Producto")
        self.tabla_carrito.heading("Precio Unitario", text="Precio Unitario")
        self.tabla_carrito.heading("Cantidad", text="Cantidad")
        self.tabla_carrito.heading("Subtotal", text="Subtotal por Producto")
        self.tabla_carrito.pack(fill="x", padx=20)
        
        self.lbl_total_pedido = tk.Label(self.get_tab_pedidos_frame(), text="TOTAL DE LA ORDEN: $0", font=("Arial", 12, "bold"), fg="darkgreen")
        self.lbl_total_pedido.pack(pady=5)
        
        frame_confirmar = tk.Frame(self.get_tab_pedidos_frame())
        frame_confirmar.pack(pady=5)
        tk.Button(frame_confirmar, text="Confirmar y Crear Pedido", bg="#4CAF50", fg="white", command=self.confirmar_nuevo_pedido).pack(side="left", padx=5)
        tk.Button(frame_confirmar, text="Vaciar Borrador", bg="#f44336", fg="white", command=self.vaciar_borrador).pack(side="left", padx=5)
        
        tk.Frame(self.get_tab_pedidos_frame(), height=2, bd=1, relief="sunken").pack(fill="x", padx=10, pady=10)
        
        # Sección de Buscar, Modificar y Eliminar Pedidos Propios
        tk.Label(self.get_tab_pedidos_frame(), text="Buscar y Gestionar Mis Pedidos Guardados", font=("Arial", 11, "bold")).pack()
        
        frame_busqueda_p = tk.Frame(self.get_tab_pedidos_frame())
        frame_busqueda_p.pack(pady=5)
        tk.Label(frame_busqueda_p, text="Filtrar ID Pedido (Vacío para todos):").pack(side="left")
        self.ent_buscar_id_p = tk.Entry(frame_busqueda_p, width=25)
        self.ent_buscar_id_p.pack(side="left", padx=5)
        tk.Button(frame_busqueda_p, text="Buscar Pedidos", command=self.buscar_mis_pedidos).pack(side="left")
        
        self.tabla_gestion_p = ttk.Treeview(self.get_tab_pedidos_frame(), columns=("ID", "Fecha", "Total", "Estado"), show="headings", height=5)
        self.tabla_gestion_p.heading("ID", text="ID Pedido")
        self.tabla_gestion_p.heading("Fecha", text="Fecha")
        self.tabla_gestion_p.heading("Total", text="Total")
        self.tabla_gestion_p.heading("Estado", text="Estado de la Orden")
        self.tabla_gestion_p.pack(fill="x", padx=20, pady=5)
        
        frame_crud_pedidos = tk.Frame(self.get_tab_pedidos_frame())
        frame_crud_pedidos.pack(pady=10)
        tk.Button(frame_crud_pedidos, text="Modificar Cantidades (Solo Ingresado)", bg="#FF9800", fg="white", command=self.modificar_pedido_ingresado).pack(side="left", padx=10)
        tk.Button(frame_crud_pedidos, text="Eliminar Pedido (Solo Ingresado)", bg="#f44336", fg="white", command=self.eliminar_pedido_ingresado).pack(side="left", padx=10)
        
        self.buscar_mis_pedidos()

    def get_tab_pedidos_frame(self):
        return self.tab_gestion_pedidos

    def actualizar_vista_carrito(self):
        self.tabla_carrito.delete(*self.tabla_carrito.get_children())
        total = 0
        for item in self.carrito_actual:
            subtotal = item["precio_unitario"] * item["cantidad"]
            total += subtotal
            self.tabla_carrito.insert("", "end", values=(item["nombre_producto"], f"${item['precio_unitario']}", item["cantidad"], f"${subtotal}"))
        self.lbl_total_pedido.config(text=f"TOTAL DE LA ORDEN: ${total}")

    def vaciar_borrador(self):
        self.carrito_actual = []
        self.actualizar_vista_carrito()

    def confirmar_nuevo_pedido(self):
        if not self.carrito_actual:
            messagebox.showwarning("Borrador Vacío", "No has agregado productos a tu orden desde el Catálogo.")
            return
            
        direccion_simulada = {"calle": "Av. Diagonal Ecoeficiente", "comuna": "Santiago"}
        exito, msg = crear_pedido(self.db, self.rut_cliente, self.carrito_actual, direccion_simulada)
        if exito:
            messagebox.showinfo("Orden Creada", "¡Tu nuevo pedido ha sido confirmado e ingresado al sistema NoSQL!")
            self.vaciar_borrador()
            self.restablecer_catalogo()
            self.buscar_mis_pedidos()
            self.cargar_historial_pedidos()
        else:
            messagebox.showerror("Error", msg)

    def buscar_mis_pedidos(self):
        filtro_id = self.ent_buscar_id_p.get().strip()
        self.tabla_gestion_p.delete(*self.tabla_gestion_p.get_children())
        
        query = {"id_cliente": self.rut_cliente}
        if filtro_id:
            try:
                query["_id"] = ObjectId(filtro_id)
            except:
                messagebox.showerror("Error", "ID de pedido no tiene un formato válido de MongoDB ObjectId.")
                return
                
        for ped in self.db.pedidos.find(query):
            fecha_str = ped["fecha_pedido"].strftime("%Y-%m-%d %H:%M") if "fecha_pedido" in ped else "N/A"
            self.tabla_gestion_p.insert("", "end", values=(str(ped["_id"]), fecha_str, f"${ped.get('total_pedido',0)}", ped.get("estado_pedido", "Ingresado")))

    def modificar_pedido_ingresado(self):
        sel = self.tabla_gestion_p.selection()
        if not sel:
            messagebox.showwarning("Atención", "Seleccione una orden para modificar.")
            return
        valores = self.tabla_gestion_p.item(sel)['values']
        id_ped, estado = valores[0], valores[3]
        
        # REGLA DE NEGOCIO OBLIGATORIA: Solo en estado 'Ingresado'
        if estado != "Ingresado":
            messagebox.showerror("Denegado", f"Los pedidos en estado '{estado}' NO pueden ser modificados por el cliente.")
            return
            
        # Obtener el estado actual del pedido desde MongoDB
        pedido = self.db.pedidos.find_one({"_id": ObjectId(id_ped)})
        if not pedido:
            messagebox.showerror("Error", "No se encontró el pedido en la base de datos.")
            return

        # --- VENTANA EMERGENTE PARA EDITAR CANTIDADES ---
        ventana_edit = tk.Toplevel(self.root)
        ventana_edit.title(f"Modificar Cantidades - Pedido {id_ped[:8]}...")
        ventana_edit.geometry("450x350")
        ventana_edit.grab_set() # Bloquea la ventana principal mientras esta esté abierta
        
        tk.Label(ventana_edit, text="Modificar Cantidades del Pedido", font=("Arial", 11, "bold")).pack(pady=10)
        
        # Contenedor para las líneas de productos
        frame_lineas = tk.Frame(ventana_edit)
        frame_lineas.pack(pady=10, fill="both", expand=True, padx=20)
        
        # Diccionario para almacenar las cajas de texto de las nuevas cantidades
        entradas_cantidades = {}
        
        # Crear dinámicamente un label y un entry por cada producto en el subdocumento embebido
        for i, item in enumerate(pedido.get("detalle_productos", [])):
            id_prod_str = str(item["id_producto"])
            
            lbl_prod = tk.Label(frame_lineas, text=f"{item['nombre_producto']} (Actual: {item['cantidad']}):", font=("Arial", 10))
            lbl_prod.grid(row=i, column=0, sticky="w", pady=5, padx=5)
            
            ent_cant = tk.Entry(frame_lineas, width=8, justify="center")
            ent_cant.grid(row=i, column=1, pady=5, padx=5)
            ent_cant.insert(0, str(item["cantidad"])) # Dejar la cantidad actual por defecto
            
            # Guardamos la referencia indexada por el ID del producto
            entradas_cantidades[id_prod_str] = {
                "entry": ent_cant,
                "cantidad_anterior": item["cantidad"],
                "precio_unitario": item["precio_unitario"],
                "nombre_producto": item["nombre_producto"]
            }
            
        def guardar_cambios_cantidades():
            nuevas_lineas = []
            nuevo_total_pedido = 0
            
            # 1. Validar primero que todas las entradas sean números válidos y comprobar stock
            for id_prod_str, datos in entradas_cantidades.items():
                try:
                    nueva_cant = int(datos["entry"].get().strip())
                    if nueva_cant < 0:
                        raise ValueError()
                except ValueError:
                    messagebox.showerror("Error", f"La cantidad para {datos['nombre_producto']} debe ser un número entero mayor o igual a 0.")
                    return
                
                # Si la cantidad cambia, calcular la diferencia para ajustar el stock en la BD
                diferencia = nueva_cant - datos["cantidad_anterior"]
                
                if diferencia > 0:
                    # Validar si hay stock suficiente en la colección de productos para el aumento
                    prod_db = self.db.productos.find_one({"_id": ObjectId(id_prod_str)})
                    if not prod_db or prod_db.get("stock", 0) < diferencia:
                        messagebox.showerror("Stock Insuficiente", f"No hay suficiente stock para aumentar {datos['nombre_producto']}. Disponible extra: {prod_db.get('stock', 0)}")
                        return
                
                # Guardar temporalmente los datos validados para el update
                if nueva_cant > 0: # Si es 0, simplemente no se añade al detalle recalculado
                    subtotal = nueva_cant * datos["precio_unitario"]
                    nuevo_total_pedido += subtotal
                    nuevas_lineas.append({
                        "id_producto": ObjectId(id_prod_str),
                        "nombre_producto": datos["nombre_producto"],
                        "cantidad": nueva_cant,
                        "precio_unitario": datos["precio_unitario"],
                        "subtotal": subtotal
                    })
            
            # 2. Aplicar los cambios en la Base de Datos de manera atómica
            for id_prod_str, datos in entradas_cantidades.items():
                nueva_cant = int(datos["entry"].get().strip())
                diferencia = nueva_cant - datos["cantidad_anterior"]
                
                if diferencia != 0:
                    # Si la diferencia es positiva, resta stock. Si es negativa, devuelve stock (gracias al signo negativo en $inc)
                    self.db.productos.update_one(
                        {"_id": ObjectId(id_prod_str)},
                        {"$inc": {"stock": -diferencia}}
                    )
            
            # 3. Actualizar el documento del pedido con el nuevo arreglo de subdocumentos y el nuevo total
            self.db.pedidos.update_one(
                {"_id": ObjectId(id_ped)},
                {"$set": {
                    "detalle_productos": nuevas_lineas,
                    "total_pedido": nuevo_total_pedido
                }}
            )
            
            messagebox.showinfo("Éxito", "Cantidades del pedido modificadas y stock actualizado.")
            ventana_edit.destroy()
            self.buscar_mis_pedidos() # Refresca la tabla de gestión de pedidos
            self.restablecer_catalogo() # Refresca el stock visible en el catálogo
            self.cargar_historial_pedidos() # Refresca el historial de la pestaña 1

        # Botón para confirmar los cambios de la ventana emergente
        tk.Button(ventana_edit, text="Guardar Cambios", bg="#4CAF50", fg="white", font=("Arial", 10, "bold"), command=guardar_cambios_cantidades).pack(pady=15)

    def eliminar_pedido_ingresado(self):
        sel = self.tabla_gestion_p.selection()
        if not sel:
            messagebox.showwarning("Atención", "Seleccione un pedido para eliminar.")
            return
        valores = self.tabla_gestion_p.item(sel)['values']
        id_ped, estado = valores[0], valores[3]
        
        # REGLA DE NEGOCIO: Solo se puede eliminar si el estado es 'Ingresado'
        if estado != "Ingresado":
            messagebox.showerror("Denegado", f"Los pedidos en estado '{estado}' NO pueden ser eliminados por el cliente.")
            return
            
        if messagebox.askyesno("Confirmar", "¿Está seguro de que desea eliminar este pedido por completo? El stock será devuelto."):
            exito, msg = eliminar_pedido_cliente(self.db, id_ped)
            if exito:
                messagebox.showinfo("Eliminado", msg)
                self.buscar_mis_pedidos()
                self.restablecer_catalogo()
                self.cargar_historial_pedidos()
            else:
                messagebox.showerror("Error", msg)