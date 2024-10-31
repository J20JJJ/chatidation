import tkinter as tk

def on_button_click(button_name):
    # Imprimir el botón presionado en la consola
    print(f'Botón presionado: {button_name}')
    
    # Actualizar el label con la elección del oponente
    opponent_label.config(text=f"Oponente eligió: Papel")  # Oponente fijo elige "Papel"
    
    # Determinar el resultado
    if button_name == "Piedra":
        result_label.config(text="¡Pierdes!", fg="red")
    elif button_name == "Papel":
        result_label.config(text="Empate", fg="orange")
    elif button_name == "Tijeras":
        result_label.config(text="¡Ganas!", fg="green")

# Crear la ventana principal
root = tk.Tk()
root.title("Juego de Piedra, Papel o Tijeras")

# Crear botones grandes
button1 = tk.Button(root, text="Piedra", width=10, height=5, command=lambda: on_button_click("Piedra"))
button2 = tk.Button(root, text="Papel", width=10, height=5, command=lambda: on_button_click("Papel"))
button3 = tk.Button(root, text="Tijeras", width=10, height=5, command=lambda: on_button_click("Tijeras"))

# Crear labels para mostrar la elección del oponente y el resultado
opponent_label = tk.Label(root, text="")
result_label = tk.Label(root, text="", font=("Arial", 16))

# Colocar los botones en la ventana
button1.pack(side=tk.LEFT, padx=10, pady=10)
button2.pack(side=tk.LEFT, padx=10, pady=10)
button3.pack(side=tk.LEFT, padx=10, pady=10)

# Colocar los labels en la ventana
opponent_label.pack(pady=10)
result_label.pack(pady=10)

# Iniciar el bucle principal
root.mainloop()
