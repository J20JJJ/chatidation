import tkinter as tk
from tkinter import messagebox

class TicTacToe:
    def __init__(self, root):
        self.root = root
        self.root.title("3 en Raya")
        self.root.geometry("400x400")
        self.buttons = [[None for _ in range(3)] for _ in range(3)]
        self.current_player = "X"
        self.create_board()

    def create_board(self):
        for row in range(3):
            for col in range(3):
                button = tk.Button(self.root, text="", font="Arial 20 bold", width=5, height=2,
                                   command=lambda r=row, c=col: self.on_click(r, c))
                button.grid(row=row, column=col)
                self.buttons[row][col] = button

    def on_click(self, row, col):
        if not self.buttons[row][col].cget("text"):
            self.buttons[row][col].config(text=self.current_player)
            if self.check_winner():
                messagebox.showinfo("3 en Raya", f"¡El jugador {self.current_player} ha ganado!")
                self.reset_board()
            elif self.is_board_full():
                messagebox.showinfo("3 en Raya", "¡Es un empate!")
                self.reset_board()
            else:
                self.current_player = "O" if self.current_player == "X" else "X"

    def check_winner(self):
        for row in range(3):
            if self.buttons[row][0].cget("text") == self.buttons[row][1].cget("text") == self.buttons[row][2].cget("text") != "":
                return True
        for col in range(3):
            if self.buttons[0][col].cget("text") == self.buttons[1][col].cget("text") == self.buttons[2][col].cget("text") != "":
                return True
        if self.buttons[0][0].cget("text") == self.buttons[1][1].cget("text") == self.buttons[2][2].cget("text") != "":
            return True
        if self.buttons[0][2].cget("text") == self.buttons[1][1].cget("text") == self.buttons[2][0].cget("text") != "":
            return True
        return False

    def is_board_full(self):
        for row in range(3):
            for col in range(3):
                if self.buttons[row][col].cget("text") == "":
                    return False
        return True

    def reset_board(self):
        for row in range(3):
            for col in range(3):
                self.buttons[row][col].config(text="")
        self.current_player = "X"

if __name__ == "__main__":
    root = tk.Tk()
    game = TicTacToe(root)
    root.mainloop()
