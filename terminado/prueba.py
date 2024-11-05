import tkinter as tk
import threading  # Importar threading para usar hilos

def crear_ventana(client_socket):
    global ventana_juego

    ventana_juego = tk.Tk()
    ventana_juego.title("Piedra, Papel o Tijeras")

    # Crear botones de juego
    btn_piedra = tk.Button(ventana_juego, text="Piedra", command=lambda: print("piedra"))
    btn_papel = tk.Button(ventana_juego, text="Papel", command=lambda: print("papel"))
    btn_tijeras = tk.Button(ventana_juego, text="Tijeras", command=lambda: print("tijeras"))

    # Posicionar botones
    btn_piedra.pack(padx=10, pady=5)
    btn_papel.pack(padx=10, pady=5)
    btn_tijeras.pack(padx=10, pady=5)

    # Mostrar ventana
    ventana_juego.protocol("WM_DELETE_WINDOW", ventana_juego.destroy)  # Manejar el cierre de la ventana
    ventana_juego.mainloop()

def iniciar_juego(client_socket):
    # Crear un nuevo hilo para ejecutar crear_ventana
    hilo_ventana = threading.Thread(target=crear_ventana, args=(client_socket,))
    hilo_ventana.start()  # Iniciar el hilo para no bloquear el input en consola

def sensor_comandos(message, client_socket):
    if "/[game]" in message:
        parts = message.split(" ", 2)
        if len(parts) < 3:
            print("mal\n".encode('utf-8'))
        else:
            jugador = parts[1]
            turno = parts[2]
            
            print("jugador: " + jugador)
            print("Tu turno es: " + turno)

            # Iniciar el juego en un nuevo hilo
            iniciar_juego("1")

    elif message == "/juego win":
        mostrar_resultado("¡Has ganado!", "green")

    elif message == "/juego lose":
        mostrar_resultado("¡Has perdido!", "red")

    elif message == "/juego empate":
        mostrar_resultado("¡Empate!", "orange")

def mostrar_resultado(mensaje, color):
    if ventana_juego is not None:
        for widget in ventana_juego.winfo_children():
            widget.destroy()

        resultado_label = tk.Label(ventana_juego, text=mensaje, fg=color, font=("Helvetica", 24))
        resultado_label.pack(padx=20, pady=20)

        btn_cerrar = tk.Button(ventana_juego, text="Cerrar", command=ventana_juego.destroy)
        btn_cerrar.pack(pady=10)

        ventana_juego.update()

def ya():
    while True:
        sensor_comandos(input("> "), "1")

if __name__ == "__main__":
    ya()
