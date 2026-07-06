import tkinter as tk
from tkinter import ttk, messagebox

class AdminInterfaz:
    def __init__(self, root, datos_admin):
        self.root = root
        self.admin = datos_admin
        self.root.title(f"ComercioTech - Módulo de Control Administrativo")
        self.root.geometry("850x500")
        
        self.crear_componentes()

    def crear_componentes(self):
        # --- ENCABEZADO ---
        lbl_titulo = ttk.Label(self.root, text="Panel de Gestión de Pedidos Globales", font=("Arial", 14, "bold"))
        lbl_titulo.pack(pady=10)

        # --- FILTROS DE BÚSQUEDA ---
        frame_filtros = ttk.LabelFrame(self.root, text=" Filtros de Auditoría ")
        frame_filtros.pack(fill="x", padx=10, pady=5)
        
        ttk.Label(frame_filtros, text="Estado:").grid(row=0, column=0, padx=5, pady=5)
        self.combo_filtro_estado = ttk.Combobox(frame_filtros, values=["Todos", "Ingresado", "En Proceso", "Entregado", "Anulado"], state="readonly")
        self.combo_filtro_estado.set("Todos")
        self.combo_filtro_estado.grid(row=0, column=1, padx=5, pady=5)
        
        btn_filtrar = ttk.Button(frame_filtros, text="Aplicar Filtro", command=self.acc_filtrar_pedidos)
        btn_filtrar.grid(row=0, column=2, padx=10, pady=5)

        # --- TABLA DE PEDIDOS ---
        frame_tabla = ttk.Frame(self.root)
        frame_tabla.pack(fill="both", expand=True, padx=10, pady=5)
        
        columnas = ("id_pedido", "rut_cliente", "fecha", "total", "estado")
        self.tabla_pedidos = ttk.Treeview(frame_tabla, columns=columnas, show="headings")
        
        for col in columnas:
            self.tabla_pedidos.heading(col, text=col.upper().replace("_", " "))
            self.tabla_pedidos.column(col, width=140, anchor="center")
            
        self.tabla_pedidos.pack(fill="both", expand=True, side="left")
        
        # Barra de scroll para cuando la base de datos crezca exponencialmente
        scrollbar = ttk.Scrollbar(frame_tabla, orient="vertical", command=self.tabla_pedidos.yview)
        self.tabla_pedidos.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(fill="y", side="right")

        # Inyección de datos de prueba (Boceto)
        self.tabla_pedidos.insert("", "end", values=("6677ccb1...03cc", "12345678-9", "2026-06-28", "$734.970", "Ingresado"))
        self.tabla_pedidos.insert("", "end", values=("6677ccb1...04dd", "9876543-2", "2026-06-27", "$45.000", "Entregado"))

        # --- GESTIÓN DE ESTADOS (PIE DE PÁGINA) ---
        frame_gestion = ttk.LabelFrame(self.root, text=" Cambiar Estado del Pedido Seleccionado ")
        frame_gestion.pack(fill="x", padx=10, pady=10)
        
        ttk.Label(frame_gestion, text="Nuevo Estado:").pack(side="left", padx=10, pady=10)
        self.combo_nuevo_estado = ttk.Combobox(frame_gestion, values=["Ingresado", "En Proceso", "Entregado", "Anulado"], state="readonly")
        self.combo_nuevo_estado.pack(side="left", padx=5, pady=10)
        
        btn_actualizar = ttk.Button(frame_gestion, text="Guardar Cambios en DB", command=self.acc_cambiar_estado)
        btn_actualizar.pack(side="left", padx=10, pady=10)

    # --- ACCIONES ---
    def acc_filtrar_pedidos(self):
        estado = self.combo_filtro_estado.get()
        messagebox.showinfo("Filtro", f"Llamando a PedidoModel para traer solo los documentos con estado: {estado}")

    def acc_cambiar_estado(self):
        seleccion = self.tabla_pedidos.selection()
        if not seleccion:
            messagebox.showwarning("Advertencia", "Seleccione un pedido de la lista para modificarlo.")
            return
            
        nuevo_estado = self.combo_nuevo_estado.get()
        if not nuevo_estado:
            messagebox.showwarning("Advertencia", "Seleccione el nuevo estado de la lista desplegable.")
            return
            
        valores = self.tabla_pedidos.item(seleccion, "values")
        id_pedido = valores[0]
        
        # Aquí se ejecuta el update_one() de tu controlador
        messagebox.showinfo("Éxito", f"Pedido {id_pedido} actualizado a: {nuevo_estado}")