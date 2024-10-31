import socket
import os
import sys
import threading
import time
import keyboard  # Para detectar la pulsación de teclas
from plyer import notification
import tkinter as tk

version = "0.3"
contador_msg = 0  
chat_visible = -1  

def borra_backup():
    backup_path = "cliente_backup.exe"
    if os.path.exists(backup_path):
        time.sleep(2)
        try:
            os.remove(backup_path)
            print(f"'{backup_path}' eliminado.")
        except Exception as e:
            print(f"Error al eliminar '{backup_path}': {e}")

def start_game(idGame, jugador):

    def on_button_click(button_name):
        # Imprimir el botón presionado en la consola
        print(f'Botón presionado: {button_name}')
        
        # Actualizar el label con la elección del oponente
        opponent_label.config(text=f"Oponente eligió: Papel")  # Oponente fijo elige "Papel"
        
        # Determinar el resultado
        if button_name == "Piedra":
            result_label.config(text="¡Pierdes!", fg="red")
        elif button_name == "Papel":
            result_label.config(text="Empate", fg="orange")
        elif button_name == "Tijeras":
            result_label.config(text="¡Ganas!", fg="green")

    # Crear la ventana principal
    root = tk.Tk()
    root.title("Juego de Piedra, Papel o Tijeras")

    # Crear botones grandes
    button1 = tk.Button(root, text="Piedra", width=10, height=5, command=lambda: on_button_click("Piedra"))
    button2 = tk.Button(root, text="Papel", width=10, height=5, command=lambda: on_button_click("Papel"))
    button3 = tk.Button(root, text="Tijeras", width=10, height=5, command=lambda: on_button_click("Tijeras"))

    # Crear labels para mostrar la elección del oponente y el resultado
    opponent_label = tk.Label(root, text="")
    result_label = tk.Label(root, text="", font=("Arial", 16))

    # Colocar los botones en la ventana
    button1.pack(side=tk.LEFT, padx=10, pady=10)
    button2.pack(side=tk.LEFT, padx=10, pady=10)
    button3.pack(side=tk.LEFT, padx=10, pady=10)

    # Colocar los labels en la ventana
    opponent_label.pack(pady=10)
    result_label.pack(pady=10)

    # Iniciar el bucle principal
    root.mainloop()


def sensor_comandos(message):
    if "/[game]" in message:
        parts = message.split(" ", 3)
        if len(parts) < 4:
            print("mal\n".encode('utf-8'))
        else:
            idGame = parts[1]
            jugador = parts[2]
            turno = parts[3]
            print("idGame: " + idGame)
            print("jugador: " + jugador)
            print("Tu turno es: " + turno)
            start_game(idGame, jugador)

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
                print(message)

                sensor_comandos(message)

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
    start_client()
