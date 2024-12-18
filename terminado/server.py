import socket
import threading
import os
import numpy as np
from PIL import Image
import requests
from io import BytesIO
import re
import random

server_version = "0.6"
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


def comprovar_ppt(comando, game, ipJugador, jugador):


    def borrar_partida():
        games.remove(game)
        print(games)

    def sacar_ip_del_otroJugador():
        if jugador == "1":
            target_nickname = game["jugador2"]
            if target_nickname in nicknames:
                target_index = nicknames.index(target_nickname)
                ip_del_otroJugador = clients[target_index]
        if jugador == "2":
            target_nickname = game["jugador1"]
            if target_nickname in nicknames:
                target_index = nicknames.index(target_nickname)
                ip_del_otroJugador = clients[target_index]

        return ip_del_otroJugador



    def gana_J1():
        borrar_partida()
        sacar_ip_del_otroJugador().send(f"/juego lose".encode('utf-8'))
        ipJugador.send(f"/juego win".encode('utf-8'))
        print("Jugador 1 gana")
        
    def gana_J2():
        borrar_partida()
        sacar_ip_del_otroJugador().send(f"/juego win".encode('utf-8'))
        ipJugador.send(f"/juego lose".encode('utf-8'))
        print("Jugador 2 gana")

    def empate():
        borrar_partida()
        sacar_ip_del_otroJugador().send(f"/juego empate".encode('utf-8'))
        ipJugador.send(f"/juego empate".encode('utf-8'))
        print("EMPATE")
    
    # PIEDRA PAPEL TIJERA
    if comando == "ppt":
        if game["mano_j1"] == game["mano_j2"]:
            empate()
            # print("EMPATE")
        elif game["mano_j1"] == "papel" and game["mano_j2"] == "piedra":
            gana_J1()
            # print("Jugador 1 gana")
        elif game["mano_j1"] == "piedra" and game["mano_j2"] == "papel":
            gana_J2()
            # print("Jugador 2 gana")
        elif game["mano_j1"] == "tijeras" and game["mano_j2"] == "papel":
            gana_J1()
            # print("Jugador 1 gana")
        elif game["mano_j1"] == "papel" and game["mano_j2"] == "tijeras":
            gana_J2()
            # print("Jugador 2 gana")
        elif game["mano_j1"] == "piedra" and game["mano_j2"] == "tijeras":
            gana_J1()
            # print("Jugador 1 gana")
        elif game["mano_j1"] == "tijeras" and game["mano_j2"] == "piedra":
            gana_J2()
            # print("Jugador 2 gana")
    
    # PIEDRA PAPEL TIJERA

    if comando == "tictactoe":
        tablero = game["tablero"]
        
        # Revisa filas
        for fila in tablero:
            if fila[0] == fila[1] == fila[2] and fila[0] != "":
                if fila[0] == "X":
                    gana_J1()
                    return
                elif fila[0] == "O":
                    gana_J2()
                    return

        # Revisa columnas
        for col in range(3):
            if tablero[0][col] == tablero[1][col] == tablero[2][col] and tablero[0][col] != "":
                if tablero[0][col] == "X":
                    gana_J1()
                    return
                elif tablero[0][col] == "O":
                    gana_J2()
                    return

        # Revisa diagonales
        if tablero[0][0] == tablero[1][1] == tablero[2][2] and tablero[0][0] != "":
            if tablero[0][0] == "X":
                gana_J1()
                return
            elif tablero[0][0] == "O":
                gana_J2()
                return

        if tablero[0][2] == tablero[1][1] == tablero[2][0] and tablero[0][2] != "":
            if tablero[0][2] == "X":
                gana_J1()
                return
            elif tablero[0][2] == "O":
                gana_J2()
                return

        # Revisa si hay empate (no hay espacios vacíos)
        if all(cell != "" for row in tablero for cell in row):
            empate()


        

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

                    games.append({"jugador1": nickname, "jugador2": target_nickname, "mano_j1":"", "mano_j2":""})

                    turno_retador = random.randint(0, 1)

                    if turno_retador == 0:
                        turno_rival = 1
                    elif turno_retador == 1:
                        turno_rival = 0
                    
                    print(games)

                    broadcast(f"{nickname} vs {target_nickname}".encode('utf-8'))

                    target_client.send(f"/[game] {nickname} {turno_retador}".encode('utf-8'))
                    client_socket.send(f"/[game] {target_nickname} {turno_rival}".encode('utf-8'))
                else:
                    client_socket.send(f"Usuario '{target_nickname}' no encontrado.\n".encode('utf-8'))

            elif "/JUEGO" in message.upper():         
                parts = message.split(" ", 2)
                
                # Encontrar el índice y el nombre del usuario que envió el comando
                index = clients.index(client_socket)
                nickname = nicknames[index]
                
                # Verificar si el mensaje tiene el formato esperado
                if len(parts) > 1:
                    comando = parts[1]  # El comando que el usuario quiere ejecutar

                    # Verificar si se ha especificado un movimiento en el mensaje
                    if len(parts) > 2:
                        movimiento = parts[2]  # Movimiento opcional del jugador
                    else:
                        movimiento = "Movimiento no especificado"

                    print(f"Comando: {comando}, Usuario: {nickname}, Movimiento: {movimiento}")
                    
                    if comando == "ppt":
                        for game in games:

                            if nickname == game["jugador1"]:
                                game["mano_j1"] = movimiento
                                print("el jugador1 es: " + nickname)
                                comprovar_ppt(comando, game, client_socket, "1")
                                break  
                                
                            elif nickname == game["jugador2"]:
                                game["mano_j2"] = movimiento
                                print("el jugador2 es: " + nickname)
                                comprovar_ppt(game, client_socket, "2")
                                break  
                        
                            
                        else: 
                            print("No se ha econtrado al jugador " + nickname)
                    
                    print(games)

                else:
                    comando = "Comando no especificado"
                
                # Imprimir el comando junto con el nombre del usuario
                # print(f"Comando: {comando}, Usuario: {nickname}")
                
                


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
