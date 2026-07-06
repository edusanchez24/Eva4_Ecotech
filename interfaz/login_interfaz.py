import tkinter as tk
from tkinter import messagebox, ttk
from interfaz.cliente_interfaz import VentanaCliente
from interfaz.admin_interfaz import VentanaAdmin

class VentanaLogin:
    def __init__(self, root, db):
        self.root = root
        self.db = db
        self.root.title("EcoTech - Acceso")
        self.root.geometry("380x300")
        
        tk.Label(root, text="EcoTech Sistema Integrado", font=("Arial", 14, "bold")).pack(pady=15)
        
        # Cuadro 1: Entrada de texto (RUT o 'admin')
        tk.Label(root, text="Ingrese RUT Usuario (o 'admin'):", font=("Arial", 10)).pack(pady=2)
        self.txt_usuario = tk.Entry(root, justify="center", font=("Arial", 11))
        self.txt_usuario.pack(pady=5)
        self.txt_usuario.insert(0, "12345678-9")
        
        # Cuadro 2: Menú desplegable para elegir Rol
        tk.Label(root, text="Seleccione el Rol / Perfil:", font=("Arial", 10)).pack(pady=2)
        self.combo_rol = ttk.Combobox(root, values=["Cliente", "Administrador"], state="readonly", justify="center", font=("Arial", 10))
        self.combo_rol.pack(pady=5)
        self.combo_rol.set("Cliente") # Por defecto

        tk.Button(root, text="Ingresar al Sistema", bg="#4CAF50", fg="white", font=("Arial", 11, "bold"), command=self.ingresar).pack(pady=20)
        
    def ingresar(self):
        usuario = self.txt_usuario.get().strip()
        rol_seleccionado = self.combo_rol.get()
        
        if not usuario:
            messagebox.showwarning("Campos Vacíos", "Por favor, ingrese su RUT o identificación.")
            return

        if rol_seleccionado == "Administrador":
            if usuario.lower() == "admin":
                self.root.destroy()
                root_admin = tk.Tk()
                VentanaAdmin(root_admin, self.db)
                root_admin.mainloop()
            else:
                messagebox.showerror("Error de Acceso", "Para el rol Administrador, debe escribir 'admin' en el cuadro de usuario.")
        else:
            # Rol Cliente: Entra con cualquier RUT sin validación previa en la BD
            self.root.destroy()
            root_cliente = tk.Tk()
            VentanaCliente(root_cliente, self.db, usuario)
            root_cliente.mainloop()