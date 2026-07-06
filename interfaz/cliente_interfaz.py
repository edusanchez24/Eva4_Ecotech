import tkinter as tk
from tkinter import ttk

class ClienteInterfaz:
    def __init__(self, root, datos_cliente):
        self.root = root
        self.cliente = datos_cliente
        self.root.title(f"ComercioTech - Portal Corporativo: {self.cliente.get('nombre', 'Usuario')}")
        self.root.geometry("850x550")
        
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill="both", expand=True, padx=10, pady=10)
        
        self.tab_perfil = ttk.Frame(self.notebook)
        self.notebook.add(self.tab_perfil, text=" 👤 Mi Perfil NoSQL ")
        
        self.dibujar_perfil()

    def dibujar_perfil(self):
        frame_datos = ttk.LabelFrame(self.tab_perfil, text=" Ficha Técnica del Documento de Usuario ", padding=20)
        frame_datos.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Mapeo de campos en singular directos de MongoDB
        nombre = self.cliente.get("nombre", "No Registrado")
        rut = self.cliente.get("rut", "No Registrado")
        correo = self.cliente.get("correo", "No Registrado")
        telefono = self.cliente.get("telefono", "No Registrado")
        
        # Extracción segura de subdocumentos embebidos (direccion)
        direccion_subdoc = self.cliente.get("direccion", {})
        calle = direccion_subdoc.get("calle", "Dirección no parametrizada")
        comuna = direccion_subdoc.get("comuna", "")
        
        ttk.Label(frame_datos, text=f"Bienvenido(a), {nombre}", font=("Arial", 13, "bold"), foreground="#2980b9").pack(pady=(0, 20), anchor="w")
        
        info_cuerpo = (
            f"• Identificador RUT: {rut}\n\n"
            f"• Canal de Correo: {correo}\n\n"
            f"• Teléfono de Contacto: {telefono}\n\n"
            f"• Despacho Base: {calle} {comuna}"
        )
        
        ttk.Label(frame_datos, text=info_cuerpo, font=("Arial", 10), justify="left").pack(anchor="w")