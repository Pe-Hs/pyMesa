import os
import sys

import requests
import ipaddress

import tkinter as tk
import customtkinter

from tkinter import filedialog, messagebox

from PIL import Image, ImageTk

import numpy as np

import matplotlib.pyplot as plt
import matplotlib.animation as animation

from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

# def load_and_resize_image(file_path, size):
#     image = Image.open(resource_path(file_path))
#     image = image.resize(size, Image.Resampling.LANCZOS)  # Redimensionar la imagen
#     return ImageTk.PhotoImage(image)

def open_file(event=None):
    filepath = filedialog.askopenfilename()

def select_file():
    filepath = filedialog.askopenfilename()
    # if filepath:
    #     port = port_entry.get()
    #     baudrate = int(sub_entry.get())
    #     send_file_to_arduino(port, baudrate, filepath)


def load_and_resize_image(file_path):
    return Image.open(resource_path(file_path))

def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)

def on_drag_start(event):
    global x, y
    x = event.x
    y = event.y

def on_drag_motion(event, root):
    delta_x = event.x - x
    delta_y = event.y - y

    new_x = root.winfo_x() + delta_x
    new_y = root.winfo_y() + delta_y

    root.geometry(f"+{new_x}+{new_y}")

def toggle_maximize_restore(root, button):
    if root.state() == 'zoomed':
        root.state('normal')
        button.configure(text="+") 
    else:
        root.state('zoomed')
        button.configure(text="−") 

# ----------------------------------------------------------------

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

tiempo = []

def update(frame):
    if not result_data or not amplitud or not frecuencia:
        return ax,

    inf = result_data.get("inf", False) if result_data else False
    max_time = frame * 0.1 if inf else duracion

    x = np.linspace(0, max_time , 1000) 
    y =  amp_slider.get() * np.sin(2 * np.pi * fre_slider.get() * (x - 0.01 * frame))

    amplitud.append(amp_slider.get())

    ax.clear()

    ax.plot(x, y, '#ee7218')
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
    ani.event_source.stop()
    # canvas.draw()

def start_animation():
    global ani, result_data

    amp = str(amp_slider.get())
    freq = str(fre_slider.get())

    result_data = {
        "amp" : f"{float(amp):.2f}",
        "freq": f"{float(freq):.2f}",
        "dur" : 10,  
        "inf" : True
    }

    plot_graph_sen()
    if ani is not None:
        canvas.draw()
        ani.event_source.start()

def stop_animation():
    global ani
    if ani is not None:
        ani.event_source.stop()

def reset_graph():
    global ani, ax, result_data, amplitud

    result_data = None

    if ani is not None:
        ani.event_source.stop()  

    amplitud = []
    ax.clear()
    ax.set_xlim(0, 1)
    ax.set_ylim(-1, 1)
    canvas.draw()
    animate()

def on_window_configure(event):
    global animating
    if animating and ani is not None:
        animating = False
        ani.event_source.stop()
    
    root.after(800, restart_animation)

def restart_animation():
    global animating
    if not animating and ani is not None:
        animating = True
        ani.event_source.start()

def next_frame():
    global frame_index
    if ani:
        ani.event_source.stop()

def prev_frame():
    global frame_index
    if ani:
         ani.event_source.stop()

# ----------------------------

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
                img_status.configure(image=onlin_img)
                status_label.configure(text="Conectado")
            else:
                img_status.configure(image=error_img)
                status_label.configure(text="Error")
        except requests.Timeout:
                img_status.configure(image=disco_img)
                status_label.configure(text="TimeOut")
        except requests.RequestException:
                img_status.configure(image=error_img)
                status_label.configure(text="Error")

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
            ip_label.configure(text=f"{result_conn["ip"]}")
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
        dura_entry.configure(state='disabled')
    
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
            amp_label.configure(text=f"{float(result_data["amp"])} mm")
            freq_label.configure(text=f"{float(result_data["freq"])} hz")
            if result_data["inf"]:
                dura_label.configure(text="Infinito")
            else:
                dura_label.configure(text=f"{float(result_data['dur'])} seg")
            plot_graph_sen()
        except tk.TclError as e:
            print(f"Error al actualizar las etiquetas: {e}")
    else:
        root.after(100, check_result_data)

# -------------------------------

