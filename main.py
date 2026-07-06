from config.db_connection import obtener_db
from interfaz.login_interfaz import VentanaLogin
import tkinter as tk

def main():
    db = obtener_db()
    if db is None:
        print("Cierre de emergencia: Error de persistencia de datos.")
        return
    
    root = tk.Tk()
    app = VentanaLogin(root, db)
    root.mainloop()

if __name__ == "__main__":
    main()