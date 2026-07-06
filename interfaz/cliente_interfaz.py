import tkinter as tk
from tkinter import messagebox, ttk
from logicasCRUD.producto_crud import listar_productos_disponibles
from logicasCRUD.pedido_crud import crear_pedido, listar_pedidos_por_cliente

class VentanaCliente:
    def __init__(self, root, db, rut_cliente):
        self.root = root
        self.db = db
        self.rut_cliente = rut_cliente
        self.carrito = []
        
        self.root.title(f"EcoTech - Panel Cliente ({self.rut_cliente})")
        self.root.geometry("700x500")
        
        # Pestañas
        tab_control = ttk.Notebook(root)
        self.tab_comprar = ttk.Frame(tab_control)
        self.tab_mis_pedidos = ttk.Frame(tab_control)
        tab_control.add(self.tab_comprar, text="Catálogo de Productos")
        tab_control.add(self.tab_mis_pedidos, text="Mis Pedidos")
        tab_control.pack(expand=1, fill="both")
        
        self.inicializar_tab_comprar()
        self.inicializar_tab_pedidos()
        
    def inicializar_tab_comprar(self):
        tk.Label(self.tab_comprar, text="Productos Eco-Eficientes Disponibles", font=("Arial", 12, "bold")).pack(pady=10)
        
        # Tabla de productos
        self.tabla_prod = ttk.Treeview(self.tab_comprar, columns=("ID", "Nombre", "Precio", "Stock"), show="headings")
        self.tabla_prod.heading("ID", text="ID")
        self.tabla_prod.heading("Nombre", text="Nombre")
        self.tabla_prod.heading("Precio", text="Precio")
        self.tabla_prod.heading("Stock", text="Stock Disponible")
        self.tabla_prod.pack(fill="x", padx=15)
        
        btn_frame = tk.Frame(self.tab_comprar)
        btn_frame.pack(pady=15)
        
        tk.Button(btn_frame, text="Actualizar Catálogo", command=self.cargar_productos).pack(side="left", padx=5)
        tk.Button(btn_frame, text="Añadir Seleccionado al Carrito", bg="#2196F3", fg="white", command=self.anadir_al_carrito).pack(side="left", padx=5)
        tk.Button(btn_frame, text="Finalizar Compra del Carrito", bg="#4CAF50", fg="white", command=self.comprar).pack(side="left", padx=5)
        
        self.lbl_carrito = tk.Label(self.tab_comprar, text="Carrito: 0 items", fg="blue")
        self.lbl_carrito.pack()
        self.cargar_productos()

    def cargar_productos(self):
        self.tabla_prod.delete(*self.tabla_prod.get_children())
        for p in listar_productos_disponibles(self.db):
            self.tabla_prod.insert("", "end", values=(str(p["_id"]), p["nombre_producto"], p["precio_unitario"], p["stock"]))

    def anadir_al_carrito(self):
        seleccion = self.tabla_prod.selection()
        if not seleccion:
            messagebox.showwarning("Atención", "Seleccione un producto de la lista.")
            return
        valores = self.tabla_prod.item(seleccion)['values']
        
        # Agregar ítem al carrito de compras local
        item = {
            "id_producto": valores[0],
            "nombre": valores[1],
            "precio_unitario": int(valores[2]),
            "cantidad": 1  # Por simplicidad añade de a 1 unidad
        }
        self.carrito.append(item)
        self.lbl_carrito.config(text=f"Carrito: {len(self.carrito)} item(s) añadidos.")
        messagebox.showinfo("Éxito", f"{valores[1]} agregado al carrito.")

    def comprar(self):
        if not self.carrito:
            messagebox.showwarning("Carrito Vacío", "No tienes productos en el carrito.")
            return
            
        # Dirección fija simulada (proveniente de las direcciones embebidas del cliente)
        direccion = {"calle": "Av. Principal", "numero": "456", "comuna": "Santiago"}
        
        exito, msg = crear_pedido(self.db, self.rut_cliente, self.carrito, direccion)
        if exito:
            messagebox.showinfo("Compra Exitosa", msg)
            self.carrito = []
            self.lbl_carrito.config(text="Carrito: 0 items")
            self.cargar_productos()
            self.cargar_pedidos()
        else:
            messagebox.showerror("Fallo en la Compra", msg)

    def inicializar_tab_pedidos(self):
        self.tabla_pedidos = ttk.Treeview(self.tab_mis_pedidos, columns=("Fecha", "Estado", "Total"), show="headings")
        self.tabla_pedidos.heading("Fecha", text="Fecha")
        self.tabla_pedidos.heading("Estado", text="Estado")
        self.tabla_pedidos.heading("Total", text="Monto Total")
        self.tabla_pedidos.pack(fill="both", expand=True, padx=15, pady=15)
        tk.Button(self.tab_mis_pedidos, text="Actualizar Mis Pedidos", command=self.cargar_pedidos).pack(pady=5)
        self.cargar_pedidos()

    def cargar_pedidos(self):
        self.tabla_pedidos.delete(*self.tabla_pedidos.get_children())
        for ped in listar_pedidos_por_cliente(self.db, self.rut_cliente):
            self.tabla_pedidos.insert("", "end", values=(ped["fecha_pedido"].strftime("%Y-%m-%d %H:%M"), ped["estado_pedido"], f"${ped['total_pedido']}"))