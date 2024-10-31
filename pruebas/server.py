import socket
import threading
import random

class TicTacToeGame:
    def __init__(self):
        self.board = [' ' for _ in range(9)]
        self.current_player = 'X'

    def check_win(self):
        win_conditions = [(0, 1, 2), (3, 4, 5), (6, 7, 8), (0, 3, 6), (1, 4, 7), (2, 5, 8), (0, 4, 8), (2, 4, 6)]
        for condition in win_conditions:
            if self.board[condition[0]] == self.board[condition[1]] == self.board[condition[2]] != ' ':
                return True
        return False

    def reset_game(self):
        self.board = [' ' for _ in range(9)]
        self.current_player = 'X'

    def update_board(self, move):
        self.board[move] = self.current_player
        self.current_player = 'O' if self.current_player == 'X' else 'X'
        return self.check_win()

    def get_board_state(self):
        return ' '.join(self.board)

class ChatServer:
    def __init__(self, host='127.0.0.1', port=9999):
        self.host = host
        self.port = port
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.bind((self.host, self.port))
        self.server_socket.listen(5)
        print(f"Servidor iniciado en {host}:{port}")

        self.clients = []
        self.nicknames = []

        self.tictactoe_games = {}

        self.handle_clients()

    def handle_clients(self):
        while True:
            client, addr = self.server_socket.accept()
            print(f"Nuevo cliente conectado: {addr}")

            client_handler = threading.Thread(target=self.handle_client, args=(client,))
            client_handler.start()

    def handle_client(self, client):
        nickname = client.recv(1024).decode('utf-8')
        self.nicknames.append(nickname)
        self.clients.append(client)

        print(f"Cliente {nickname} se ha conectado.")

        client.send("NICKNAME_CONFIRMED".encode('utf-8'))

        while True:
            try:
                message = client.recv(1024).decode('utf-8')
                if message.startswith("/tictactoe"):
                    game_request = message.split()[1:]
                    if len(game_request) != 2:
                        client.send("INVALID_GAME_REQUEST".encode('utf-8'))
                        continue
                    
                    opponent_nickname = game_request[1]
                    if opponent_nickname not in self.nicknames:
                        client.send("OPPONENT_NOT_FOUND".encode('utf-8'))
                        continue
                    
                    if nickname in self.tictactoe_games:
                        client.send("ALREADY_IN_GAME".encode('utf-8'))
                        continue
                    
                    game = TicTacToeGame()
                    
                    self.tictactoe_games[nickname] = {"game": game, "opponent": opponent_nickname}
                    self.tictactoe_games[opponent_nickname] = {"game": game, "opponent": nickname}

                    client.send("GAME_CREATED".encode('utf-8'))
                else:
                    broadcast(message, nickname)
            except:
                index = self.clients.index(client)
                self.clients.remove(client)
                self.nicknames.remove(nickname)
                self.tictactoe_games.pop(nickname, None)
                self.tictactoe_games.pop(opponent, None)
                client.close()
                print(f"Cliente {nickname} desconectado.")
                break

def broadcast(message, sender):
    for client in clients:
        if client != sender:
            client.send(message.encode('utf-8'))

if __name__ == "__main__":
    chat_server = ChatServer()