def update_ampl(value):
    global ani, result_data

    amp = str(amp_slider.get())
    freq = str(fre_slider.get())

    result_data = {
        "amp" : f"{float(amp):.2f}",
        "freq": f"{float(freq):.2f}",
        "dur" : 10,  
        "inf" : True
    }
    print(result_data)
    amp_label.configure(text=f"{int(value)} mm")
    send_info_table()
    # plot_graph_sen()

def update_freq(value):
    global ani, result_data

    amp = str(amp_slider.get())
    freq = str(fre_slider.get())

    result_data = {
        "amp" : f"{float(amp):.2f}",
        "freq": f"{float(freq):.2f}",
        "dur" : 10,  
        "inf" : True
    }
    print(result_data)
    freq_label.configure(text=f"{float(value):.2f} Hz")
    send_info_table()
    # plot_graph_sen()

# -------------------------------

def show_frame(frame):
    slider_control.grid_forget()
    frame.grid(row=0, column=0, sticky="nsew")

# -------------------------------

def send_info_table():
    global result_data, result_conn
    if result_conn is not None and result_data is not None:
        try:
            ip = result_conn["ip"]
            response = requests.post(f'http://{ip}', json=result_data)
            
            if response.status_code == 200:
                d = ''
                #messagebox.showinfo("Enviado", f"Los datos se enviaron Correctamente")
            else:
                d = ''
                #messagebox.showwarning("Advertencia", f"La IP {ip} respondió con estado {response.status_code}.")

        except requests.Timeout:
            d = ''
            #messagebox.showwarning("Advertencia", f"La solicitud a {ip} superó el tiempo de espera")
        except requests.RequestException as e:
            d = ''
            #messagebox.showerror("Error", f"Error al hacer la solicitud a {ip}")
    else:
        d = ''
        #messagebox.showwarning("Advertencia", "Verificar medios de Conexion o datos")

# --------------------------------------------------------------------------

root = customtkinter.CTk()
# root.overrideredirect(True)

root.iconbitmap('./img/NCN.ico')

root.title("NCN | Shake Table Controller - Nuevo Control")
root.geometry("800x600")

fig, ax = plt.subplots()
text_artist = None

amplitud = []
frecuencia = []

duracion = 1
ani = None
infinite_duration = customtkinter.BooleanVar(value=False)

# customtkinter.set_appearance_mode("light") 
# customtkinter.set_default_color_theme("blue")

open_img  = customtkinter.CTkImage(load_and_resize_image("./img/dark-open.png"),    size=(32,32))
save_img  = customtkinter.CTkImage(load_and_resize_image("./img/dark-save.png"),    size=(32,32))
dsen_img  = customtkinter.CTkImage(load_and_resize_image("./img/dark-send.png"),    size=(32,32))
conn_img  = customtkinter.CTkImage(load_and_resize_image("./img/dark-connect.png"), size=(32,32))

back_img  = customtkinter.CTkImage(load_and_resize_image("./img/dark-back.png"),    size=(32,32))
next_img  = customtkinter.CTkImage(load_and_resize_image("./img/dark-next.png"),    size=(32,32))
start_img = customtkinter.CTkImage(load_and_resize_image("./img/dark-play.png"),    size=(32,32))
pause_img = customtkinter.CTkImage(load_and_resize_image("./img/dark-pause.png"),   size=(32,32))
sstop_img = customtkinter.CTkImage(load_and_resize_image("./img/dark-stop.png"),    size=(32,32))

contr_img = customtkinter.CTkImage(load_and_resize_image("./img/dark-control.png"), size=(32,32))
quake_img = customtkinter.CTkImage(load_and_resize_image("./img/dark-quake.png"),   size=(32,32))

help_img =  customtkinter.CTkImage(load_and_resize_image("./img/dark-help.png"),    size=(32,32))

send_img  = customtkinter.CTkImage(load_and_resize_image("./img/enviar.png"),       size=(32,32))

onlin_img = customtkinter.CTkImage(load_and_resize_image("./img/status_online.png"),size=(16,16))
error_img = customtkinter.CTkImage(load_and_resize_image("./img/status_error.png"), size=(16,16))

disco_img = customtkinter.CTkImage(load_and_resize_image("./img/status_disconected.png"), size=(16,16))
ncn_img   = customtkinter.CTkImage(load_and_resize_image("./img/NCN.ico"), size=(16,16))

