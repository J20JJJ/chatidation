# client.py
import socket
import threading
import tkinter as tk
from tkinter import scrolledtext

class ChatClient:
    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.nickname = ""
        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        self.window = tk.Tk()
        self.window.title("Chat Client")

        self.chat_area = scrolledtext.ScrolledText(self.window, width=50, height=20)
        self.chat_area.pack(padx=10, pady=10)
        self.chat_area.config(state=tk.DISABLED)

        self.input_area = tk.Entry(self.window, width=50)
        self.input_area.pack(padx=10, pady=5)
        self.input_area.bind("<Return>", self.send_message)

        self.send_button = tk.Button(self.window, text="Send", command=self.send_message)
        self.send_button.pack(padx=10, pady=5)

    def connect(self):
        self.client_socket.connect((self.host, self.port))

        nickname_window = tk.Toplevel(self.window)
        nickname_window.title("Enter Nickname")

        nickname_label = tk.Label(nickname_window, text="Nickname:")
        nickname_label.pack(padx=10, pady=5)

        nickname_entry = tk.Entry(nickname_window, width=20)
        nickname_entry.pack(padx=10, pady=5)

        def set_nickname():
            self.nickname = nickname_entry.get()
            nickname_window.destroy()
            self.client_socket.send(f"NICK {self.nickname}".encode('utf-8'))
            receive_thread = threading.Thread(target=self.receive_messages)
            receive_thread.start()

        nickname_button = tk.Button(nickname_window, text="Set Nickname", command=set_nickname)
        nickname_button.pack(padx=10, pady=5)

        self.window.mainloop()

    def receive_messages(self):
        while True:
            try:
                message = self.client_socket.recv(1024).decode('utf-8')
                self.chat_area.config(state=tk.NORMAL)
                self.chat_area.insert(tk.END, message + "\n")
                self.chat_area.config(state=tk.DISABLED)
                self.chat_area.see(tk.END)
            except ConnectionAbortedError:
                break

    def send_message(self, event=None):
        message = self.input_area.get()
        self.input_area.delete(0, tk.END)
        self.client_socket.send(f"MSG {message}".encode('utf-8'))

    def disconnect(self):
        self.client_socket.send("QUIT".encode('utf-8'))
        self.client_socket.close()
        self.window.quit()

if __name__ == '__main__':
    client = ChatClient('localhost', 12345)
    client.connect()