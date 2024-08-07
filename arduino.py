import requests
import tkinter as tk
import ipaddress

import os
import sys

from tkinter import filedialog, messagebox

import numpy as np

import matplotlib.pyplot as plt
import matplotlib.animation as animation

from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

from PIL import Image, ImageTk


# ----------------------------

def plot_graph_sen():
    global text_artist, duracion, ani
    try:
        amp = result_data["amp"]
        freq = result_data["freq"]
        dur = result_data["dur"]
        inf = result_data["inf"]

        if amp and freq and (dur or inf):
            if is_float(amp) and is_float(freq) and (is_float(dur) or inf):
                amplitud.append(float(amp))
                frecuencia.append(float(freq))
                duracion = float(dur) if not inf else 10
                if ani is not None:
                    ani.event_source.stop() 
                animate()
            else:
                messagebox.showinfo("Info", "Los datos deben ser números.")
        else:
            messagebox.showinfo("Info", "Ingrese datos completos.")
    except KeyError as e:
        messagebox.showerror("Error", f"Falta el valor: {e}")
    except ValueError as e:
        messagebox.showerror("Error", f"Valor inválido: {e}")
    except Exception as e:
        messagebox.showerror("Error", f"Ocurrió un error inesperado: {e}")

def init():
    ax.clear()
    ax.set_xlim(0, 1)
    ax.set_ylim(-1, 1)
    ax.set_xlabel("Tiempo (s)")
    ax.set_ylabel("Amplitud (mm)")
    ax.grid(True)
    return ax,

def update(frame):
    if not result_data or not amplitud or not frecuencia:
        return ax,
    inf = result_data.get("inf", False) if result_data else False
    max_time = frame * 0.1 if inf else duracion

    x = np.linspace(0, max_time , 1000)
    y = amplitud[-1] * np.sin(2 * np.pi * frecuencia[-1] * (x - 0.01 * frame))

    ax.clear()

    ax.plot(x, y, 'b-')
    if inf:
        ax.set_xlim(0, min(max_time * 2, frame * 0.1))  
    else:
        ax.set_xlim(0, duracion)

    if amplitud:
        ax.set_ylim(float(-1.5 * max(amplitud)), float(1.5 * max(amplitud)))

    # ax.text(0.81, 1.05, f'PGA: FF cm/s²', horizontalalignment='left', verticalalignment='top',
    # transform=ax.transAxes,fontsize=10, bbox=dict(facecolor='white', edgecolor='none', pad=1))
    
    ax.set_xlabel("Tiempo (s)")
    ax.set_ylabel("Amplitud (mm)")
    ax.grid(True)

    return ax,

def animate():
    global ani

    if not result_data:
        return
    
    inf = result_data.get("inf", False) if result_data else False
    dur = float(result_data["dur"]) if not inf else 10
    
    frames = None if inf else int(dur * 100)
    interval = 1000 / 30 
    ani = animation.FuncAnimation(fig, update, init_func=init, frames=frames, interval=interval, blit=False, cache_frame_data=False)
    canvas.draw()

def start_animation():
    global ani
    if ani is not None:
        ani.event_source.start()

def stop_animation():
    global ani
    if ani is not None:
        ani.event_source.stop()

def reset_graph():
    global fig, ax, ani, result_data

    result_data = None

    if ani is not None:
        ani.event_source.stop()  

    amp_label.config(text="0.00")
    freq_label.config(text="0.00")
    dura_label.config(text="0.00")

    ax.clear()
    ax.set_xlim(0, 1)  
    ax.set_ylim(-1, 1)
    ax.set_xlabel("Tiempo (s)")
    ax.set_ylabel("Amplitud (mm)")
    ax.grid(True)

    ani = animation.FuncAnimation(fig, update, init_func=init, frames=100, interval=50, blit=False)
    canvas.draw() 

# ------------------------------

def is_float(value):
    try:
        number = float(value)
        return True
    except ValueError:
        return False

def max_abs_value(array):
    max_abs = max(abs(x) for x in array)
    
    for x in array:
        if abs(x) == max_abs:
            return x

# --------------------------------

