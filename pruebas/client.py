import socket
import threading
import random

class Client:
    def __init__(self, host='127.0.0.1', port=9999):
        self.host = host
        self.port = port
        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.client_socket.connect((self.host, self.port))

        self.nickname = input("Ingrese un nombre de usuario: ")
        self.client_socket.send(self.nickname.encode('utf-8'))

        self.receive_thread = threading.Thread(target=self.receive)
        self.receive_thread.start()

        self.chat_window = self.create_chat_window()

    def receive(self):
        while True:
            try:
                message = self.client_socket.recv(1024).decode('utf-8')
                if message.startswith("NICKNAME_CONFIRMED"):
                    print("Tu nombre ha sido confirmado.")
                elif message.startswith("GAME_CREATED"):
                    self.create_tictactoe_game()
                else:
                    print(message)
            except:
                print("Error al recibir datos del servidor.")
                self.client_socket.close()
                break

    def send_message(self, message):
        self.client_socket.send(message.encode('utf-8'))

    def create_tictactoe_game(self):
        self.tictactoe_window = self.create_tictactoe_window()

    def create_chat_window(self):
        chat_window = ""
        chat_window += "Conectado al servidor.\n\n"
        chat_window += "Para iniciar un juego de Tictactoe, escriba:\n"
        chat_window += "/tictactoe <nombre_del_oponente>\n\n"
        chat_window += "Chat:"
        return chat_window

    def create_tictactoe_window(self):
        tictactoe_window = ""
        tictactoe_window += "Juego de Tictactoe contra " + self.nickname + "\n\n"
        tictactoe_window += "Turno de X\n\n"
        tictactoe_window += "Disponibles: "
        for i in range(9):
            if self.board[i] == ' ':
                tictactoe_window += str(i) + " "
        tictactoe_window += "\n\n"
        tictactoe_window += "Ingrese su movimiento (0-8): "
        return tictactoe_window

    def run(self):
        while True:
            command = input("\nCliente> ").strip()
            if command.lower() == 'quit':
                self.client_socket.close()
                break
            elif command.startswith('/tictactoe'):
                self.send_message(command)
            else:
                self.send_message(command)

if __name__ == "__main__":
    client = Client()
    client.run()
