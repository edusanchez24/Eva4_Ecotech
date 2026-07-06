import tkinter as tk
from tkinter import messagebox, ttk
from bson.objectid import ObjectId
from datetime import datetime
from logicasCRUD.producto_crud import listar_productos_disponibles
from logicasCRUD.pedido_crud import crear_pedido, eliminar_pedido_cliente

class VentanaCliente:
    def __init__(self, root, db, rut_cliente):
        self.root = root
        self.db = db
        self.rut_cliente = rut_cliente
        self.carrito_actual = [] 
        
        self.root.title(f"EcoTech - Panel de Cliente ({self.rut_cliente})")
        self.root.geometry("900x680")
        
        self.tab_control = ttk.Notebook(root)
        self.tab_perfil = ttk.Frame(self.tab_control)
        self.tab_catalogo = ttk.Frame(self.tab_control)
        self.tab_gestion_pedidos = ttk.Frame(self.tab_control)
        
        self.tab_control.add(self.tab_perfil, text="Módulo 1: Mi Perfil e Historial")
        self.tab_control.add(self.tab_catalogo, text="Módulo 2: Catálogo y Búsqueda")
        self.tab_control.add(self.tab_gestion_pedidos, text="Módulo 3: Gestión de Pedidos")
        self.tab_control.pack(expand=1, fill="both")
        
        self.crear_modulo_1_perfil()
        self.crear_modulo_2_catalogo()
        self.crear_modulo_3_pedidos()

    # =========================================================================
    # MÓDULO 1: GESTIÓN DE PERFIL (CON DIRECCIÓN DETALLADA Y FECHA REGISTRO)
    # =========================================================================
    def crear_modulo_1_perfil(self):
        tk.Label(self.tab_perfil, text="Mis Datos Personales y Dirección Obligatoria", font=("Arial", 12, "bold")).pack(pady=5)
        
        frame_datos = tk.Frame(self.tab_perfil)
        frame_datos.pack(pady=5)
        
        # Datos Básicos
        tk.Label(frame_datos, text="Nombre:").grid(row=0, column=0, padx=5, pady=3, sticky="e")
        self.ent_nom = tk.Entry(frame_datos, width=25)
        self.ent_nom.grid(row=0, column=1, padx=5, pady=3)
        
        tk.Label(frame_datos, text="Correo:").grid(row=1, column=0, padx=5, pady=3, sticky="e")
        self.ent_cor = tk.Entry(frame_datos, width=25)
        self.ent_cor.grid(row=1, column=1, padx=5, pady=3)
        
        tk.Label(frame_datos, text="Teléfono:").grid(row=2, column=0, padx=5, pady=3, sticky="e")
        self.ent_tel = tk.Entry(frame_datos, width=25)
        self.ent_tel.grid(row=2, column=1, padx=5, pady=3)

        # Campos de Dirección Obligatoria
        tk.Label(frame_datos, text="Calle:").grid(row=0, column=2, padx=5, pady=3, sticky="e")
        self.ent_calle = tk.Entry(frame_datos, width=25)
        self.ent_calle.grid(row=0, column=3, padx=5, pady=3)

        tk.Label(frame_datos, text="Número:").grid(row=1, column=2, padx=5, pady=3, sticky="e")
        self.ent_numero = tk.Entry(frame_datos, width=25)
        self.ent_numero.grid(row=1, column=3, padx=5, pady=3)

        tk.Label(frame_datos, text="Comuna:").grid(row=2, column=2, padx=5, pady=3, sticky="e")
        self.ent_comuna = tk.Entry(frame_datos, width=25)
        self.ent_comuna.grid(row=2, column=3, padx=5, pady=3)

        tk.Label(frame_datos, text="Ciudad:").grid(row=3, column=2, padx=5, pady=3, sticky="e")
        self.ent_ciudad = tk.Entry(frame_datos, width=25)
        self.ent_ciudad.grid(row=3, column=3, padx=5, pady=3)

        tk.Label(frame_datos, text="Región:").grid(row=4, column=2, padx=5, pady=3, sticky="e")
        self.ent_region = tk.Entry(frame_datos, width=25)
        self.ent_region.grid(row=4, column=3, padx=5, pady=3)

        tk.Label(frame_datos, text="Tipo Vivienda:").grid(row=5, column=2, padx=5, pady=3, sticky="e")
        self.combo_tipo_dir = ttk.Combobox(frame_datos, values=["Casa", "Departamento"], state="readonly", width=22)
        self.combo_tipo_dir.set("Casa")
        self.combo_tipo_dir.grid(row=5, column=3, padx=5, pady=3)

        # Fecha de Registro informativa
        self.lbl_fecha_reg = tk.Label(self.tab_perfil, text="Fecha de Registro: No registrado", fg="purple", font=("Arial", 10, "italic"))
        self.lbl_fecha_reg.pack(pady=3)
        
        frame_btn_perfil = tk.Frame(self.tab_perfil)
        frame_btn_perfil.pack(pady=5)
        
        tk.Button(frame_btn_perfil, text="Registrar / Actualizar Datos", bg="#4CAF50", fg="white", command=self.guardar_perfil).pack(side="left", padx=5)
        tk.Button(frame_btn_perfil, text="Consultar Mis Datos", bg="#2196F3", fg="white", command=self.cargar_perfil).pack(side="left", padx=5)
        
        tk.Label(self.tab_perfil, text="Historial General de Pedidos", font=("Arial", 11, "bold")).pack(pady=5)
        self.tabla_historial = ttk.Treeview(self.tab_perfil, columns=("ID", "Fecha", "Total", "Estado"), show="headings", height=5)
        self.tabla_historial.heading("ID", text="ID Pedido")
        self.tabla_historial.heading("Fecha", text="Fecha")
        self.tabla_historial.heading("Total", text="Total")
        self.tabla_historial.heading("Estado", text="Estado")
        self.tabla_historial.pack(fill="x", padx=20)
        
        self.cargar_perfil()

    def guardar_perfil(self):
        nombre = self.ent_nom.get().strip()
        correo = self.ent_cor.get().strip()
        telefono = self.ent_tel.get().strip()
        calle = self.ent_calle.get().strip()
        numero = self.ent_numero.get().strip()
        comuna = self.ent_comuna.get().strip()
        ciudad = self.ent_ciudad.get().strip()
        region = self.ent_region.get().strip()
        tipo_dir = self.combo_tipo_dir.get()
        
        # Validación obligatoria de todos los campos
        if not all([nombre, correo, telefono, calle, numero, comuna, ciudad, region, tipo_dir]):
            messagebox.showwarning("Atención", "Todos los campos de datos personales y dirección son OBLIGATORIOS.")
            return

        # Buscar si ya existe para mantener su fecha de registro original o asignarle la actual
        cliente_existente = self.db.clientes.find_one({"rut": self.rut_cliente})
        fecha_reg = cliente_existente.get("fecha_registro", datetime.now()) if cliente_existente else datetime.now()
            
        self.db.clientes.update_one(
            {"rut": self.rut_cliente},
            {"$set": {
                "nombre": nombre, 
                "correo": correo, 
                "telefono": telefono, 
                "fecha_registro": fecha_reg,
                "direccion": {
                    "calle": calle,
                    "numero": numero,
                    "comuna": comuna,
                    "ciudad": ciudad,
                    "region": region,
                    "tipo_direccion": tipo_dir
                },
                "estado": "activo"
            }},
            upsert=True
        )
        messagebox.showinfo("Éxito", "Perfil y Dirección obligatoria guardados correctamente.")
        self.cargar_perfil()

    def cargar_perfil(self):
        cliente = self.db.clientes.find_one({"rut": self.rut_cliente})
        if cliente:
            self.ent_nom.delete(0, tk.END); self.ent_nom.insert(0, cliente.get("nombre", ""))
            self.ent_cor.delete(0, tk.END); self.ent_cor.insert(0, cliente.get("correo", ""))
            self.ent_tel.delete(0, tk.END); self.ent_tel.insert(0, cliente.get("telefono", ""))
            
            # Cargar dirección embebida
            dir_emb = cliente.get("direccion", {})
            self.ent_calle.delete(0, tk.END); self.ent_calle.insert(0, dir_emb.get("calle", ""))
            self.ent_numero.delete(0, tk.END); self.ent_numero.insert(0, dir_emb.get("numero", ""))
            self.ent_comuna.delete(0, tk.END); self.ent_comuna.insert(0, dir_emb.get("comuna", ""))
            self.ent_ciudad.delete(0, tk.END); self.ent_ciudad.insert(0, dir_emb.get("ciudad", ""))
            self.ent_region.delete(0, tk.END); self.ent_region.insert(0, dir_emb.get("region", ""))
            if "tipo_direccion" in dir_emb:
                self.combo_tipo_dir.set(dir_emb["tipo_direccion"])
                
            if "fecha_registro" in cliente:
                self.lbl_fecha_reg.config(text=f"Fecha de Registro en Sistema: {cliente['fecha_registro'].strftime('%Y-%m-%d %H:%M')}")
        self.cargar_historial_pedidos()

    def cargar_historial_pedidos(self):
        self.tabla_historial.delete(*self.tabla_historial.get_children())
        pedidos = list(self.db.pedidos.find({"id_cliente": self.rut_cliente}))
        for ped in pedidos:
            fecha_str = ped["fecha_pedido"].strftime("%Y-%m-%d %H:%M") if "fecha_pedido" in ped else "N/A"
            self.tabla_historial.insert("", "end", values=(str(ped["_id"]), fecha_str, f"${ped.get('total_pedido', 0)}", ped.get("estado_pedido", "Ingresado")))

    # =========================================================================
    # MÓDULO 2: CATÁLOGO CON MARCA Y DESCRIPCIÓN
    # =========================================================================
    def crear_modulo_2_catalogo(self):
        tk.Label(self.tab_catalogo, text="Catálogo de Productos", font=("Arial", 12, "bold")).pack(pady=5)
        
        frame_busqueda = tk.Frame(self.tab_catalogo)
        frame_busqueda.pack(pady=5, fill="x", padx=20)
        
        tk.Label(frame_busqueda, text="Filtrar por (Nombre/Categoría/Marca):").pack(side="left", padx=5)
        self.ent_buscar_cat = tk.Entry(frame_busqueda, width=25)
        self.ent_buscar_cat.pack(side="left", padx=5)
        
        tk.Button(frame_busqueda, text="Buscar", bg="#2196F3", fg="white", command=self.buscar_productos).pack(side="left", padx=5)
        tk.Button(frame_busqueda, text="Restablecer", command=self.restablecer_catalogo).pack(side="left", padx=5)
        
        self.tabla_productos = ttk.Treeview(self.tab_catalogo, columns=("ID", "Nombre", "Marca", "Categoria", "Precio", "Stock"), show="headings", height=8)
        self.tabla_productos.heading("ID", text="ID")
        self.tabla_productos.heading("Nombre", text="Nombre")
        self.tabla_productos.heading("Marca", text="Marca")
        self.tabla_productos.heading("Categoria", text="Categoría")
        self.tabla_productos.heading("Precio", text="Precio")
        self.tabla_productos.heading("Stock", text="Stock")
        self.tabla_productos.pack(fill="both", expand=True, padx=20, pady=5)
        
        frame_acciones_cat = tk.Frame(self.tab_catalogo)
        frame_acciones_cat.pack(pady=10)
        
        tk.Button(frame_acciones_cat, text="Ver Detalle Extendido (Incluye Descripción)", bg="#9C27B0", fg="white", command=self.consultar_detalle_producto).pack(side="left", padx=10)
        tk.Button(frame_acciones_cat, text="Añadir a mi Orden", bg="#FF9800", fg="white", command=self.pre_anadir_producto).pack(side="left", padx=10)
        
        self.restablecer_catalogo()

    def buscar_productos(self):
        termino = self.ent_buscar_cat.get().strip()
        self.tabla_productos.delete(*self.tabla_productos.get_children())
        query = {
            "stock": {"$gt": 0},
            "$or": [
                {"nombre_producto": {"$regex": termino, "$options": "i"}},
                {"categoria": {"$regex": termino, "$options": "i"}},
                {"marca": {"$regex": termino, "$options": "i"}}
            ]
        }
        for p in self.db.productos.find(query):
            self.tabla_productos.insert("", "end", values=(str(p["_id"]), p.get("nombre_producto"), p.get("marca", "EcoBrand"), p.get("categoria", "General"), p.get("precio_unitario"), p.get("stock")))

    def restablecer_catalogo(self):
        self.ent_buscar_cat.delete(0, tk.END)
        self.tabla_productos.delete(*self.tabla_productos.get_children())
        for p in self.db.productos.find({"stock": {"$gt": 0}}):
            self.tabla_productos.insert("", "end", values=(str(p["_id"]), p.get("nombre_producto"), p.get("marca", "EcoBrand"), p.get("categoria", "General"), p.get("precio_unitario"), p.get("stock")))

    def consultar_detalle_producto(self):
        sel = self.tabla_productos.selection()
        if not sel:
            messagebox.showwarning("Atención", "Seleccione un producto del catálogo.")
            return
        id_p = self.tabla_productos.item(sel)['values'][0]
        p = self.db.productos.find_one({"_id": ObjectId(id_p)})
        
        detalle = f"ID: {p['_id']}\nNombre: {p['nombre_producto']}\nMarca: {p.get('marca','No especificada')}\nCategoría: {p.get('categoria','N/A')}\nPrecio: ${p['precio_unitario']}\nStock: {p['stock']}\n\nDescripción:\n{p.get('descripcion','Sin descripción disponible (Opcional).')}"
        messagebox.showinfo("Detalle Técnico de Producto", detalle)

    def pre_anadir_producto(self):
        sel = self.tabla_productos.selection()
        if not sel:
            messagebox.showwarning("Atención", "Seleccione un producto para añadir.")
            return
        valores = self.tabla_productos.item(sel)['values']
        id_p, nombre, precio, stock_disp = valores[0], valores[1], int(valores[4]), int(valores[5])
        
        if stock_disp <= 0:
            messagebox.showerror("Sin Unidades", "No queda stock disponible.")
            return
            
        cant_ya_en_carrito = sum(item['cantidad'] for item in self.carrito_actual if item['id_producto'] == id_p)
        if cant_ya_en_carrito + 1 > stock_disp:
            messagebox.showerror("Límite de Stock", "No puedes añadir más unidades de las existentes.")
            return
            
        self.carrito_actual.append({
            "id_producto": id_p,
            "nombre_producto": nombre,
            "precio_unitario": precio,
            "cantidad": 1
        })
        messagebox.showinfo("Añadido", f"Se agregó 1 unidad de '{nombre}' al Módulo 3.")
        self.actualizar_vista_carrito()

    # =========================================================================
    # MÓDULO 3: GESTIÓN DE PEDIDOS (USA LA DIRECCIÓN GUARDADA)
    # =========================================================================
    def crear_modulo_3_pedidos(self):
        tk.Label(self.tab_gestion_pedidos, text="Borrador del Pedido Actual", font=("Arial", 11, "bold")).pack(pady=5)
        
        self.tabla_carrito = ttk.Treeview(self.tab_gestion_pedidos, columns=("Nombre", "Precio Unitario", "Cantidad", "Subtotal"), show="headings", height=4)
        self.tabla_carrito.heading("Nombre", text="Producto")
        self.tabla_carrito.heading("Precio Unitario", text="Precio Unitario")
        self.tabla_carrito.heading("Cantidad", text="Cantidad")
        self.tabla_carrito.heading("Subtotal", text="Subtotal")
        self.tabla_carrito.pack(fill="x", padx=20)
        
        self.lbl_total_pedido = tk.Label(self.tab_gestion_pedidos, text="TOTAL DE LA ORDEN: $0", font=("Arial", 12, "bold"), fg="darkgreen")
        self.lbl_total_pedido.pack(pady=5)
        
        frame_confirmar = tk.Frame(self.tab_gestion_pedidos)
        frame_confirmar.pack(pady=5)
        tk.Button(frame_confirmar, text="Confirmar y Crear Pedido", bg="#4CAF50", fg="white", command=self.confirmar_nuevo_pedido).pack(side="left", padx=5)
        tk.Button(frame_confirmar, text="Vaciar Borrador", bg="#f44336", fg="white", command=self.vaciar_borrador).pack(side="left", padx=5)
        
        tk.Frame(self.tab_gestion_pedidos, height=2, bd=1, relief="sunken").pack(fill="x", padx=10, pady=10)
        
        tk.Label(self.tab_gestion_pedidos, text="Buscar y Gestionar Mis Pedidos Guardados", font=("Arial", 11, "bold")).pack()
        
        frame_busqueda_p = tk.Frame(self.tab_gestion_pedidos)
        frame_busqueda_p.pack(pady=5)
        tk.Label(frame_busqueda_p, text="Filtrar ID Pedido (Opcional):").pack(side="left")
        self.ent_buscar_id_p = tk.Entry(frame_busqueda_p, width=25)
        self.ent_buscar_id_p.pack(side="left", padx=5)
        tk.Button(frame_busqueda_p, text="Buscar", command=self.buscar_mis_pedidos).pack(side="left")
        
        self.tabla_gestion_p = ttk.Treeview(self.tab_gestion_pedidos, columns=("ID", "Fecha", "Total", "Estado"), show="headings", height=5)
        self.tabla_gestion_p.heading("ID", text="ID Pedido")
        self.tabla_gestion_p.heading("Fecha", text="Fecha")
        self.tabla_gestion_p.heading("Total", text="Total")
        self.tabla_gestion_p.heading("Estado", text="Estado")
        self.tabla_gestion_p.pack(fill="x", padx=20, pady=5)
        
        frame_crud_pedidos = tk.Frame(self.tab_gestion_pedidos)
        frame_crud_pedidos.pack(pady=10)
        tk.Button(frame_crud_pedidos, text="Modificar Cantidades", bg="#FF9800", fg="white", command=self.modificar_pedido_ingresado).pack(side="left", padx=10)
        tk.Button(frame_crud_pedidos, text="Eliminar Pedido", bg="#f44336", fg="white", command=self.eliminar_pedido_ingresado).pack(side="left", padx=10)
        
        self.buscar_mis_pedidos()

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
            messagebox.showwarning("Borrador Vacío", "No has agregado productos a tu orden.")
            return
            
        # Requerimiento: Buscar la dirección registrada del cliente para adjuntarla al pedido
        cliente = self.db.clientes.find_one({"rut": self.rut_cliente})
        if not cliente or "direccion" not in cliente:
            messagebox.showerror("Dirección Faltante", "Antes de crear un pedido, debes completar y guardar tu perfil con tu dirección obligatoria en el Módulo 1.")
            return

        direccion_cliente = cliente["direccion"]
        exito, msg = crear_pedido(self.db, self.rut_cliente, self.carrito_actual, direccion_cliente)
        if exito:
            messagebox.showinfo("Orden Creada", "¡Pedido confirmado e ingresado exitosamente con tu dirección registrada!")
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
            try: query["_id"] = ObjectId(filtro_id)
            except: return
                
        for ped in self.db.pedidos.find(query):
            fecha_str = ped["fecha_pedido"].strftime("%Y-%m-%d %H:%M") if "fecha_pedido" in ped else "N/A"
            self.tabla_gestion_p.insert("", "end", values=(str(ped["_id"]), fecha_str, f"${ped.get('total_pedido',0)}", ped.get("estado_pedido", "Ingresado")))

    def modificar_pedido_ingresado(self):
        sel = self.tabla_gestion_p.selection()
        if not sel: return
        valores = self.tabla_gestion_p.item(sel)['values']
        id_ped, estado = valores[0], valores[3]
        
        if estado != "Ingresado":
            messagebox.showerror("Denegado", f"No se pueden modificar pedidos en estado '{estado}'.")
            return
            
        pedido = self.db.pedidos.find_one({"_id": ObjectId(id_ped)})
        ventana_edit = tk.Toplevel(self.root)
        ventana_edit.title("Modificar Cantidades")
        ventana_edit.geometry("450x350")
        ventana_edit.grab_set()
        
        frame_lineas = tk.Frame(ventana_edit)
        frame_lineas.pack(pady=10, padx=20, fill="both", expand=True)
        entradas_cantidades = {}
        
        for i, item in enumerate(pedido.get("detalle_productos", [])):
            id_prod_str = str(item["id_producto"])
            tk.Label(frame_lineas, text=f"{item['nombre_producto']} (Actual: {item['cantidad']}):").grid(row=i, column=0, sticky="w", pady=5)
            ent_cant = tk.Entry(frame_lineas, width=8)
            ent_cant.grid(row=i, column=1, pady=5, padx=5)
            ent_cant.insert(0, str(item["cantidad"]))
            entradas_cantidades[id_prod_str] = {"entry": ent_cant, "cantidad_anterior": item["cantidad"], "precio_unitario": item["precio_unitario"], "nombre_producto": item["nombre_producto"]}
            
        def guardar_cambios_cantidades():
            nuevas_lineas = []
            nuevo_total = 0
            for id_prod_str, datos in entradas_cantidades.items():
                try:
                    nueva_cant = int(datos["entry"].get().strip())
                    if nueva_cant < 0: raise ValueError()
                except:
                    messagebox.showerror("Error", "Ingrese números válidos.")
                    return
                
                diferencia = nueva_cant - datos["cantidad_anterior"]
                if diferencia > 0:
                    prod_db = self.db.productos.find_one({"_id": ObjectId(id_prod_str)})
                    if not prod_db or prod_db.get("stock", 0) < diferencia:
                        messagebox.showerror("Stock Insuficiente", f"No hay stock para {datos['nombre_producto']}.")
                        return
                
                if nueva_cant > 0:
                    sub = nueva_cant * datos["precio_unitario"]
                    nuevo_total += sub
                    nuevas_lineas.append({"id_producto": ObjectId(id_prod_str), "nombre_producto": datos["nombre_producto"], "cantidad": nueva_cant, "precio_unitario": datos["precio_unitario"], "subtotal": sub})
            
            for id_prod_str, datos in entradas_cantidades.items():
                nueva_cant = int(datos["entry"].get().strip())
                diferencia = nueva_cant - datos["cantidad_anterior"]
                if diferencia != 0:
                    self.db.productos.update_one({"_id": ObjectId(id_prod_str)}, {"$inc": {"stock": -diferencia}})
            
            self.db.pedidos.update_one({"_id": ObjectId(id_ped)}, {"$set": {"detalle_productos": nuevas_lineas, "total_pedido": nuevo_total}})
            messagebox.showinfo("Éxito", "Pedido modificado correctamente.")
            ventana_edit.destroy()
            self.buscar_mis_pedidos()
            self.restablecer_catalogo()
            self.cargar_historial_pedidos()

        tk.Button(ventana_edit, text="Guardar Cambios", bg="#4CAF50", fg="white", command=guardar_cambios_cantidades).pack(pady=15)

    def eliminar_pedido_ingresado(self):
        sel = self.tabla_gestion_p.selection()
        if not sel: return
        valores = self.tabla_gestion_p.item(sel)['values']
        id_ped, estado = valores[0], valores[3]
        if estado != "Ingresado":
            messagebox.showerror("Denegado", "Solo se pueden eliminar pedidos en estado 'Ingresado'.")
            return
        if messagebox.askyesno("Confirmar", "¿Desea eliminar este pedido?"):
            exito, msg = eliminar_pedido_cliente(self.db, id_ped)
            if exito:
                self.buscar_mis_pedidos()
                self.restablecer_catalogo()
                self.cargar_historial_pedidos()