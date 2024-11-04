# server.py
import socket
import threading

# Configuración del servidor
HOST = '172.16.53.3'
PORT = 65432

# Almacenar conexiones y elecciones de jugadores
connections = []
choices = {}

# Función para manejar la conexión con cada cliente
def handle_client(conn, addr):
    print(f"[NUEVA CONEXIÓN] {addr} conectado.")
    conn.send("Bienvenido al juego de Piedra, Papel o Tijera. Haz tu elección (piedra, papel, tijera):".encode('utf-8'))
    
    try:
        # Recibir elección del jugador
        choice = conn.recv(1024).decode('utf-8').lower()
        choices[addr] = choice
        print(f"[ELECCIÓN] {addr} eligió {choice}")

        # Esperar hasta que todos los jugadores hayan elegido
        if len(choices) == len(connections):
            results = evaluate_winner()
            for c in connections:
                c.send(results.encode('utf-8'))
            reset_game()
    except:
        print(f"[ERROR] Error con la conexión {addr}")
    finally:
        conn.close()

# Función para evaluar el ganador
def evaluate_winner():
    if len(set(choices.values())) == 1:
        return "¡Empate! Todos eligieron lo mismo."
    elif ("piedra" in choices.values() and "tijera" in choices.values() and "papel" in choices.values()):
        return "¡Empate! Se eligieron todas las opciones."
    else:
        # Lógica de comparación entre jugadores
        winners = []
        for addr, choice in choices.items():
            if (choice == "piedra" and "tijera" in choices.values()) or \
               (choice == "tijera" and "papel" in choices.values()) or \
               (choice == "papel" and "piedra" in choices.values()):
                winners.append(f"Jugador {addr} con {choice}")
        return f"Ganador(es): {', '.join(winners)}"

# Función para reiniciar el juego
def reset_game():
    global choices
    choices = {}

# Iniciar el servidor
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind((HOST, PORT))
server.listen()

print("[INICIANDO] El servidor está escuchando...")
while True:
    conn, addr = server.accept()
    connections.append(conn)
    thread = threading.Thread(target=handle_client, args=(conn, addr))
    thread.start()
    print(f"[CONEXIONES ACTIVAS] {threading.activeCount() - 1}")