def dialog_connect_server(root):
    global result_conn

    def on_submit():
        global result_conn

        ip = ip_entry.get().strip()

        if not ip :
            dialog.focus_set()
            messagebox.showwarning("Advertencia", "La Direccion IP es obligatoria", parent=dialog)
            return
        
        try:
            ipaddress.ip_address(ip)
        except ValueError:
            messagebox.showerror("Error", "Dirección IP no válida", parent=dialog)
            return
        
        try:
            response = requests.get(f'http://{ip}')

            if response.status_code == 200:
                img_status.config(image=onlin_img)
                status_label.config(text="Conectado")
            else:
                img_status.config(image=error_img)
                status_label.config(text="Error")
        except requests.Timeout:
                img_status.config(image=disco_img)
                status_label.config(text="TimeOut")
        except requests.RequestException:
                img_status.config(image=error_img)
                status_label.config(text="Error")

        result_conn = {
            "ip" : ip,
        }

        dialog.destroy()
    

    dialog = tk.Toplevel(root)
    dialog.title("Conexion con la Mesa")

    dialog.grid_rowconfigure(0, weight=1)

    tk.Label(dialog, text="Direccion IP:"  ).grid(row=0, column=0, padx=10, pady=10)

    ip_entry = tk.Entry(dialog)

    ip_entry.grid(row=0, column=1, padx=10, pady=10)

    submit_button = tk.Button(dialog, text="Aplicar", command=on_submit)
    submit_button.grid(row=4, columnspan=2, padx=10, pady=10, sticky="ew")

    center_dialog(dialog, root)

def show_connect_dialog(event=None):
    global result_conn
    result_conn = None 
    dialog_connect_server(root)
    root.after(100, check_result_conn)

def check_result_conn():
    if result_conn is not None:
        try:
            ip_label.config(text=f"{result_conn["ip"]}")
        except tk.TclError as e:
            print(f"Error al actualizar las etiquetas: {e}")
    else:
        root.after(100, check_result_conn)

# --------------------------------

def center_dialog(dialog, root):

    root_width = root.winfo_width()
    root_height = root.winfo_height()
    
    root_x = root.winfo_rootx()
    root_y = root.winfo_rooty()
    
    dialog.update_idletasks()
    dialog_width = dialog.winfo_width()
    dialog_height = dialog.winfo_height()
    
    x = root_x + (root_width - dialog_width) // 2
    y = root_y + (root_height - dialog_height) // 2
    
    dialog.geometry(f"{dialog_width}x{dialog_height}+{x}+{y}")
    dialog.minsize(dialog_width, dialog_height)

# -------------------------------

def create_form_dialog(root):
    global result_data

    def on_submit():
        global result_data

        amp = ampl_entry.get().strip()
        freq = freq_entry.get().strip()
        dur = dura_entry.get().strip()
        inf = infin_dur.get()

       
        if not amp or not freq:
            dialog.focus_set()
            messagebox.showwarning("Advertencia", "Amplitud y Frecuencia son obligatorios.", parent=dialog)
            return
        
        if not inf and not dur:
            dialog.focus_set()
            messagebox.showwarning("Advertencia", "Por favor, ingrese la duración o marque 'Duración Infinita'.", parent=dialog)
            return

        if not is_float(amp) or not is_float(freq):
            dialog.focus_set()
            messagebox.showwarning("Advertencia", "Amplitud y Frecuencia deben ser números válidos.", parent=dialog)
            return
        
        if not inf and (not is_float(dur) or float(dur) <= 0):
            dialog.focus_set()
            messagebox.showwarning("Advertencia", "Duración debe ser un número positivo.", parent=dialog)
            return
        
        result_data = {
            "amp" : float(amp),
            "freq": float(freq),
            "dur" : float(dur) if not inf else 10,  
            "inf" : inf
        }

        dialog.destroy()
    
    def disable_dur():
        dura_entry.delete(0, tk.END)
        dura_entry.config(state='disabled')
    
    dialog = tk.Toplevel(root)
    dialog.title("Frecuencia Harmonica")

    infin_dur = tk.BooleanVar(value=False)
    tk.Label(dialog, text="Amplitud (mm): "  ).grid(row=0, column=0, padx=10, pady=10)
    tk.Label(dialog, text="Frecuencia (hz): ").grid(row=1, column=0, padx=10, pady=10)
    tk.Label(dialog, text="Duracion (seg): " ).grid(row=2, column=0, padx=10, pady=10)
    
    ampl_entry = tk.Entry(dialog)
    freq_entry = tk.Entry(dialog)
    dura_entry = tk.Entry(dialog)
    infi_check = tk.Checkbutton(dialog, text="Duración Infinita", variable=infin_dur, command=disable_dur)
      

    ampl_entry.grid(row=0, column=1, padx=10, pady=10)
    freq_entry.grid(row=1, column=1, padx=10, pady=10)
    dura_entry.grid(row=2, column=1, padx=10, pady=10)
    infi_check.grid(row=3, column=1, columnspan=2, sticky="ew")
    
    submit_button = tk.Button(dialog, text="Aplicar", command=on_submit)
    submit_button.grid(row=4, columnspan=2, padx=10, pady=10, sticky="ew")

    center_dialog(dialog, root)

