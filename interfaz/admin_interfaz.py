import tkinter as tk
from tkinter import messagebox, ttk
from logicasCRUD.cliente_crud import registrar_cliente
from logicasCRUD.producto_crud import crear_producto
from logicasCRUD.pedido_crud import listar_todos_los_pedidos, actualizar_estado_pedido

class VentanaAdmin:
    def __init__(self, root, db):
        self.root = root
        self.db = db
        self.root.title("EcoTech - Panel de Administración")
        self.root.geometry("750x550")
        
        tab_control = ttk.Notebook(root)
        self.tab_clientes = ttk.Frame(tab_control)
        self.tab_productos = ttk.Frame(tab_control)
        self.tab_pedidos = ttk.Frame(tab_control)
        
        tab_control.add(self.tab_clientes, text="Registrar Clientes")
        tab_control.add(self.tab_productos, text="Mantenedor Productos")
        tab_control.add(self.tab_pedidos, text="Monitorear Pedidos")
        tab_control.pack(expand=1, fill="both")
        
        self.inicializar_modulo_clientes()
        self.inicializar_modulo_productos()
        self.inicializar_modulo_pedidos()

    def inicializar_modulo_clientes(self):
        tk.Label(self.tab_clientes, text="Formulario de Registro de Cliente", font=("Arial", 12, "bold")).pack(pady=10)
        
        tk.Label(self.tab_clientes, text="RUT (ID único):").pack()
        self.ent_rut = tk.Entry(self.tab_clientes)
        self.ent_rut.pack()
        
        tk.Label(self.tab_clientes, text="Nombre Completo:").pack()
        self.ent_nom = tk.Entry(self.tab_clientes)
        self.ent_nom.pack()
        
        tk.Label(self.tab_clientes, text="Correo Electrónico:").pack()
        self.ent_mail = tk.Entry(self.tab_clientes)
        self.ent_mail.pack()
        
        tk.Label(self.tab_clientes, text="Teléfono:").pack()
        self.ent_tel = tk.Entry(self.tab_clientes)
        self.ent_tel.pack()
        
        tk.Button(self.tab_clientes, text="Guardar Cliente", bg="#4CAF50", fg="white", command=self.guardar_cliente).pack(pady=20)

    def guardar_cliente(self):
        r, n, m, t = self.ent_rut.get().strip(), self.ent_nom.get().strip(), self.ent_mail.get().strip(), self.ent_tel.get().strip()
        if not all([r, n, m, t]):
            messagebox.showwarning("Campos vacíos", "Por favor complete todos los datos.")
            return
        exito, msg = registrar_cliente(self.db, r, n, m, t)
        if exito:
            messagebox.showinfo("Éxito", msg)
            # Limpiar entradas
            self.ent_rut.delete(0, tk.END); self.ent_nom.delete(0, tk.END); self.ent_mail.delete(0, tk.END); self.ent_tel.delete(0, tk.END)
        else:
            messagebox.showerror("Error", msg)

    def inicializar_modulo_productos(self):
        tk.Label(self.tab_productos, text="Agregar Nuevo Producto al Inventario", font=("Arial", 12, "bold")).pack(pady=10)
        
        tk.Label(self.tab_productos, text="Nombre del Producto:").pack()
        self.ent_p_nom = tk.Entry(self.tab_productos)
        self.ent_p_nom.pack()
        
        tk.Label(self.tab_productos, text="Categoría:").pack()
        self.ent_p_cat = tk.Entry(self.tab_productos)
        self.ent_p_cat.pack()
        
        tk.Label(self.tab_productos, text="Precio Unitario ($):").pack()
        self.ent_p_pre = tk.Entry(self.tab_productos)
        self.ent_p_pre.pack()
        
        tk.Label(self.tab_productos, text="Stock Inicial:").pack()
        self.ent_p_stk = tk.Entry(self.tab_productos)
        self.ent_p_stk.pack()
        
        tk.Button(self.tab_productos, text="Publicar Producto", bg="#2196F3", fg="white", command=self.guardar_producto).pack(pady=20)

    def guardar_producto(self):
        n, c, p, s = self.ent_p_nom.get().strip(), self.ent_p_cat.get().strip(), self.ent_p_pre.get().strip(), self.ent_p_stk.get().strip()
        if not all([n, c, p, s]):
            messagebox.showwarning("Atención", "Todos los campos son obligatorios.")
            return
        crear_producto(self.db, n, c, p, s)
        messagebox.showinfo("Guardado", "Producto incorporado de forma exitosa.")
        self.ent_p_nom.delete(0, tk.END); self.ent_p_cat.delete(0, tk.END); self.ent_p_pre.delete(0, tk.END); self.ent_p_stk.delete(0, tk.END)

    def inicializar_modulo_pedidos(self):
        tk.Label(self.tab_pedidos, text="Consola de Monitoreo de Órdenes de Compra", font=("Arial", 12, "bold")).pack(pady=5)
        
        self.tabla_adm_ped = ttk.Treeview(self.tab_pedidos, columns=("ID", "Cliente", "Total", "Estado"), show="headings")
        self.tabla_adm_ped.heading("ID", text="ID Pedido")
        self.tabla_adm_ped.heading("Cliente", text="RUT Cliente")
        self.tabla_adm_ped.heading("Total", text="Monto Total")
        self.tabla_adm_ped.heading("Estado", text="Estado Actual")
        self.tabla_adm_ped.pack(fill="x", padx=10, pady=5)
        
        btn_frame = tk.Frame(self.tab_pedidos)
        btn_frame.pack(pady=10)
        
        tk.Button(btn_frame, text="Cargar/Refrescar Pedidos", command=self.cargar_todos_los_pedidos).pack(side="left", padx=5)
        tk.Button(btn_frame, text="Marcar 'En Proceso'", bg="#FF9800", fg="white", command=lambda: self.cambiar_estado("En Proceso")).pack(side="left", padx=5)
        tk.Button(btn_frame, text="Marcar 'Entregado'", bg="#4CAF50", fg="white", command=lambda: self.cambiar_estado("Entregado")).pack(side="left", padx=5)
        self.cargar_todos_los_pedidos()

    def cargar_todos_los_pedidos(self):
        self.tabla_adm_ped.delete(*self.tabla_adm_ped.get_children())
        for p in listar_todos_los_pedidos(self.db):
            self.tabla_adm_ped.insert("", "end", values=(str(p["_id"]), p["id_cliente"], f"${p['total_pedido']}", p["estado_pedido"]))

    def cambiar_estado(self, nuevo_estado):
        seleccion = self.tabla_adm_ped.selection()
        if not seleccion:
            messagebox.showwarning("Selección vacía", "Debe seleccionar un pedido de la lista.")
            return
        id_pedido = self.tabla_adm_ped.item(seleccion)['values'][0]
        actualizar_estado_pedido(self.db, id_pedido, nuevo_estado)
        messagebox.showinfo("Actualizado", f"Pedido modificado a '{nuevo_estado}' con éxito.")
        self.cargar_todos_los_pedidos()