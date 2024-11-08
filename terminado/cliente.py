import socket
import os
import sys
import threading
import time
import keyboard  # Para detectar la pulsación de teclas
from plyer import notification
import tkinter as tk

version = "0.5"
contador_msg = 0  
chat_visible = -1  

ventana_juego = None


def borra_backup():
    backup_path = "cliente_backup.exe"
    if os.path.exists(backup_path):
        time.sleep(2)
        try:
            os.remove(backup_path)
            print(f"'{backup_path}' eliminado.")
            os.system("clear")
        except Exception as e:
            print(f"Error al eliminar '{backup_path}': {e}")
            os.system("clear")


def limpiar_consola():
    if os.name == "nt":  # Para Windows
        os.system("cls")
    else:  # Para sistemas Unix (Linux, macOS)
        os.system("clear")

# Función que crea la ventana inicial y se mantiene abierta
def crear_ventana_inicial():
    global ventana_juego
    ventana_juego = tk.Tk()
    ventana_juego.title("Ventana Principal")
    ventana_juego.geometry("300x200")  # Tamaño inicial
    ventana_juego.protocol("WM_DELETE_WINDOW", lambda: None)  # Evitar que se cierre
    ventana_juego.withdraw()  # Empezamos con la ventana invisible
    ventana_juego.mainloop()

# Actualizar la ventana existente para el juego
def iniciar_juego(client_socket):
    # Hacer visible la ventana y limpiar el contenido
    ventana_juego.deiconify()
    for widget in ventana_juego.winfo_children():
        widget.destroy()

    # Función para enviar la jugada
    def enviar_jugada(jugada):
        client_socket.send(f"/juego ppt {jugada}".encode('utf-8'))
        # Bloquear los botones después de seleccionar
        btn_piedra.config(state="disabled")
        btn_papel.config(state="disabled")
        btn_tijeras.config(state="disabled")

    # Crear botones de juego
    btn_piedra = tk.Button(ventana_juego, text="Piedra", command=lambda: enviar_jugada("piedra"))
    btn_papel = tk.Button(ventana_juego, text="Papel", command=lambda: enviar_jugada("papel"))
    btn_tijeras = tk.Button(ventana_juego, text="Tijeras", command=lambda: enviar_jugada("tijeras"))

    # Posicionar botones
    btn_piedra.pack(padx=10, pady=5)
    btn_papel.pack(padx=10, pady=5)
    btn_tijeras.pack(padx=10, pady=5)

    # Actualizar la ventana
    ventana_juego.update()

def sensor_comandos(message, client_socket):
    if "/[game]" in message:
        parts = message.split(" ", 2)
        if len(parts) < 3:
            print("".encode('utf-8'))
        else:
            jugador = parts[1]
            turno = parts[2]
            
            # print("jugador: " + jugador)
            # print("Tu turno es: " + turno)

            # Iniciar el juego en el mismo hilo de la ventana base
            iniciar_juego(client_socket)
            return False

    elif message == "/juego win":
        mostrar_resultado("¡Has ganado!", "green")
        return False

    elif message == "/juego lose":
        mostrar_resultado("¡Has perdido!", "red")
        return False

    elif message == "/juego empate":
        mostrar_resultado("¡Empate!", "orange")
        return False
    else:
        return True

def mostrar_resultado(mensaje, color):
    if ventana_juego is not None:
        for widget in ventana_juego.winfo_children():
            widget.destroy()

        # Crear un nuevo label para mostrar el resultado
        resultado_label = tk.Label(ventana_juego, text=mensaje, fg=color, font=("Helvetica", 24))
        resultado_label.pack(padx=20, pady=20)

        # Botón para limpiar y ocultar la ventana sin cerrar el programa
        btn_cerrar = tk.Button(ventana_juego, text="Cerrar", command=ocultar_ventana)
        btn_cerrar.pack(pady=10)

        ventana_juego.update()

# Función que limpia y oculta la ventana
def ocultar_ventana():
    for widget in ventana_juego.winfo_children():
        widget.destroy()  # Limpiar todos los widgets
    ventana_juego.withdraw()  # Ocultar la ventana
        

def chat(client_socket):
    global chat_visible
    nickname = input("Elige tu apodo: ")
    client_socket.send(nickname.encode('utf-8'))  

    def receive():
        global contador_msg
        while True:
            try:
                message = client_socket.recv(1024).decode('utf-8')
                if not message:
                    break
                

                if sensor_comandos(message, client_socket):
                    print(message)

                contador_msg += 1
            except:
                print("Error al recibir mensaje.")
                break
            
    def write():
        global chat_visible
        while True:
            message = input()
            client_socket.send(message.encode('utf-8'))
            
    def notify():
        global contador_msg, chat_visible
        chat_visible += 5
        display_message = f"Tienes {contador_msg} mensajes sin leer"
        if contador_msg > chat_visible:
            notification.notify(
                title="Chat Notificación",
                message=display_message,
                app_icon=None,
                timeout=1
            )

    def check_for_user_list():
        while True:
            if keyboard.is_pressed('tab'):
                client_socket.send("/USERS".encode('utf-8'))
                time.sleep(0.5)

    receive_thread = threading.Thread(target=receive)
    receive_thread.start()
    write_thread = threading.Thread(target=write)
    write_thread.start()
    tab_thread = threading.Thread(target=check_for_user_list)
    tab_thread.start()

def receive_update(client_socket):
    update_path = "cliente_new.exe"
    with open(update_path, "wb") as file:
        while True:
            data = client_socket.recv(1024)
            if data == b"END_OF_UPDATE":
                break
            if not data:
                print("Error al recibir la actualización.")
                return
            file.write(data)
    print("Actualización recibida y guardada como 'cliente_new.exe'.")

    client_socket.close()
    os.rename(sys.argv[0], "cliente_backup.exe")
    os.rename(update_path, sys.argv[0])
    print("Actualización aplicada. Reiniciando...")
    os.execl(sys.executable, sys.executable, *sys.argv)

def start_client():
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect(("172.16.53.3", 12346))
    client_socket.send(version.encode('utf-8'))  
    
    server_message = client_socket.recv(1024).decode('utf-8')  
    print(server_message)
    
    if "actualizada" not in server_message:  
        receive_update(client_socket)
    else:
        chat(client_socket) 

if __name__ == "__main__":
    borra_backup()
    threading.Thread(target=crear_ventana_inicial, daemon=True).start()
    start_client()
