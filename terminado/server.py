import socket
import threading
import os
import numpy as np
from PIL import Image
import requests
from io import BytesIO
import re
import random

server_version = "0.3"
clients = []
nicknames = []
games = []  # Diccionario para almacenar juegos en curso

def encontrar_links(texto):
    patron = r'(https?://[^\s]+)'
    patron2 = r'(http?://[^\s]+)'
    links = re.findall(patron2, texto)
    links += re.findall(patron, texto)
    if links:
        return links[0]

def image_to_ascii(image_url, width=100):
    # Verificar si el comando está incompleto
    if not image_url:
        return "Uso: /img <url>"

    # Verificar si la URL es válida
    if not re.match(r'^https?://', image_url):
        return "URL no válida"

    try:
        response = requests.get(image_url)
        img = Image.open(BytesIO(response.content))
        img = img.convert('L')
        aspect_ratio = img.height / img.width
        new_height = int(aspect_ratio * width * 0.55)
        img = img.resize((width, new_height))
        pixels = np.array(img)
        chars = np.array([' ', '.', ':', '-', '=', '+', '*', '#', '%', '@'])
        normalized_pixels = (pixels - pixels.min()) / (pixels.max() - pixels.min()) * (chars.size - 1)
        ascii_art = "\n".join("".join(chars[pixel] for pixel in row) for row in normalized_pixels.astype(int))
        return ascii_art
    except Exception as e:
        return f"Error al procesar la imagen"


def send_update(client_socket):
    try:
        file_path = "terminado/cliente.exe"
        if not os.path.exists(file_path):
            print(f"Error: El archivo de actualización '{file_path}' no existe.")
            client_socket.send("Error: No se encontró el archivo de actualización.\n".encode('utf-8'))
            return

        with open(file_path, "rb") as file:
            while (chunk := file.read(1024)):
                client_socket.send(chunk)
        print("Actualización enviada completamente.")
        client_socket.send(b"END_OF_UPDATE")
    except Exception as e:
        print(f"Error al enviar la actualización: {e}")

def handle_client(client_socket):
    try:
        client_version = client_socket.recv(1024).decode('utf-8').strip()
        print(f"Versión del cliente: {client_version}")
        
        if client_version != server_version:
            client_socket.send("Actualización disponible. Descargando...\n".encode('utf-8'))
            send_update(client_socket)
            client_socket.close()
        else:
            client_socket.send("Tu versión está actualizada.\n".encode('utf-8'))
            chat_handler_thread = threading.Thread(target=chat_handler, args=(client_socket,))
            chat_handler_thread.start()
    except Exception as e:
        print(f"Error en la comunicación con el cliente: {e}")

def chat_handler(client_socket):
    try:
        nickname = client_socket.recv(1024).decode('utf-8')
        nicknames.append(nickname)
        clients.append(client_socket)
        
        broadcast(f"{nickname} se ha unido al chat.".encode('utf-8'))
        client_socket.send("Conectado al servidor!".encode('utf-8'))

        while True:
            message = client_socket.recv(1024).decode('utf-8').strip()
            print(f"Mensaje recibido: {message}")

            if message.upper() == "/USERS":
                user_list = "Usuarios conectados:\n" + "\n".join(nicknames)
                client_socket.send(user_list.encode('utf-8'))
            
            # piedra papel tijera
            elif "/MANOS" in message.upper():

                parts = message.split(" ", 2)
                if len(parts) < 2:
                    client_socket.send("Uso: /manos <jugador>\n".encode('utf-8'))
                    continue
                target_nickname = parts[1]
                print("target_nickname: " + target_nickname)
                
                if target_nickname in nicknames:
                    target_index = nicknames.index(target_nickname)
                    target_client = clients[target_index]

                    games.append({"id":len(games), "jugador1": nickname, "jugador2": target_nickname})

                    turno_retador = random.randint(0, 1)

                    if turno_retador == 0:
                        turno_rival = 1
                    elif turno_retador == 1:
                        turno_rival = 0
                    
                    print(games)

                    broadcast(f"{nickname} vs {target_nickname}".encode('utf-8'))

                    target_client.send(f"/[game] {len(games)-1} {nickname} {turno_retador}".encode('utf-8'))
                    client_socket.send(f"/[game] {len(games)-1} {target_nickname} {turno_rival}".encode('utf-8'))
                else:
                    client_socket.send(f"Usuario '{target_nickname}' no encontrado.\n".encode('utf-8'))

            # message privado
            elif "/MSG" in message.upper():
                parts = message.split(" ", 3)
                if len(parts) < 3:
                    client_socket.send("Uso: /msg <jugador> <mensaje>\n".encode('utf-8'))
                    continue
                target_nickname = parts[1]
                print("target_nickname: " + target_nickname)
                private_message = parts[2]
                print("private_message: " + private_message)
                
                if target_nickname in nicknames:
                    target_index = nicknames.index(target_nickname)
                    target_client = clients[target_index]
                    if "/IMG" in private_message.upper():
                        image_url = encontrar_links(private_message)
                        private_message = image_to_ascii(image_url)
                    target_client.send(f"\033[91m[Privado de {nickname}]: {private_message}\033[0m".encode('utf-8'))
                    client_socket.send(f"\033[92m[Privado a {target_nickname}]: {private_message}\n\033[0m".encode('utf-8'))
                else:
                    client_socket.send(f"Usuario '{target_nickname}' no encontrado.\n".encode('utf-8'))
            elif "/IMG" in message.upper():
                image_url = encontrar_links(message)
                img = image_to_ascii(image_url)
                broadcast("\n".join(img.splitlines()).encode('utf-8'))
            else:
                broadcast(f"{nickname} {message}".encode('utf-8'))
    except Exception as e:
        print(f"Error en chat_handler: {str(e)}")
        if client_socket in clients:
            index = clients.index(client_socket)
            clients.remove(client_socket)
            client_socket.close()
            nickname = nicknames[index]
            broadcast(f"{nickname} ha salido del chat.".encode('utf-8'))
            nicknames.remove(nickname)

def broadcast(message):
    for client in clients:
        try:
            client.send(message)
        except Exception as e:
            print(f"Error al enviar mensaje a cliente: {e}")
            clients.remove(client)
            client.close()

def start_server():
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_SNDBUF, 2000)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_RCVBUF, 2000)
    server_socket.bind(("0.0.0.0", 12346))

    server_socket.listen(5)
    print(f"Servidor versión {server_version} escuchando en el puerto 12346...")

    while True:
        client_socket, address = server_socket.accept()
        print(f"Conexión desde {address}")
        client_handler = threading.Thread(target=handle_client, args=(client_socket,))
        client_handler.start()

if __name__ == "__main__":
    start_server()