def show_form_dialog():
    global result_data
    result_data = None  # Reiniciar la variable global
    create_form_dialog(root)
    root.after(100, check_result_data)

def check_result_data():
    if result_data is not None:
        try:
            amp_label.config(text=f"{float(result_data["amp"])} mm")
            freq_label.config(text=f"{float(result_data["freq"])} hz")
            if result_data["inf"]:
                dura_label.config(text="Infinito")
            else:
                dura_label.config(text=f"{float(result_data['dur'])} seg")
            plot_graph_sen()
        except tk.TclError as e:
            print(f"Error al actualizar las etiquetas: {e}")
    else:
        root.after(100, check_result_data)

# --------------------------------

def open_file(event=None):
    filepath = filedialog.askopenfilename()

def select_file():
    filepath = filedialog.askopenfilename()
    # if filepath:
    #     port = port_entry.get()
    #     baudrate = int(sub_entry.get())
    #     send_file_to_arduino(port, baudrate, filepath)

def load_and_resize_image(file_path, size):
    image = Image.open(resource_path(file_path))
    image = image.resize(size, Image.Resampling.LANCZOS)  # Redimensionar la imagen
    return ImageTk.PhotoImage(image)

def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)

def exit_application():
    root.destroy()
    
def on_window_move(event):
    global ani

    new_x = root.winfo_x()
    new_y = root.winfo_y()

    if new_x != root.winfo_x() or new_y != root.winfo_y():
        if ani is not None:
            ani.event_source.stop()


def send_info_table():
    global result_data, result_conn
    if result_conn is not None and result_data is not None:
        try:
            ip = result_conn["ip"]
            response = requests.post(f'http://{ip}', json=result_data)
            
            if response.status_code == 200:
                messagebox.showinfo("Enviado", f"Los datos se enviaron Correctamente")
                # print(f"La IP {ip} respondió con estado 200 OK.")
                # print("Respuesta del servidor:", response.json())
            else:
                messagebox.showwarning("Advertencia", f"La IP {ip} respondió con estado {response.status_code}.")
                # print(f"La IP {ip} respondió con estado {response.status_code}.")
                # print("Respuesta del servidor:", response.text)

        except requests.Timeout:
            messagebox.showwarning("Advertencia", f"La solicitud a {ip} superó el tiempo de espera")
        except requests.RequestException as e:
            messagebox.showerror("Error", f"Error al hacer la solicitud a {ip}")
    else:
        messagebox.showwarning("Advertencia", "Verificar medios de Conexion o datos")

# ----- Tool Kit ---------

root = tk.Tk()
root.title("NCN | ShakeTable Controller")


ancho_pantalla = root.winfo_screenwidth() 
alto_pantalla = root.winfo_screenheight() 

ancho_ventana = 900
alto_ventana = 650

posicion_x = (ancho_pantalla - ancho_ventana) // 2 
posicion_y = (alto_pantalla - alto_ventana) // 2

root.geometry(f"{ancho_ventana}x{alto_ventana}+{posicion_x}+{posicion_y}")
root.minsize(800, 650)

# root.grid_columnconfigure(2, weight=1)    
root.grid_rowconfigure(1, weight=1)
for i in range(5):
    root.grid_columnconfigure(i, weight=1)

# -------------------------

menu_bar = tk.Menu(root)

file_menu = tk.Menu(menu_bar, tearoff=False)  
menu_bar.add_cascade(label="Archivo", menu=file_menu)

# ------------------------

file_menu.add_command(label="Abrir", accelerator="Ctrl+O", command=select_file)

file_menu.add_command(label="Guardar", command=select_file)

# -----------------------

file_menu.add_separator()  

file_menu.add_command(label="Salir", command=exit_application)

# ------------------------

opt_bar = tk.Menu(root)
opt_menu = tk.Menu(menu_bar, tearoff=0)  
menu_bar.add_cascade(label="Opciones", menu=opt_menu)

opt_menu.add_command(label="Harmonico", command=show_form_dialog)

# ------------------------

connect_bar = tk.Menu(root)
connect_menu = tk.Menu(menu_bar, tearoff=0)  
menu_bar.add_cascade(label="Conectar", menu=connect_menu)

connect_menu.add_command(label="Conectar", accelerator="Ctrl+L", command=show_connect_dialog)

# ------------------------

help_bar = tk.Menu(root)
help_menu = tk.Menu(menu_bar, tearoff=0)  
menu_bar.add_cascade(label="Ayuda", menu=help_menu)

# ------------------------


