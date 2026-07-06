import tkinter as tk
from tkinter import ttk, messagebox
from logicasCRUD.cliente_crud import ClienteCRUD
from logicasCRUD.pedido_crud import PedidoCRUD

class AdminInterfaz:
    def __init__(self, root, datos_admin):
        self.root = root
        self.admin = datos_admin 
        self.root.title(f"ComercioTech - Panel Maestro de Datos (Operador: {self.admin['nombre']})")
        self.root.geometry("1100x680")
        
        self.crud_cliente = ClienteCRUD()
        self.crud_pedido = PedidoCRUD()

        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill="both", expand=True, padx=10, pady=10)
        
        self.tab_pedido = ttk.Frame(self.notebook)
        self.tab_cliente = ttk.Frame(self.notebook)
        
        self.notebook.add(self.tab_pedido, text=" 📦 Monitor de Pedido ")
        self.notebook.add(self.tab_cliente, text=" 👥 Auditoría de Cliente ")
        
        self.dibujar_modulo_pedido()
        self.dibujar_modulo_cliente()

    def dibujar_modulo_pedido(self):
        frame_filtros = ttk.LabelFrame(self.tab_pedido, text=" Filtros de Búsqueda Dinámica (Colección: pedido) ", padding=10)
        frame_filtros.pack(fill="x", padx=10, pady=5)
        
        ttk.Label(frame_filtros, text="Estado:").grid(row=0, column=0, padx=5, pady=5)
        self.combo_filtro_estado = ttk.Combobox(frame_filtros, values=["Todos", "Ingresado", "En Proceso", "Entregado", "Anulado"], state="readonly", width=12)
        self.combo_filtro_estado.set("Todos")
        self.combo_filtro_estado.grid(row=0, column=1, padx=5, pady=5)
        
        ttk.Label(frame_filtros, text="Fecha (YYYY-MM-DD):").grid(row=0, column=2, padx=10, pady=5)
        self.entry_filtro_fecha = ttk.Entry(frame_filtros, width=15)
        self.entry_filtro_fecha.grid(row=0, column=3, padx=5, pady=5)
        
        ttk.Button(frame_filtros, text="🔍 Buscar", command=self.filtrar_pedido_db).grid(row=0, column=4, padx=15, pady=5)
        ttk.Button(frame_filtros, text="Limpiar", command=self.cargar_pedido_db_completo).grid(row=0, column=5, padx=5, pady=5)

        frame_tabla = ttk.Frame(self.tab_pedido)
        frame_tabla.pack(fill="both", expand=True, padx=10, pady=5)
        
        self.tabla_pedido = ttk.Treeview(frame_tabla, columns=("id", "rut", "fecha", "total", "estado"), show="headings")
        self.tabla_pedido.heading("id", text="ID Documento (_id)")
        self.tabla_pedido.heading("rut", text="RUT Cliente")
        self.tabla_pedido.heading("fecha", text="Fecha Creación")
        self.tabla_pedido.heading("total", text="Total")
        self.tabla_pedido.heading("estado", text="Estado")
        
        self.tabla_pedido.column("id", width=220, anchor="center")
        self.tabla_pedido.column("rut", width=140, anchor="center")
        self.tabla_pedido.column("fecha", width=140, anchor="center")
        self.tabla_pedido.column("total", width=130, anchor="e")
        self.tabla_pedido.column("estado", width=140, anchor="center")
        
        self.tabla_pedido.pack(fill="both", expand=True, side="left")
        scroll = ttk.Scrollbar(frame_tabla, orient="vertical", command=self.tabla_pedido.yview)
        self.tabla_pedido.configure(yscrollcommand=scroll.set)
        scroll.pack(fill="y", side="right")

        frame_acciones = ttk.LabelFrame(self.tab_pedido, text=" Operaciones de Estado ", padding=10)
        frame_acciones.pack(fill="x", padx=10, pady=10)
        
        ttk.Button(frame_acciones, text="⚙ Modificar Estado en MongoDB", command=self.actualizar_estado_pedido_db).pack(side="right", padx=5)
        self.combo_nuevo_estado = ttk.Combobox(frame_acciones, values=["Ingresado", "En Proceso", "Entregado", "Anulado"], state="readonly", width=15)
        self.combo_nuevo_estado.set("En Proceso")
        self.combo_nuevo_estado.pack(side="right", padx=10)

        self.cargar_pedido_db_completo()

    def cargar_pedido_db_completo(self):
        self.tabla_pedido.delete(*self.tabla_pedido.get_children())
        for ped in self.crud_pedido.obtener_todo_pedido():
            self.tabla_pedido.insert("", "end", values=(str(ped["_id"]), ped.get("rut_cliente", "N/A"), ped.get("fecha_pedido", "N/A"), f"${ped.get('total_pedido', 0)}", ped.get("estado_pedido", "Ingresado")))

    def filtrar_pedido_db(self):
        self.tabla_pedido.delete(*self.tabla_pedido.get_children())
        for ped in self.crud_pedido.filtrar_pedido_admin(self.combo_filtro_estado.get(), self.entry_filtro_fecha.get()):
            self.tabla_pedido.insert("", "end", values=(str(ped["_id"]), ped.get("rut_cliente", "N/A"), ped.get("fecha_pedido", "N/A"), f"${ped.get('total_pedido', 0)}", ped.get("estado_pedido", "Ingresado")))

    def actualizar_estado_pedido_db(self):
        seleccion = self.tabla_pedido.selection()
        if not seleccion:
            messagebox.showwarning("Aviso", "Seleccione un pedido de la cuadrícula.")
            return
            
        id_ped = self.tabla_pedido.item(seleccion, "values")[0]
        nuevo_est = self.combo_nuevo_estado.get()
        
        if self.crud_pedido.cambiar_estado_pedido(id_ped, nuevo_est):
            messagebox.showinfo("Éxito", "Documento actualizado en el motor local.")
            self.cargar_pedido_db_completo()
        else:
            messagebox.showerror("Error", "No se modificó el documento NoSQL.")

    def dibujar_modulo_cliente(self):
        frame_busqueda_cli = ttk.LabelFrame(self.tab_cliente, text=" Cuentas de Usuario Existentes (Colección: cliente) ", padding=10)
        frame_busqueda_cli.pack(fill="x", padx=10, pady=5)
        
        ttk.Button(frame_busqueda_cli, text="🔄 Sincronizar Tabla", command=self.cargar_cliente_db_completo).pack(side="right", padx=5)

        frame_tabla_cli = ttk.Frame(self.tab_cliente)
        frame_tabla_cli.pack(fill="both", expand=True, padx=10, pady=5)
        
        self.tabla_cliente = ttk.Treeview(frame_tabla_cli, columns=("id", "rut", "nombre", "correo", "rol"), show="headings")
        self.tabla_cliente.heading("id", text="ID Documento")
        self.tabla_cliente.heading("rut", text="RUT")
        self.tabla_cliente.heading("nombre", text="Nombre Completo")
        self.tabla_cliente.heading("correo", text="Correo Electrónico")
        self.tabla_cliente.heading("rol", text="Rol")
        
        self.tabla_cliente.column("id", width=220, anchor="center")
        self.tabla_cliente.column("rut", width=140, anchor="center")
        self.tabla_cliente.column("nombre", width=220, anchor="w")
        self.tabla_cliente.column("correo", width=240, anchor="w")
        self.tabla_cliente.column("rol", width=120, anchor="center")
        self.tabla_cliente.pack(fill="both", expand=True)
        
        frame_cruces = ttk.LabelFrame(self.tab_cliente, text=" Herramientas de Auditoría Cruzada ", padding=10)
        frame_cruces.pack(fill="x", padx=10, pady=10)
        
        ttk.Button(frame_cruces, text="📦 Rastrear Pedidos de este Cliente", command=self.auditar_pedidos_cliente).pack(side="left", padx=5)

        self.cargar_cliente_db_completo()

    def cargar_cliente_db_completo(self):
        self.tabla_cliente.delete(*self.tabla_cliente.get_children())
        for cli in self.crud_cliente.obtener_todo_cliente():
            self.tabla_cliente.insert("", "end", values=(str(cli["_id"]), cli.get("rut", "N/A"), cli.get("nombre", "N/A"), cli.get("correo", "N/A"), cli.get("rol", "cliente")))

    def auditar_pedidos_cliente(self):
        seleccion = self.tabla_cliente.selection()
        if not seleccion:
            messagebox.showwarning("Atención", "Seleccione un cliente para realizar el cruce.")
            return
        
        valores = self.tabla_cliente.item(seleccion, "values")
        rut_cli = valores[1]
        nombre_cli = valores[2]
        
        pedidos = self.crud_pedido.buscar_pedidos_por_cliente(rut_cli)
        resumen = f"📋 AUDITORÍA DE PEDIDO: {nombre_cli} ({rut_cli})\n" + "="*50 + "\n"
        
        if not pedidos:
            resumen += "Sin documentos de compra relacionados en la colección 'pedido'."
        else:
            for p in pedidos:
                resumen += f"• ID: {p['_id']} | Fecha: {p.get('fecha_pedido','N/A')}\n  Monto: ${p.get('total_pedido',0)} | Estado: {p.get('estado_pedido','Ingresado')}\n\n"
        
        messagebox.showinfo("Cruce NoSQL Relacionado", resumen)