# server.py
import socket
import threading

class ChatServer:
    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.clients = {}

    def start(self):
        self.server_socket.bind((self.host, self.port))
        self.server_socket.listen(5)
        print(f"Server started on {self.host}:{self.port}")

        while True:
            client_socket, address = self.server_socket.accept()
            print(f"New connection from {address}")

            client_thread = threading.Thread(target=self.handle_client, args=(client_socket,))
            client_thread.start()

    def handle_client(self, client_socket):
        while True:
            try:
                message = client_socket.recv(1024).decode('utf-8')
                if message.startswith("NICK"):
                    nickname = message.split()[1]
                    self.clients[client_socket] = nickname
                    self.broadcast(f"{nickname} joined the chat!")
                elif message.startswith("MSG"):
                    content = message[4:]
                    self.broadcast(f"{self.clients[client_socket]}: {content}", sender=client_socket)
                elif message.startswith("QUIT"):
                    self.remove_client(client_socket)
                    break
            except ConnectionResetError:
                self.remove_client(client_socket)
                break

    def broadcast(self, message, sender=None):
        for client_socket in self.clients:
            if client_socket != sender:
                client_socket.send(message.encode('utf-8'))

    def remove_client(self, client_socket):
        if client_socket in self.clients:
            nickname = self.clients[client_socket]
            del self.clients[client_socket]
            client_socket.close()
            self.broadcast(f"{nickname} left the chat!")

if __name__ == '__main__':
    server = ChatServer('localhost', 12345)
    server.start()