root.bind_all("<Control-l>", show_connect_dialog)
root.bind_all("<Control-L>", show_connect_dialog)

root.bind_all("<Control-s>", open_file)
root.bind_all("<Control-S>", open_file)

root.bind_all("<Control-O>", open_file)
root.bind_all("<Control-o>", open_file)

root.config(menu=menu_bar)

# -------------------

fig, ax = plt.subplots()
text_artist = None

amplitud = []
frecuencia = []

duracion = 1
ani = None
infinite_duration = tk.BooleanVar(value=False)

frame = tk.Frame(root, relief="raised", bd=1)
frame.grid(row=0, column=0, columnspan=5, padx=2, pady=2, sticky="ew")

# -------------------------

open_img = load_and_resize_image("./img/carpeta.png", (30, 30))
save_img = load_and_resize_image("./img/salvar.png",  (30, 30))

start_img = load_and_resize_image("./img/start.png", (32, 32)) 
pause_img = load_and_resize_image("./img/pause.png", (32, 32))
sstop_img = load_and_resize_image("./img/sstop.png", (32, 32))

contr_img = load_and_resize_image("./img/control.png", (32, 32))

onlin_img = load_and_resize_image("./img/status_online.png", (16, 16))
error_img = load_and_resize_image("./img/status_error.png", (16, 16))
disco_img = load_and_resize_image("./img/status_disconected.png", (16, 16))

send_img  = load_and_resize_image("./img/enviar.png", (32, 32))

# --------------------------

open_button = tk.Button(frame, text="Abrir", image=open_img, relief="flat")
open_button.grid(row=0, column=0)

save_button = tk.Button(frame, text="Guardar", image=save_img, relief="flat")
save_button.grid(row=0, column=1)

# -------------------------

separator = tk.Frame(frame, width=1, bg="#d6d6d6")
separator.grid(row=0, column=2, sticky="ns", padx=5, pady=2)

# -------------------------

play_button = tk.Button(frame, text="Continuar", image=start_img, relief="flat", command=start_animation)
play_button.grid(row=0, column=3)

pause_button = tk.Button(frame, text="Pausar", image=pause_img, relief="flat", command=stop_animation)
pause_button.grid(row=0, column=4)

reset_button = tk.Button(frame, text="Reiniciar", image=sstop_img, relief="flat", command=reset_graph)
reset_button.grid(row=0, column=5)

# -------------------------

separator_2 = tk.Frame(frame, width=1, bg="#d6d6d6")
separator_2.grid(row=0, column=6, sticky="ns", padx=5, pady=2)

# -------------------------

control_button = tk.Button(frame, text="Harmonico", image=contr_img, relief="flat", command=show_form_dialog)
control_button.grid(row=0, column=7)

# -------------------------

separator_3 = tk.Frame(frame, width=1, bg="#d6d6d6")
separator_3.grid(row=0, column=8, sticky="ns", padx=5, pady=2)

# -------------------------

send_button = tk.Button(frame, text="Enviar", image=send_img, relief="flat", command=send_info_table)
send_button.grid(row=0, column=9)

# -------------------------

footer = tk.Frame(root, relief="raised", bd=1)
footer.grid(row=2, column=0, columnspan=5, sticky="ew")

img_status = tk.Label(footer, text="status", image=disco_img)
img_status.grid(row=0, column=0)

status_label  = tk.Label(footer, text="Desconectado")
status_label.grid(row=0, column=1)

ip_label  = tk.Label(footer, text="0.0.0.0")
ip_label.grid(row=0, column=2)

separator_footer = tk.Frame(footer, width=1, bg="#d6d6d6")
separator_footer.grid(row=0, column=3, sticky="ns", padx=5, pady=2)

tk.Label(footer, text="Amplitud:"  ).grid(row=0, column=4)

amp_label  = tk.Label(footer, text="0.00")
amp_label.grid(row=0, column=5)

tk.Label(footer, text="Frecuencia:").grid(row=0, column=6)

freq_label = tk.Label(footer, text="0.00")
freq_label.grid(row=0, column=7)

tk.Label(footer, text="Duracion:").grid(row=0, column=8)

dura_label = tk.Label(footer, text="0.00")
dura_label.grid(row=0, column=9)
# slider = tk.Scale(footer, from_=0, to=100, orient="horizontal", length=300, tickinterval=10, showvalue=False, sliderlength=20)
# slider.grid(row=0, column=1)

# -------------------------

canvas = FigureCanvasTkAgg(fig, master=root)
canvas.get_tk_widget().grid(row=1, column=0, columnspan=5, sticky="SNEW", padx=5, pady=5)

result_data = None
result_conn = None

root.mainloop()