ancho_pantalla = root.winfo_screenwidth() 
alto_pantalla = root.winfo_screenheight() 

ancho_ventana = 850
alto_ventana = 500

posicion_x = (ancho_pantalla - ancho_ventana) // 2 
posicion_y = (alto_pantalla - alto_ventana) // 2

root.geometry(f"{ancho_ventana}x{alto_ventana}+{posicion_x}+{posicion_y}")
root.minsize(800, 500)

bold_font = customtkinter.CTkFont(weight="bold")

# -------------------------


root.grid_rowconfigure(0, weight=1)  
root.grid_columnconfigure(1, weight=1)

frame = customtkinter.CTkFrame(root)
frame.grid(row=0, column=0, rowspan=9, sticky="ns")

frame.grid_rowconfigure(8, weight=1)

# -------------------------

open_button = customtkinter.CTkButton(frame, width=32, height=32,  fg_color="transparent", hover_color="#ee7218", image=open_img, text="", command=select_file)
open_button.grid(row=0, column=0, sticky="n")

# -------------------------

separator = customtkinter.CTkFrame(frame, width=1, height=2, fg_color="#d6d6d6")
separator.grid(row=1, column=0, padx=5, pady=2, sticky="we")

# -------------------------

conn_button = customtkinter.CTkButton(frame, width=32, height=32,  fg_color="transparent", hover_color="#ee7218", image=conn_img, text="", command=show_connect_dialog)
conn_button.grid(row=2, column=0, sticky="n")

# -------------------------

separator_2 = customtkinter.CTkFrame(frame, width=1, height=2, fg_color="#d6d6d6")
separator_2.grid(row=3, column=0, padx=5, pady=2, sticky="we")

# -------------------------

harm_button = customtkinter.CTkButton(frame, width=32, height=32,  fg_color="transparent", hover_color="#ee7218", image=contr_img, text="", command=show_form_dialog)
harm_button.grid(row=4, column=0, sticky="n")

quake_button = customtkinter.CTkButton(frame, width=32, height=32, fg_color="transparent", hover_color="#ee7218", image=quake_img, text="")
quake_button.grid(row=5, column=0, sticky="n")

# -------------------------

separator_3 = customtkinter.CTkFrame(frame, width=1, height=2, fg_color="#d6d6d6")
separator_3.grid(row=6, column=0, padx=5, pady=2, sticky="we")

# -------------------------

send_button = customtkinter.CTkButton(frame, width=32, height=32, fg_color="transparent", hover_color="#ee7218", image=dsen_img, text="")
send_button.grid(row=7, column=0, sticky="n")

# -------------------------

frame.grid_rowconfigure(8, weight=1)

exit_button = customtkinter.CTkButton(frame, width=32, height=32,  fg_color="transparent", hover_color="#ee7218", image=help_img, text="")
exit_button.grid(row=9, column=0, sticky="s") 

# -------------------------

animating = True
frame_index = 0

canvas = FigureCanvasTkAgg(fig, master=root)
canvas.get_tk_widget().grid(row=0, column=1, sticky="SNEW")

root.bind("<Configure>", on_window_configure)

# ---------------------------

graph_control = customtkinter.CTkFrame(root)
graph_control.grid(row=1, column=1, sticky="ew")

# back_button = customtkinter.CTkButton(graph_control, width=32, height=32,  fg_color="transparent", hover_color="#ee7218", image=back_img, text="", command=prev_frame)
# back_button.grid(row=0, column=0, sticky="n")

play_button = customtkinter.CTkButton(graph_control, width=32, height=32,  fg_color="transparent", hover_color="#ee7218", image=start_img, text="", command=start_animation)
play_button.grid(row=0, column=0, sticky="n")

pause_button = customtkinter.CTkButton(graph_control, width=32, height=32, fg_color="transparent", hover_color="#ee7218", image=pause_img, text="", command=stop_animation)
pause_button.grid(row=0, column=1, sticky="n")

# next_button = customtkinter.CTkButton(graph_control, width=32, height=32, fg_color="transparent", hover_color="#ee7218", image=next_img, text="", command=next_frame)
# next_button.grid(row=0, column=3, sticky="n")

