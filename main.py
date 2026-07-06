import tkinter as tk
from interfaz.login_interfaz import LoginInterfaz

def main():
    # Instanciamos el contenedor base de la interfaz gráfica
    root = tk.Tk()
    
    # Aplicamos un estilo visual un poco más moderno (Ttk utiliza temas nativos)
    estilo = tk.ttk.Style()
    estilo.theme_use("clam") # 'clam', 'alt' o 'default' cambian el look de los botones
    
    # Cargamos nuestra interfaz de Login pasándole la ventana raíz
    app = LoginInterfaz(root)
    
    # Mantenemos la aplicación corriendo y escuchando los clics del mouse
    root.mainloop()

if __name__ == "__main__":
    main()