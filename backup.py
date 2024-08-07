import tkinter as tk
import serial
import time

import socket
import netifaces as ni
import time

import numpy as np

from tkinter import filedialog, messagebox
from serial.tools import list_ports

import matplotlib.pyplot as plt
import matplotlib.animation as animation
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

from PIL import Image, ImageTk

# def list_interfaces():
#     interfaces = ni.interfaces()
#     interfaces_red = []
#     for interface in interfaces:
#         try:
#             addrs = ni.ifaddresses(interface)
#             ip_info = addrs[ni.AF_INET][0] if ni.AF_INET in addrs else {'addr': 'No tiene IP'}
#             interfaces_red.append(ip_info)
#         except KeyError:
#             no_ip = "Red Desconectada"
#             interfaces_red.append(no_ip)
#     return interfaces_red

# def get_network_config(interface):
#     ni.ifaddresses(interface)
#     return ni.ifaddresses(interface)[ni.AF_INET][0]

# def connect_to_webserver(host, port):
#     try:
#         sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

#         sock.connect((host, port))
#         print(f"Conectado a {host}:{port}")
        
#         request = "GET / HTTP/1.1\r\nHost: {}\r\n\r\n".format(host)
#         sock.sendall(request.encode())
        
#         response = sock.recv(4096)
#         print("Respuesta del servidor:")
#         print(response.decode())
        
#         sock.close()
#     except Exception as e:
#         print(f"Error al conectar al servidor: {e}")

# def update_interfaces():
#     ports = list_interfaces()
#     port_entry.delete(0, tk.END)
#     sub_entry.delete(0, tk.END)
#     if ports:
#         port_entry.insert(0, ports[0]["addr"])
#         if 'broadcast' in ports[0]:
#             sub_entry.insert(0, ports[0]["netmask"])
#         else:
#             sub_entry.insert(0, '')
        
#         ports_list.delete(0, tk.END)
#         for port in ports:
#             if 'broadcast' in port or 'netmask' in port:
#                 ports_list.insert(tk.END, f'{port["addr"]}, {port["netmask"]},  {port["broadcast"]} ')
#             else: 
#                 ports_list.insert(tk.END, f'{port["addr"]}, --, --')
#     else:
#         messagebox.showinfo("Info", "No hay dispositivos")


# Scaneo de puertos Seriales

# def scan_ports():
#     ports = list_ports.comports()
#     arduino_ports = []
#     for port in ports:
#         try:
#             s = serial.Serial(port.device)
#             s.close()
#             arduino_ports.append(port.device)
#         except (OSError, serial.SerialException):
#             pass
#     return arduino_ports

# def update_ports():
#     ports = scan_ports()
#     port_entry.delete(0, tk.END)
#     if ports:
#         port_entry.insert(0, ports[0])
#         ports_list.delete(0, tk.END)
#         for port in ports:
#             ports_list.insert(tk.END, port)
#     else:
#         messagebox.showinfo("Info", "No hay dispositivos")


# Funcion mandar archivos por Serial Port

# def send_file_to_arduino(port, baudrate, filepath):
#     try:
#         with open(filepath, 'r') as file:
#             data = file.read()
#         with serial.Serial(port, baudrate, timeout=1) as ser:
#             time.sleep(2)
#             ser.write(data.encode('utf-8'))
#             print(f"Data sent from file: {filepath} ")

#             response = ser.read(ser.in_waiting or 1)
#             print(f"Response: {response.decode('utf-8')} ")

#     except serial.SerialException as e:
#         messagebox.showerror("Serial error", f"Error: {e}")
#     except FileNotFoundError:
#         messagebox.showerror("File Error", "File not found")

def select_file():
    filepath = filedialog.askopenfilename()
    # if filepath:
    #     port = port_entry.get()
    #     baudrate = int(sub_entry.get())
    #     send_file_to_arduino(port, baudrate, filepath)


# Funciones para graficar

arr_dist = []
arr_acce = []

# fig = Figure(figsize=(5, 4), dpi=100)
# ax = fig.add_subplot(111)

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
    # ax.set_xlim(0, 2 * np.pi * duracion)
    # ax.set_xlim(0, duracion)
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

# def plot_delete_lastValue():
#     global text_artist

#     if arr_dist == [] and amp_entry == []:
#          messagebox.showinfo("Info", "No hay Datos")
#     else:
#         arr_dist.pop()
#         arr_acce.pop()

#         pga_a_value_ac1e = max_abs_value(arr_acce)

#         ax.clear()
#         ax.plot(arr_dist, arr_acce, 'b-')
#         if text_artist:
#                 text_artist.remove()  
#         text_artist = ax.text(0.81, 1.05, f'PGA: {pga_a_value_ac1e} cm/s²',
#                                 horizontalalignment='left',
#                                 verticalalignment='top',
#                                 transform=ax.transAxes,
#                                 fontsize=10,
#                                 bbox=dict(facecolor='white', edgecolor='none', pad=1))
#         ax.grid()
#         canvas.draw()
    