reset_button = customtkinter.CTkButton(graph_control, width=32, height=32, fg_color="transparent", hover_color="#ee7218", image=sstop_img, text="", command=reset_graph)
reset_button.grid(row=0, column=2, sticky="n")

save_button = customtkinter.CTkButton(graph_control, width=32, height=32,  fg_color="transparent", hover_color="#ee7218", image=save_img, text="", command=lambda: show_frame(slider_control))
save_button.grid(row=0, column=3, sticky="n")

# ---------------------------

slider_control = customtkinter.CTkFrame(root)
slider_control.grid(row=2, column=1, sticky="ew")

customtkinter.CTkLabel(slider_control, text="Amplitud (mm): ", font=bold_font ).grid(row=0, column=0)

amp_slider = customtkinter.CTkSlider(slider_control, from_=1, to=60, number_of_steps=60, command=update_ampl)
amp_slider.grid(row=0, column=1)


customtkinter.CTkLabel(slider_control, text="Frecuencia (Hz): " , font=bold_font ).grid(row=0, column=2)

fre_slider = customtkinter.CTkSlider(slider_control, from_=0, to=10, number_of_steps=1000, command=update_freq)
fre_slider.grid(row=0, column=3)

# ---------------------------

footer = customtkinter.CTkFrame(root)
footer.grid(row=3, column=1, sticky="ew")

footer.grid_columnconfigure(10, weight=1)

img_status = customtkinter.CTkLabel(footer, text="", image=disco_img)
img_status.grid(row=0, column=0)

status_label  = customtkinter.CTkLabel(footer, text="Desconectado ")
status_label.grid(row=0, column=1, padx=1)

ip_label  = customtkinter.CTkLabel(footer, text="0.0.0.0")
ip_label.grid(row=0, column=2)

# --------------------------

separator_footer = customtkinter.CTkFrame(footer, width=1, height=1, fg_color="#d6d6d6")
separator_footer.grid(row=0, column=3, sticky="ns", padx=5, pady=2)

# --------------------------

customtkinter.CTkLabel(footer, text="Amplitud:" , font=bold_font ).grid(row=0, column=4)

amp_label  = customtkinter.CTkLabel(footer, text=f"{amp_slider.get()} mm")
amp_label.grid(row=0, column=5, padx=3)

customtkinter.CTkLabel(footer, text="Frecuencia:", font=bold_font).grid(row=0, column=6)

freq_label = customtkinter.CTkLabel(footer, text=f"{fre_slider.get()} Hz")
freq_label.grid(row=0, column=7, padx=3)

customtkinter.CTkLabel(footer, text="Duracion:", font=bold_font).grid(row=0, column=8)

dura_label = customtkinter.CTkLabel(footer, text="0.00")
dura_label.grid(row=0, column=9, padx=3)


customtkinter.CTkLabel(footer, text="", image=ncn_img).grid(row=0, column=11)
customtkinter.CTkLabel(footer, text="NCN | Nuevo Control").grid(row=0, column=12, padx=5)

# ----------------------------

result_data = None
result_conn = None

# ---------------------------

root.mainloop()


# # -------------------------

# frame_control = customtkinter.CTkFrame(root, corner_radius=0)
# frame_control.grid(row=0, column=1, sticky="ew")

# frame_control.bind("<Button-1>", on_drag_start)
# frame_control.bind("<B1-Motion>", lambda event: on_drag_motion(event, root))

# # -------------------------

# minim_button = customtkinter.CTkButton(frame_control, width=55, height=32, corner_radius=0, fg_color="transparent", text="-", command=root.iconify)
# minim_button.grid(row=0, column=0, sticky="e")

# maxim_button = customtkinter.CTkButton(frame_control, width=55, height=32, corner_radius=0, fg_color="transparent", text="+",  command=lambda: toggle_maximize_restore(root, maxim_button))
# maxim_button.grid(row=0, column=1, sticky="e")

# close_button = customtkinter.CTkButton(frame_control, width=55, height=32, corner_radius=0, fg_color="transparent", hover_color="#e81123", text="x", command=root.destroy)
# close_button.grid(row=0, column=3, sticky="e")

# frame_control.grid_columnconfigure(0, weight=1)
# frame_control.grid_columnconfigure(1, weight=0)
# frame_control.grid_columnconfigure(2, weight=0)
# frame_control.grid_columnconfigure(3, weight=0)

# # -------------------------