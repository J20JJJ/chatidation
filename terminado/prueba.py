import tkinter as tk
import threading

# Variable para guardar la instancia de la ventana
ventana = None

def crear_ventana():
    global ventana
    
    # Si ya existe una ventana, la destruye desde el hilo principal usando after()
    if ventana is not None:
        ventana.after(0, ventana.destroy)
    
    # Crea una nueva instancia de Tk y guarda la referencia
    ventana = tk.Tk()
    ventana.title("Ventana en Segundo Hilo")
    ventana.geometry("300x200")
    
    # Contenido de la ventana
    label = tk.Label(ventana, text="¡Hola desde la ventana en segundo hilo!")
    label.pack(pady=20)
    
    # Inicia el bucle principal de tkinter
    ventana.mainloop()

def abrir_ventana_en_hilo():
    hilo = threading.Thread(target=crear_ventana)
    hilo.start()

# Ejemplo de cómo llamar a la función
while True:
    input()
    abrir_ventana_en_hilo()  # Abre la primera ventana

# Llama a esta función otra vez cuando quieras abrir una nueva ventana