# def plot_delete_all():
#     global text_artist

#     respuesta = messagebox.askyesno("Confirmación", "¿Estás seguro de borrar el grafico?")
#     if respuesta:
#         arr_dist.clear()
#         arr_acce.clear()

#         pga_a_value_ac1e = 0.00

#         ax.clear()
#         ax.plot(arr_dist, arr_acce, 'b-')
#         if text_artist:
#                 text_artist.remove()  
#         text_artist = ax.text(0.81, 1.05, f'PGA: {pga_a_value_ac1e} cm/s²',
#                                 horizontalalignment='left',
#                                 verticalalignment='top',
#                                 transform=ax.transAxes,
#                                 fontsize=10,
#                                 bbox=dict(facecolor='white', edgecolor='none', pad=1))
#         ax.grid()
#         canvas.draw()

#     else:
#         return


# Funciones Complemetarias

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


def exit_application():
    root.destroy()
    
# def on_listbox_select(event):
#     seleccion = ports_list.curselection()
#     if seleccion:
#         texto = ports_list.get(seleccion)

#         port_entry.delete(0, tk.END)
#         sub_entry.delete(0, tk.END)

#         if ',' in texto:
#             split_ports = texto.split(',')
#             port_entry.insert(0, split_ports[0])
#             if len(split_ports) > 1:
#                 sub_entry.insert(0, split_ports[1])
#             else:
#                 sub_entry.insert(0, '')
#         else:
#             port_entry.insert(0, texto)
#             sub_entry.insert(0, '')


def on_window_move(event):
    global ani

    new_x = root.winfo_x()
    new_y = root.winfo_y()

    if new_x != root.winfo_x() or new_y != root.winfo_y():
        if ani is not None:
            ani.event_source.stop()


def create_form_dialog(root):
    global result_data

    def on_submit():
        global result_data

        amp = ampl_entry.get().strip()
        freq = freq_entry.get().strip()
        dur = dura_entry.get().strip()
        inf = infin_dur.get()

       
        if not amp or not freq:
            messagebox.showwarning("Advertencia", "Amplitud y Frecuencia son obligatorios.")
            return
        
        if not inf and not dur:
            messagebox.showwarning("Advertencia", "Por favor, ingrese la duración o marque 'Duración Infinita'.")
            return

        if not is_float(amp) or not is_float(freq):
            messagebox.showwarning("Advertencia", "Amplitud y Frecuencia deben ser números válidos.")
            return
        
        if not inf and (not is_float(dur) or float(dur) <= 0):
            messagebox.showwarning("Advertencia", "Duración debe ser un número positivo.")
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
    dialog.title("Formulario")

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



def open_file(event=None):
    filepath = filedialog.askopenfilename()

def load_and_resize_image(file_path, size):
    image = Image.open(file_path)
    image = image.resize(size, Image.Resampling.LANCZOS)  # Redimensionar la imagen
    return ImageTk.PhotoImage(image)

# ----- Tool Kit ---------

# list_interfaces()

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

edit_menu = tk.Menu(file_menu, tearoff=0)
file_menu.add_cascade(label="Conectar..", menu=edit_menu)

edit_menu.add_command(label="MODO ETHERNET", command=show_form_dialog)
edit_menu.add_command(label="MODO WIFI", command=lambda: print("Paste selected"))
edit_menu.add_command(label="USB", command=lambda: print("Copy selected"))

# -----------------------

file_menu.add_separator()  

file_menu.add_command(label="Salir", command=exit_application)

# ------------------------

help_bar = tk.Menu(root)
help_menu = tk.Menu(menu_bar, tearoff=0)  
menu_bar.add_cascade(label="Ayuda", menu=help_menu)

# ------------------------
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

control_button = tk.Button(frame, text="Control", image=contr_img, relief="flat", command=show_form_dialog)
control_button.grid(row=0, column=7)

# -------------------------

footer = tk.Frame(root, relief="raised", bd=1)
footer.grid(row=2, column=0, columnspan=5, sticky="ew")

tk.Label(footer, text="Amplitud:"  ).grid(row=0, column=0)

amp_label  = tk.Label(footer, text="0.00")
amp_label.grid(row=0, column=1)

tk.Label(footer, text="Frecuencia:").grid(row=0, column=2)

freq_label = tk.Label(footer, text="0.00")
freq_label.grid(row=0, column=3)

tk.Label(footer, text="Duracion:").grid(row=0, column=4)

dura_label = tk.Label(footer, text="0.00")
dura_label.grid(row=0, column=5)
# slider = tk.Scale(footer, from_=0, to=100, orient="horizontal", length=300, tickinterval=10, showvalue=False, sliderlength=20)
# slider.grid(row=0, column=1)

# -------------------------

canvas = FigureCanvasTkAgg(fig, master=root)
canvas.get_tk_widget().grid(row=1, column=0, columnspan=5, sticky="SNEW", padx=5, pady=5)

result_data = None

root.mainloop()