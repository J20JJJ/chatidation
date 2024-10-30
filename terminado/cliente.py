import socket
import os
import sys
import threading
import time
import keyboard  # Para detectar la pulsación de teclas
from plyer import notification
import tkinter as tk
from tkinter import messagebox

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
        global contador_msg, chat_visible
        while True:
            try:
                message = client_socket.recv(1024).decode('utf-8')
                if message:
                    # Si el mensaje contiene el comando para iniciar un juego, inicia la interfaz de 3 en Raya
                    if message.startswith("/tictactoe"):
                        opponent = message.split()[1]
                        print(f"Iniciando juego contra {opponent}")
                        tictactoe_game(client_socket, opponent)
                    elif message.startswith("/move"):
                        _, row, col, player = message.split()
                        tictactoe_receive_move(int(row), int(col), player)
                    elif message.startswith("/win"):
                        winner = message.split()[1]
                        tictactoe_show_winner(winner)
                    elif message.startswith("/draw"):
                        tictactoe_show_draw()
                    else:
                        print(message)
                        contador_msg += 1
                        notify()
            except Exception as e:
                print(f"Error al recibir del servidor: {e}")
                client_socket.close()
                break

    def write():
        global chat_visible
        while True:
            message = input()
            if message.startswith("/tictactoe"):
                target_nickname = message.split(" ")[1]
                client_socket.send(f"/tictactoe {target_nickname}".encode('utf-8'))
            else:
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

def tictactoe_game(client_socket, opponent):
    game_root = tk.Tk()
    game = TicTacToe(game_root, client_socket)
    game_root.title(f"3 en Raya contra {opponent}")
    game_root.geometry("400x400")
    game_root.mainloop()

def tictactoe_receive_move(row, col, player):
    if TicTacToe.current_game:
        TicTacToe.current_game.receive_move(row, col, player)

def tictactoe_show_winner(winner):
    if TicTacToe.current_game:
        TicTacToe.current_game.show_winner(winner)

def tictactoe_show_draw():
    if TicTacToe.current_game:
        TicTacToe.current_game.show_draw()

class TicTacToe:
    current_game = None

    def __init__(self, root, client_socket):
        self.root = root
        self.client_socket = client_socket
        self.current_player = "X"
        self.board = [["" for _ in range(3)] for _ in range(3)]
        self.buttons = [[None for _ in range(3)] for _ in range(3)]
        self.create_board()
        TicTacToe.current_game = self

    def create_board(self):
        for row in range(3):
            for col in range(3):
                button = tk.Button(self.root, text="", font="Arial 20 bold", width=5, height=2,
                                   command=lambda r=row, c=col: self.on_click(r, c))
                button.grid(row=row, column=col)
                self.buttons[row][col] = button

    def on_click(self, row, col):
        if not self.buttons[row][col].cget("text") and self.current_player == "X":
            self.buttons[row][col].config(text="X")
            self.board[row][col] = "X"
            self.client_socket.send(f"/move {row} {col} X".encode('utf-8'))
            self.current_player = "O"

    def receive_move(self, row, col, player):
        self.buttons[row][col].config(text=player)
        self.board[row][col] = player
        self.current_player = "X" if player == "O" else "O"

    def show_winner(self, winner):
        messagebox.showinfo("3 en Raya", f"¡El jugador {winner} ha ganado!")
        self.reset_board()

    def show_draw(self):
        messagebox.showinfo("3 en Raya", "¡Es un empate!")
        self.reset_board()

    def reset_board(self):
        for row in range(3):
            for col in range(3):
                self.buttons[row][col].config(text="")
                self.board[row][col] = ""
        self.current_player = "X"

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
