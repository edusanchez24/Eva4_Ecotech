import tkinter as tk
from tkinter import messagebox, ttk
from datetime import datetime
from bson.objectid import ObjectId

class VentanaAdmin:
    def __init__(self, root, db):
        self.root = root
        self.db = db
        self.root.title("EcoTech - Panel de Administración General")
        self.root.geometry("950x650")
        
        # Control de Pestañas para los 3 Módulos del Administrador
        tab_control = ttk.Notebook(root)
        
        self.tab_pedidos = ttk.Frame(tab_control)
        self.tab_clientes = ttk.Frame(tab_control)
        self.tab_productos = ttk.Frame(tab_control)
        
        tab_control.add(self.tab_pedidos, text="Módulo 1: Gestión de Pedidos")
        tab_control.add(self.tab_clientes, text="Módulo 2: Gestión de Clientes")
        tab_control.add(self.tab_productos, text="Módulo 3: Inventario de Productos")
        
        tab_control.pack(expand=1, fill="both")
        
        # Inicializar los componentes de cada módulo
        self.inicializar_modulo_pedidos()
        self.inicializar_modulo_clientes()
        self.inicializar_modulo_productos()

    # =========================================================================
    # MÓDULO 1: ADMINISTRACIÓN DE PEDIDOS
    # =========================================================================
    def inicializar_modulo_pedidos(self):
        tk.Label(self.tab_pedidos, text="Consola de Órdenes y Pedidos del Sistema", font=("Arial", 12, "bold")).pack(pady=10)
        
        # Frame de Filtros de Pedidos
        frame_filtros_ped = tk.Frame(self.tab_pedidos)
        frame_filtros_ped.pack(fill="x", padx=15, pady=5)
        
        tk.Label(frame_filtros_ped, text="Buscar por Estado:").grid(row=0, column=0, padx=5, pady=5, sticky="w")
        self.combo_filtro_estado = ttk.Combobox(frame_filtros_ped, values=["Todos", "Ingresado", "En Proceso", "Entregado", "Anulado"], state="readonly", width=12)
        self.combo_filtro_estado.set("Todos")
        self.combo_filtro_estado.grid(row=0, column=1, padx=5, pady=5)
        
        tk.Label(frame_filtros_ped, text="Fecha (AAAA-MM-DD):").grid(row=0, column=2, padx=5, pady=5, sticky="w")
        self.ent_filtro_fecha = tk.Entry(frame_filtros_ped, width=12)
        self.ent_filtro_fecha.grid(row=0, column=3, padx=5, pady=5)
        
        tk.Button(frame_filtros_ped, text="Aplicar Filtros", bg="#2196F3", fg="white", command=self.cargar_pedidos_filtrados).grid(row=0, column=4, padx=10, pady=5)
        tk.Button(frame_filtros_ped, text="Limpiar Filtros", command=self.limpiar_filtros_pedidos).grid(row=0, column=5, padx=5, pady=5)
        
        # Tabla Principal de Pedidos
        self.tabla_pedidos = ttk.Treeview(self.tab_pedidos, columns=("ID", "RUT Cliente", "Fecha", "Total", "Estado"), show="headings", height=8)
        self.tabla_pedidos.heading("ID", text="ID Pedido")
        self.tabla_pedidos.heading("RUT Cliente", text="RUT Cliente")
        self.tabla_pedidos.heading("Fecha", text="Fecha de Creación")
        self.tabla_pedidos.heading("Total", text="Monto Total")
        self.tabla_pedidos.heading("Estado", text="Estado")
        self.tabla_pedidos.pack(fill="x", padx=15, pady=5)
        
        # Frame de Acciones de Actualización de Estado y Desglose
        frame_acciones_ped = tk.Frame(self.tab_pedidos)
        frame_acciones_ped.pack(pady=10)
        
        tk.Button(frame_acciones_ped, text="Ver Desglose Completo", bg="#9C27B0", fg="white", font=("Arial", 10, "bold"), command=self.mostrar_desglose_pedido).pack(side="left", padx=10)
        
        tk.Label(frame_acciones_ped, text="Cambiar Estado Seleccionado a:").pack(side="left", padx=5)
        self.combo_nuevo_estado = ttk.Combobox(frame_acciones_ped, values=["Ingresado", "En Proceso", "Entregado", "Anulado"], state="readonly", width=12)
        self.combo_nuevo_estado.set("En Proceso")
        self.combo_nuevo_estado.pack(side="left", padx=5)
        
        tk.Button(frame_acciones_ped, text="Actualizar Estado", bg="#4CAF50", fg="white", command=self.ejecutar_cambio_estado).pack(side="left", padx=5)
        
        self.cargar_pedidos_filtrados()

    def cargar_pedidos_filtrados(self):
        self.tabla_pedidos.delete(*self.tabla_pedidos.get_children())
        estado = self.combo_filtro_estado.get()
        fecha_texto = self.ent_filtro_fecha.get().strip()
        
        query = {}
        if estado != "Todos":
            query["estado_pedido"] = estado
            
        if fecha_texto:
            try:
                inicio_dia = datetime.strptime(fecha_texto, "%Y-%m-%d")
                # Filtro que abarca desde las 00:00 hasta las 23:59 del día ingresado
                fin_dia = inicio_dia.replace(hour=23, minute=59, second=59)
                query["fecha_pedido"] = {"$gte": inicio_dia, "$lte": fin_dia}
            except ValueError:
                messagebox.showerror("Error de Fecha", "El formato de fecha debe ser AAAA-MM-DD (Ejemplo: 2026-07-06).")
                return
                
        for p in self.db.pedidos.find(query):
            f_str = p["fecha_pedido"].strftime("%Y-%m-%d %H:%M") if "fecha_pedido" in p else "N/A"
            self.tabla_pedidos.insert("", "end", values=(str(p["_id"]), p.get("id_cliente"), f_str, f"${p.get('total_pedido', 0)}", p.get("estado_pedido")))

    def limpiar_filtros_pedidos(self):
        self.combo_filtro_estado.set("Todos")
        self.ent_filtro_fecha.delete(0, tk.END)
        self.cargar_pedidos_filtrados()

    def mostrar_desglose_pedido(self):
        sel = self.tabla_pedidos.selection()
        if not sel:
            messagebox.showwarning("Atención", "Seleccione un pedido para ver el desglose.")
            return
        id_ped = self.tabla_pedidos.item(sel)['values'][0]
        pedido = self.db.pedidos.find_one({"_id": ObjectId(id_ped)})
        
        desglose = f"=== DESGLOSE DEL PEDIDO ===\nID: {pedido['_id']}\nCliente: {pedido['id_cliente']}\nEstado: {pedido['estado_pedido']}\nTotal: ${pedido['total_pedido']}\n\n"
        desglose += "PRODUCTOS ADQUIRIDOS:\n"
        
        for item in pedido.get("detalle_productos", []):
            desglose += f"- {item['nombre_producto']} x{item['cantidad']} (c/u: ${item['precio_unitario']}) Subtotal: ${item['subtotal']}\n"
            
        messagebox.showinfo("Detalle de Órden", desglose)

    def ejecutar_cambio_estado(self):
        sel = self.tabla_pedidos.selection()
        if not sel:
            messagebox.showwarning("Atención", "Seleccione un pedido para modificar su estado.")
            return
        id_ped = self.tabla_pedidos.item(sel)['values'][0]
        nuevo_est = self.combo_nuevo_estado.get()
        
        self.db.pedidos.update_one({"_id": ObjectId(id_ped)}, {"$set": {"estado_pedido": nuevo_est}})
        messagebox.showinfo("Éxito", f"El pedido {id_ped} se actualizó a '{nuevo_est}' correctamente.")
        self.cargar_pedidos_filtrados()

    # =========================================================================
    # MÓDULO 2: ADMINISTRACIÓN DE CLIENTES
    # =========================================================================
    def inicializar_modulo_clientes(self):
        tk.Label(self.tab_clientes, text="Consola de Gestión y Registro de Clientes", font=("Arial", 12, "bold")).pack(pady=10)
        
        # Frame de Búsquedas Multicriterio
        frame_busqueda_cli = tk.Frame(self.tab_clientes)
        frame_busqueda_cli.pack(fill="x", padx=15, pady=5)
        
        tk.Label(frame_busqueda_cli, text="Buscar por RUT Exacto:").grid(row=0, column=0, padx=5, pady=5, sticky="w")
        self.ent_cli_rut = tk.Entry(frame_busqueda_cli, width=15)
        self.ent_cli_rut.grid(row=0, column=1, padx=5, pady=5)
        
        tk.Label(frame_busqueda_cli, text="Buscar por Nombre (Coincidencia):").grid(row=0, column=2, padx=5, pady=5, sticky="w")
        self.ent_cli_nombre = tk.Entry(frame_busqueda_cli, width=20)
        self.ent_cli_nombre.grid(row=0, column=3, padx=5, pady=5)
        
        tk.Button(frame_busqueda_cli, text="Buscar Clientes", bg="#2196F3", fg="white", command=self.buscar_clientes).grid(row=0, column=4, padx=10, pady=5)
        tk.Button(frame_busqueda_cli, text="Ver Todos", command=self.restablecer_clientes).grid(row=0, column=5, padx=5, pady=5)
        
        # Tabla de Clientes
        self.tabla_clientes = ttk.Treeview(self.tab_clientes, columns=("RUT", "Nombre", "Correo", "Telefono"), show="headings", height=6)
        self.tabla_clientes.heading("RUT", text="RUT Cliente")
        self.tabla_clientes.heading("Nombre", text="Nombre")
        self.tabla_clientes.heading("Correo", text="Correo Electrónico")
        self.tabla_clientes.heading("Telefono", text="Teléfono")
        self.tabla_clientes.pack(fill="x", padx=15, pady=5)
        
        frame_acciones_cli = tk.Frame(self.tab_clientes)
        frame_acciones_cli.pack(pady=10)
        tk.Button(frame_acciones_cli, text="Ver Ficha y Pedidos Asociados", bg="#4CAF50", fg="white", font=("Arial", 10, "bold"), command=self.consultar_detalle_y_pedidos_cliente).pack()
        
        self.restablecer_clientes()

    def buscar_clientes(self):
        rut_exacto = self.ent_cli_rut.get().strip()
        nombre_parcial = self.ent_cli_nombre.get().strip()
        
        self.tabla_clientes.delete(*self.tabla_clientes.get_children())
        query = {}
        
        if rut_exacto:
            query["rut"] = rut_exacto
        elif nombre_parcial:
            # Requerimiento: Búsqueda por coincidencia en el string de nombre
            query["nombre"] = {"$regex": nombre_parcial, "$options": "i"}
            
        for c in self.db.clientes.find(query):
            self.tabla_clientes.insert("", "end", values=(c.get("rut"), c.get("nombre"), c.get("correo"), c.get("telefono")))

    def restablecer_clientes(self):
        self.ent_cli_rut.delete(0, tk.END)
        self.ent_cli_nombre.delete(0, tk.END)
        self.tabla_clientes.delete(*self.tabla_clientes.get_children())
        for c in self.db.clientes.find():
            self.tabla_clientes.insert("", "end", values=(c.get("rut"), c.get("nombre"), c.get("correo"), c.get("telefono")))

    def consultar_detalle_y_pedidos_cliente(self):
        sel = self.tabla_clientes.selection()
        if not sel:
            messagebox.showwarning("Atención", "Debe seleccionar un cliente de la lista.")
            return
        rut_cli = self.tabla_clientes.item(sel)['values'][0]
        
        cliente = self.db.clientes.find_one({"rut": rut_cli})
        pedidos = list(self.db.pedidos.find({"id_cliente": rut_cli}))
        
        ficha = f"=== DETALLE COMPLETO DEL CLIENTE ===\nRUT: {cliente['rut']}\nNombre: {cliente['nombre']}\nCorreo: {cliente['correo']}\nTeléfono: {cliente['telefono']}\n\n"
        ficha += f"=== ÓRDENES DE COMPRA ASOCIADAS ({len(pedidos)}) ===\n"
        
        for p in pedidos:
            ficha += f"- Pedido ID: {p['_id']} | Total: ${p['total_pedido']} | Estado: {p['estado_pedido']}\n"
            
        messagebox.showinfo("Ficha de Cliente", ficha)

    # =========================================================================
    # MÓDULO 3: MANTENEDOR DE PRODUCTOS (CRUD COMPLETO)
    # =========================================================================
    def inicializar_modulo_productos(self):
        tk.Label(self.tab_productos, text="Mantenedor del Catálogo y Stock de Productos", font=("Arial", 12, "bold")).pack(pady=5)
        
        # Frame superior: Búsquedas de Productos
        frame_buscar_prod = tk.Frame(self.tab_productos)
        frame_buscar_prod.pack(fill="x", padx=15, pady=5)
        
        tk.Label(frame_buscar_prod, text="Nombre/Marca:").pack(side="left", padx=5)
        self.ent_prod_busqueda = tk.Entry(frame_buscar_prod, width=15)
        self.ent_prod_busqueda.pack(side="left", padx=5)
        
        tk.Label(frame_buscar_prod, text="Categoría:").pack(side="left", padx=5)
        self.ent_prod_cat_busqueda = tk.Entry(frame_buscar_prod, width=15)
        self.ent_prod_cat_busqueda.pack(side="left", padx=5)
        
        tk.Button(frame_buscar_prod, text="Filtrar Catálogo", bg="#2196F3", fg="white", command=self.buscar_productos_admin).pack(side="left", padx=5)
        tk.Button(frame_buscar_prod, text="Limpiar", command=self.restablecer_productos_admin).pack(side="left", padx=5)
        
        # Tabla de Productos (Muestra ID claramente)
        self.tabla_productos_adm = ttk.Treeview(self.tab_productos, columns=("ID", "Nombre", "Categoria", "Precio", "Stock"), show="headings", height=5)
        self.tabla_productos_adm.heading("ID", text="[CLAVE] ID de Objeto NoSQL")
        self.tabla_productos_adm.heading("Nombre", text="Nombre Producto")
        self.tabla_productos_adm.heading("Categoria", text="Categoría")
        self.tabla_productos_adm.heading("Precio", text="Precio")
        self.tabla_productos_adm.heading("Stock", text="Stock")
        self.tabla_productos_adm.pack(fill="x", padx=15, pady=5)
        self.tabla_productos_adm.bind("<<TreeviewSelect>>", self.cargar_campos_formulario_producto)
        
        # Formulario CRUD Integrado
        frame_form_prod = tk.LabelFrame(self.tab_productos, text=" Formulario de Datos del Producto ", font=("Arial", 10, "bold"))
        frame_form_prod.pack(fill="x", padx=15, pady=5)
        
        tk.Label(frame_form_prod, text="ID Producto (Solo lectura para modificar/eliminar):").grid(row=0, column=0, padx=5, pady=5, sticky="e")
        self.ent_form_id = tk.Entry(frame_form_prod, width=30, state="readonly", fg="red")
        self.ent_form_id.grid(row=0, column=1, padx=5, pady=5, columnspan=3, sticky="w")
        
        tk.Label(frame_form_prod, text="Nombre:").grid(row=1, column=0, padx=5, pady=5, sticky="e")
        self.ent_form_nombre = tk.Entry(frame_form_prod, width=20)
        self.ent_form_nombre.grid(row=1, column=1, padx=5, pady=5)
        
        tk.Label(frame_form_prod, text="Categoría:").grid(row=1, column=2, padx=5, pady=5, sticky="e")
        self.ent_form_categoria = tk.Entry(frame_form_prod, width=20)
        self.ent_form_categoria.grid(row=1, column=3, padx=5, pady=5)
        
        tk.Label(frame_form_prod, text="Precio ($):").grid(row=2, column=0, padx=5, pady=5, sticky="e")
        self.ent_form_precio = tk.Entry(frame_form_prod, width=20)
        self.ent_form_precio.grid(row=2, column=1, padx=5, pady=5)
        
        tk.Label(frame_form_prod, text="Stock:").grid(row=2, column=2, padx=5, pady=5, sticky="e")
        self.ent_form_stock = tk.Entry(frame_form_prod, width=20)
        self.ent_form_stock.grid(row=2, column=3, padx=5, pady=5)
        
        # Botones de Control de Operaciones CRUD
        frame_botones_crud = tk.Frame(self.tab_productos)
        frame_botones_crud.pack(pady=5)
        
        tk.Button(frame_botones_crud, text="Agregar Nuevo (Crear)", bg="#4CAF50", fg="white", command=self.agregar_producto_crud).pack(side="left", padx=10)
        tk.Button(frame_botones_crud, text="Modificar Seleccionado", bg="#FF9800", fg="white", command=self.modificar_producto_crud).pack(side="left", padx=10)
        tk.Button(frame_botones_crud, text="Eliminar Seleccionado", bg="#f44336", fg="white", command=self.eliminar_producto_crud).pack(side="left", padx=10)
        tk.Button(frame_botones_crud, text="Limpiar Formulario", command=self.limpiar_formulario_producto).pack(side="left", padx=10)
        
        self.restablecer_productos_admin()

    def buscar_productos_admin(self):
        nombre_parcial = self.ent_prod_busqueda.get().strip()
        cat_parcial = self.ent_prod_cat_busqueda.get().strip()
        
        self.tabla_productos_adm.delete(*self.tabla_productos_adm.get_children())
        query = {}
        
        if nombre_parcial:
            query["nombre_producto"] = {"$regex": nombre_parcial, "$options": "i"}
        if cat_parcial:
            query["categoria"] = {"$regex": cat_parcial, "$options": "i"}
            
        for p in self.db.productos.find(query):
            self.tabla_productos_adm.insert("", "end", values=(str(p["_id"]), p.get("nombre_producto"), p.get("categoria", "General"), p.get("precio_unitario"), p.get("stock")))

    def restablecer_productos_admin(self):
        self.ent_prod_busqueda.delete(0, tk.END)
        self.ent_prod_cat_busqueda.delete(0, tk.END)
        self.tabla_productos_adm.delete(*self.tabla_productos_adm.get_children())
        for p in self.db.productos.find():
            self.tabla_productos_adm.insert("", "end", values=(str(p["_id"]), p.get("nombre_producto"), p.get("categoria", "General"), p.get("precio_unitario"), p.get("stock")))

    def cargar_campos_formulario_producto(self, event):
        sel = self.tabla_productos_adm.selection()
        if not sel:
            return
        valores = self.tabla_productos_adm.item(sel)['values']
        
        # Desbloquear temporalmente campo ID para rellenarlo
        self.ent_form_id.config(state="normal")
        self.ent_form_id.delete(0, tk.END); self.ent_form_id.insert(0, valores[0])
        self.ent_form_id.config(state="readonly")
        
        self.ent_form_nombre.delete(0, tk.END); self.ent_form_nombre.insert(0, valores[1])
        self.ent_form_categoria.delete(0, tk.END); self.ent_form_categoria.insert(0, valores[2])
        self.ent_form_precio.delete(0, tk.END); self.ent_form_precio.insert(0, valores[3])
        self.ent_form_stock.delete(0, tk.END); self.ent_form_stock.insert(0, valores[4])

    def limpiar_formulario_producto(self):
        self.ent_form_id.config(state="normal")
        self.ent_form_id.delete(0, tk.END)
        self.ent_form_id.config(state="readonly")
        self.ent_form_nombre.delete(0, tk.END)
        self.ent_form_categoria.delete(0, tk.END)
        self.ent_form_precio.delete(0, tk.END)
        self.ent_form_stock.delete(0, tk.END)

    def agregar_producto_crud(self):
        n = self.ent_form_nombre.get().strip()
        c = self.ent_form_categoria.get().strip()
        p = self.ent_form_precio.get().strip()
        s = self.ent_form_stock.get().strip()
        
        if not all([n, c, p, s]):
            messagebox.showwarning("Atención", "Complete todos los campos del formulario para guardar un nuevo artículo.")
            return
        try:
            prod = {"nombre_producto": n, "categoria": c, "precio_unitario": int(p), "stock": int(s), "estado": "disponible"}
            self.db.productos.insert_one(prod)
            messagebox.showinfo("Éxito", f"Producto '{n}' insertado al catálogo NoSQL.")
            self.limpiar_formulario_producto()
            self.restablecer_productos_admin()
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo guardar el producto: {e}")

    def modificar_producto_crud(self):
        id_p = self.ent_form_id.get().strip()
        if not id_p:
            messagebox.showwarning("Atención", "Debe seleccionar un producto de la tabla para modificarlo utilizando su ID clave.")
            return
            
        n = self.ent_form_nombre.get().strip()
        c = self.ent_form_categoria.get().strip()
        p = self.ent_form_precio.get().strip()
        s = self.ent_form_stock.get().strip()
        
        try:
            self.db.productos.update_one(
                {"_id": ObjectId(id_p)},
                {"$set": {"nombre_producto": n, "categoria": c, "precio_unitario": int(p), "stock": int(s)}}
            )
            messagebox.showinfo("Éxito", f"Producto con ID {id_p} modificado correctamente.")
            self.limpiar_formulario_producto()
            self.restablecer_productos_admin()
        except Exception as e:
            messagebox.showerror("Error", f"Fallo al actualizar: {e}")

    def eliminar_producto_crud(self):
        id_p = self.ent_form_id.get().strip()
        if not id_p:
            messagebox.showwarning("Atención", "Seleccione un registro para eliminar por ID.")
            return
            
        if messagebox.askyesno("Confirmar", f"¿Seguro que desea eliminar el producto con ID {id_p} de la persistencia de datos?"):
            self.db.productos.delete_one({"_id": ObjectId(id_p)})
            messagebox.showinfo("Eliminado", "El documento ha sido removido de MongoDB.")
            self.limpiar_formulario_producto()
            self.restablecer_productos_admin()