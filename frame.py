import customtkinter as ctk

# Crear la ventana principal
root = ctk.CTk()
root.geometry("600x400")

# Crear el contenedor principal con dos columnas
frame_left = ctk.CTkFrame(root, width=150)
frame_left.grid(row=0, column=0, sticky="ns")

frame_right = ctk.CTkFrame(root)
frame_right.grid(row=0, column=1, sticky="nsew")

# Configurar columnas y filas para expandirse
root.grid_columnconfigure(1, weight=1)
root.grid_rowconfigure(0, weight=1)

# Configurar frame_right para expandirse
frame_right.grid_rowconfigure(0, weight=1)
frame_right.grid_columnconfigure(0, weight=1)

# Crear diferentes frames para la parte derecha
frame1 = ctk.CTkFrame(frame_right, fg_color="lightblue")
frame2 = ctk.CTkFrame(frame_right, fg_color="lightgreen")
frame3 = ctk.CTkFrame(frame_right, fg_color="lightcoral")

# Añadir widgets a los frames (como ejemplo)
label1 = ctk.CTkLabel(frame1, text="Frame 1")
label1.pack(pady=20)

label2 = ctk.CTkLabel(frame2, text="Frame 2")
label2.pack(pady=20)

label3 = ctk.CTkLabel(frame3, text="Frame 3")
label3.pack(pady=20)

# Función para mostrar el frame correspondiente
def show_frame(frame):
    frame1.grid_forget()
    frame2.grid_forget()
    frame3.grid_forget()
    frame.grid(row=0, column=0, sticky="nsew")

# Mostrar el primer frame por defecto
show_frame(frame1)

# Crear botones de navegación en la parte izquierda
open_button = ctk.CTkButton(frame_left, text="Open", command=lambda: show_frame(frame1))
open_button.grid(row=0, column=0, padx=10, pady=10)

save_button = ctk.CTkButton(frame_left, text="Save", command=lambda: show_frame(frame2))
save_button.grid(row=1, column=0, padx=10, pady=10)

play_button = ctk.CTkButton(frame_left, text="Play", command=lambda: show_frame(frame3))
play_button.grid(row=2, column=0, padx=10, pady=10)

root.mainloop()
