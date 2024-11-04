# client_gui.py
import socket
import tkinter as tk
from tkinter import messagebox

# Configuración del cliente
HOST = '172.16.53.3'
PORT = 65432

# Conectar con el servidor
client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect((HOST, PORT))

# Función para enviar elección al servidor
def send_choice(choice):
    try:
        client.send(choice.encode('utf-8'))
        result = client.recv(1024).decode('utf-8')
        result_label.config(text=f"Resultado: {result}")
    except:
        messagebox.showerror("Error", "Error de conexión con el servidor.")
    finally:
        client.close()

# Configuración de la ventana con tkinter
root = tk.Tk()
root.title("Juego Piedra, Papel o Tijera")

# Etiqueta de bienvenida
welcome_label = tk.Label(root, text="Elige tu opción:", font=("Arial", 14))
welcome_label.pack(pady=10)

# Botones de elección
button_frame = tk.Frame(root)
button_frame.pack(pady=10)

btn_piedra = tk.Button(button_frame, text="Piedra", font=("Arial", 12), width=10, command=lambda: send_choice("piedra"))
btn_piedra.grid(row=0, column=0, padx=5)

btn_papel = tk.Button(button_frame, text="Papel", font=("Arial", 12), width=10, command=lambda: send_choice("papel"))
btn_papel.grid(row=0, column=1, padx=5)

btn_tijera = tk.Button(button_frame, text="Tijera", font=("Arial", 12), width=10, command=lambda: send_choice("tijera"))
btn_tijera.grid(row=0, column=2, padx=5)

# Etiqueta para mostrar el resultado
result_label = tk.Label(root, text="Esperando resultado...", font=("Arial", 14))
result_label.pack(pady=20)

# Iniciar la ventana
root.mainloop()
