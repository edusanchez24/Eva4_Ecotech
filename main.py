import tkinter as tk
from tkinter import ttk
from interfaz.login_interfaz import LoginInterfaz

def main():
    root = tk.Tk()
    
    # Aplicamos un estilo visual unificado y limpio
    estilo = ttk.Style()
    estilo.theme_use("clam")
    
    # Lanzamos el control de acceso
    app = LoginInterfaz(root)
    
    root.mainloop()

if __name__ == "__main__":
    main()