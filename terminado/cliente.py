import socket
import os
import sys
import threading
import time
import keyboard  # Para detectar la pulsación de teclas
from plyer import notification

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
