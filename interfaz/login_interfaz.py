import tkinter as tk
from tkinter import ttk, messagebox
from logicasCRUD.cliente_crud import ClienteCRUD

class LoginInterfaz:
    def __init__(self, root):
        self.root = root
        self.root.title("ComercioTech - Autenticación Local")
        self.root.geometry("400x240")
        self.root.resizable(False, False)
        
        try:
            self.crud_cliente = ClienteCRUD()
        except Exception as e:
            messagebox.showerror("Error Crítico", f"MongoDB local desconectado en Windows 11:\n{e}")
        
        self.crear_componentes()

    def crear_componentes(self):
        self.frame_principal = ttk.Frame(self.root, padding="25")
        self.frame_principal.pack(fill="both", expand=True)

        lbl_titulo = ttk.Label(
            self.frame_principal, 
            text="SISTEMA DE AUTENTICACIÓN NoSQL", 
            font=("Arial", 11, "bold"),
            foreground="#2c3e50"
        )
        lbl_titulo.pack(pady=(0, 15))

        lbl_rut = ttk.Label(self.frame_principal, text="Ingrese RUT de Usuario:")
        lbl_rut.pack(anchor="w", pady=(0, 5))
        
        self.entry_rut = ttk.Entry(self.frame_principal, font=("Arial", 10), width=30)
        self.entry_rut.pack(pady=(0, 20))
        self.entry_rut.focus()

        btn_ingresar = ttk.Button(
            self.frame_principal, 
            text="Validar Identidad", 
            command=self.acc_ejecutar_login
        )
        btn_ingresar.pack(fill="x", ipady=5)

    def acc_ejecutar_login(self):
        rut_ingresado = self.entry_rut.get().strip()

        if not rut_ingresado:
            messagebox.showwarning("Validación", "El campo RUT no puede estar vacío.")
            return

        # REQUERIMIENTO EXPLÍCITO: Validación del RUT Administrador Único
        if rut_ingresado == "20123456-7":
            usuario_db = self.crud_cliente.buscar_por_rut(rut_ingresado)
            if not usuario_db:
                # Fallback de inicialización automática en caso de base de datos vacía
                usuario_db = {
                    "rut": "20123456-7",
                    "nombre": "Eduardo Sánchez (Root)",
                    "correo": "eduardo@comerciotech.cl",
                    "rol": "admin"
                }
            else:
                usuario_db["rol"] = "admin" # Forzado de seguridad

            messagebox.showinfo("Acceso Autorizado", "Credencial de Administrador detectada.")
            self.frame_principal.destroy()
            from interfaz.admin_interfaz import AdminInterfaz
            AdminInterfaz(self.root, usuario_db)
            return

        # Flujo Operacional para Clientes Comunes
        try:
            usuario_db = self.crud_cliente.buscar_por_rut(rut_ingresado)
            
            if not usuario_db:
                messagebox.showerror("Acceso Denegado", f"El RUT {rut_ingresado} no existe en la colección cliente.")
                return

            # Sanitización de rol para clientes comunes
            nombre = usuario_db.get("nombre", "Cliente")
            messagebox.showinfo("Acceso Autorizado", f"Sesión iniciada: {nombre}")
            
            self.frame_principal.destroy()
            from interfaz.cliente_interfaz import ClienteInterfaz
            ClienteInterfaz(self.root, usuario_db)

        except Exception as e:
            messagebox.showerror("Error", f"Fallo al leer base de datos: {e}")