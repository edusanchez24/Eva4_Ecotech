import tkinter as tk
from tkinter import messagebox
from interfaz.cliente_interfaz import VentanaCliente
from interfaz.admin_interfaz import VentanaAdmin

class VentanaLogin:
    def __init__(self, root, db):
        self.root = root
        self.db = db
        self.root.title("EcoTech - Iniciar Sesión")
        self.root.geometry("350x250")
        
        tk.Label(root, text="EcoTech Sistema Integrado", font=("Arial", 14, "bold")).pack(pady=15)
        
        tk.Label(root, text="RUT Usuario (o 'admin'):").pack()
        self.txt_user = tk.Entry(root, justify="center")
        self.txt_user.pack(pady=5)
        self.txt_user.insert(0, "12345678-9") # Ejemplo rápido
        
        tk.Label(root, text="Contraseña / Rol (admin/cliente):").pack()
        self.txt_pass = tk.Entry(root, show="*", justify="center")
        self.txt_pass.pack(pady=5)
        self.txt_pass.insert(0, "cliente") # Ejemplo rápido

        tk.Button(root, text="Ingresar al Sistema", bg="#4CAF50", fg="white", command=self.ingresar).pack(pady=15)
        
    def ingresar(self):
        usuario = self.txt_user.get().strip()
        clave = self.txt_pass.get().strip().lower()
        
        if usuario == "admin" or clave == "admin":
            self.root.destroy()
            root_admin = tk.Tk()
            VentanaAdmin(root_admin, self.db)
            root_admin.mainloop()
        else:
            # Validar si el cliente existe en la BD
            cliente = self.db.clientes.find_one({"rut": usuario})
            if cliente:
                self.root.destroy()
                root_cliente = tk.Tk()
                VentanaCliente(root_cliente, self.db, usuario)
                root_cliente.mainloop()
            else:
                messagebox.showerror("Error de Acceso", "RUT no registrado. Registre al cliente en el panel de Admin.")