import socket
import threading
import os
import numpy as np
from PIL import Image
import requests
from io import BytesIO
import re

server_version = "0.3"
clients = []
nicknames = []
games = {}  # Diccionario para almacenar juegos en curso

def encontrar_links(texto):
    patron = r'(https?://[^\s]+)'
    patron2 = r'(http?://[^\s]+)'
    links = re.findall(patron2, texto)
    links += re.findall(patron, texto)
    if links:
        return links[0]

def image_to_ascii(image_url, width=100):
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

def start_tictactoe(player1_socket, player2_socket, player1_nick, player2_nick):
    # Crear una nueva partida y enviarla a los jugadores
    game_key = (min(player1_nick, player2_nick), max(player1_nick, player2_nick))
    games[game_key] = [["" for _ in range(3)] for _ in range(3)]
    player1_socket.send(f"/tictactoe {player2_nick}".encode('utf-8'))
    player2_socket.send(f"/tictactoe {player1_nick}".encode('utf-8'))
    print(f"Juego iniciado entre {player1_nick} y {player2_nick}")


def update_tictactoe(game_key, row, col, player, socket):
    # Ajustar la clave del juego con el mismo orden en el diccionario `games`
    game_key = (min(game_key[0], game_key[1]), max(game_key[0], game_key[1]))
    if game_key in games:
        board = games[game_key]
        board[row][col] = player
        player1, player2 = game_key
        # Enviar la jugada a ambos jugadores
        for sock in [clients[nicknames.index(player1)], clients[nicknames.index(player2)]]:
            sock.send(f"/move {row} {col} {player}".encode('utf-8'))

        # Chequear ganador o empate después del movimiento
        if check_winner(board, player):
            for sock in [clients[nicknames.index(player1)], clients[nicknames.index(player2)]]:
                sock.send(f"/win {player}".encode('utf-8'))
            del games[game_key]
        elif is_board_full(board):
            for sock in [clients[nicknames.index(player1)], clients[nicknames.index(player2)]]:
                sock.send("/draw".encode('utf-8'))
            del games[game_key]
    else:
        socket.send("Error: no se encontró la partida.\n".encode('utf-8'))


def check_winner(board, player):
    for row in board:
        if all([cell == player for cell in row]):
            return True
    for col in range(3):
        if all([board[row][col] == player for row in range(3)]):
            return True
    if all([board[i][i] == player for i in range(3)]) or all([board[i][2 - i] == player for i in range(3)]):
        return True
    return False

def is_board_full(board):
    return all([cell != "" for row in board for cell in row])

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
            elif message.upper().startswith("/TICTACTOE "):
                target_nick = message.split(" ")[1]
                if target_nick in nicknames:
                    start_tictactoe(client_socket, clients[nicknames.index(target_nick)], nickname, target_nick)
                    print(games)
                else:
                    client_socket.send(f"Usuario '{target_nick}' no encontrado.\n".encode('utf-8'))
            elif message.upper().startswith("/MOVE "):
                _, row, col, player = message.split(" ")
                row, col = int(row), int(col)
                game_key = (nickname, nicknames[clients.index(client_socket)]) if (nickname, nicknames[clients.index(client_socket)]) in games else (nicknames[clients.index(client_socket)], nickname)
                update_tictactoe(game_key, row, col, player, client_socket)
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
