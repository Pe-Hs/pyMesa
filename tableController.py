import math
import os
import sys
import re
import tempfile
import webbrowser

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

# ------------------------------------

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

# -------------------------------------------

tiempo = []

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
    
    amp_val = float(amp_input.get()) if amp_input.get() else 1 
    fre_val = float(freq_input.get()) if freq_input.get() else 1 

    x = np.linspace(0, duracion, 1000)
    y = amp_val * np.sin(2 * np.pi * fre_val * x)
    ax.plot(x, y, '#ee7218')

    ax.set_xlim(0, 1)
    ax.set_ylim(float(-1.5 * amp_val), float(1.5 * amp_val))

    ax.set_xlabel("Tiempo (s)")
    ax.set_ylabel("Amplitud (mm)")
    ax.grid(True)

    return ax,

def update(frame):
    if len(ax.lines) > 1:  
        ax.lines[-1].remove()
    
    if len(ax.collections) > 0:
        ax.collections[-1].remove()
    
    if len(ax.texts) > 0:
        ax.texts[-1].remove()

    vertical_line_x = frame * 0.01  
    if vertical_line_x <= duracion:
        ax.axvline(x=vertical_line_x, color='blue', linestyle='--')
    
    amp_val = float(amp_input.get()) if amp_input.get() else 1
    fre_val = float(freq_input.get()) if freq_input.get() else 1
    point_y = amp_val * np.sin(2 * np.pi * fre_val * vertical_line_x) 

    ax.scatter(vertical_line_x, point_y, color='red', zorder=5) 

    ax.text(1 , 1.05, f'x = {vertical_line_x:.2f} seg, y = {point_y:.2f} mm',
            fontsize=10, verticalalignment='top', horizontalalignment='right', color='black', transform=ax.transAxes)

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
    global ani, result_data, result_conn

    amp_l = amp_label.cget("text")[:-3]
    fre_l = freq_label.cget("text")[:-3]

    result_data = {
        "amp" : f"{float(amp_l):.2f}",
        "freq": f"{float(fre_l):.2f}",
        "dur" : 1,  
        "inf" : False
    }
    
    # plot_graph_sen()

    # if ani is not None:
    #     canvas.draw()
    #     ani.event_source.start()
    # else:
    #     return
    
    # --------------------------

    send_info_table()

    if conn_estab:
        plot_graph_sen()

        if ani is not None:
            canvas.draw()
            ani.event_source.start()
    else:
        return
    
def stop_animation():
    global ani
    if ani is not None:
        ani.event_source.stop()
    pause_loop()

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
        # ani.event_source.start()

# ----------------------------

def dialog_connect_server(root):
    global result_conn

    def on_submit():
        global result_conn

        ip =  ip_entry.get().strip() if ip_entry.get() != ""  else opt_value.get().strip() 
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
            response = requests.get(f'http://{ip}', timeout=5)

            if response.status_code == 200:
                img_status.configure(image=onlin_img)
                status_label.configure(text="Conectado")
            else:
                img_status.configure(image=error_img)
                status_label.configure(text="Error")
        except requests.Timeout:
                img_status.configure(image=disco_img)
                status_label.configure(text="TimeOut")
        except requests.RequestException as e:
                img_status.configure(image=error_img)
                status_label.configure(text="Error")

        result_conn = {
            "ip" : ip,
        }

        dialog.destroy()
    
    def radio_change():
        if opt_value.get() == "enable":
            ip_entry.configure(state="normal")
        else:
            ip_entry.configure(state="disabled")

    dialog = tk.Toplevel(root)
    dialog.title("Conexion con la Mesa")

    dialog.grid_columnconfigure(0, weight=1)

    opt_value = tk.StringVar(value="none")

    rad_utp = tk.Radiobutton(dialog, text="Conexion Cable Internet", variable=opt_value, value="192.168.1.170", command=radio_change)
    rad_utp.grid(row=0, column=0)

    rad_wif = tk.Radiobutton(dialog, text="Conexion WIFI", variable=opt_value, value="192.168.1.160", command=radio_change)
    rad_wif.grid(row=1, column=0)

    rad_ent = tk.Radiobutton(dialog, text="Connexion IP", variable=opt_value, value="enable", command=radio_change)
    rad_ent.grid(row=2, column=0)

    ip_entry = tk.Entry(dialog)
    ip_entry.grid(row=3, column=0)

    ip_entry.configure(state="disabled")

    submit_button = tk.Button(dialog, text="Aplicar", command=on_submit)
    submit_button.grid(row=4, columnspan=2, padx=5, pady=5, sticky="ew")

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
                d = ''
                # dura_label.configure(text="Infinito")
            else:
                d = ''
                # dura_label.configure(text=f"{float(result_data['dur'])} seg")
            plot_graph_sen()
        except tk.TclError as e:
            print(f"Error al actualizar las etiquetas: {e}")
    else:
        root.after(100, check_result_data)

# -------------------------------

def update_ampl(value):
    global ani, result_data

    amp = str(amp_input.get()) if str(amp_input.get()) else value

    m_dist = calibrate_slider(amp, 30, 1015, 0, 30)

    max_vel = get_max_vel(m_dist)

    freq = str(freq_input.get()) if str(freq_input.get()) else value 

    m_speed = calibrate_slider(freq, 20, 1015, 0, max_vel)

    new_speed = freq * (2 * math.PI)

    result_data = {
        "amp" : f"{float(amp):.2f}",
        "freq": f"{float(freq):.2f}",
        "f_amp" : f"{float(amp):.2f}",
        "f_freq": f"{float(m_speed):.2f}",
        "dur" : 1,  
        "inf" : False
    }

    # send_info_table()

    amp_label.configure(text=f"{int(m_dist)} mm")
    freq_label.configure(text=f"{float(new_speed):.2f} Hz")
    # plot_graph_sen()

def update_freq(value):
    global ani, result_data

    amp = str(amp_input.get()) if str(amp_input.get()) else value

    m_dist = calibrate_slider(amp, 30, 1015, 0, 30)

    max_vel = get_max_vel(m_dist)

    freq = str(freq_input.get()) if str(freq_input.get()) else value

    m_speed = calibrate_slider(freq, 20, 1015, 0, max_vel)

    new_speed = m_speed / (2 * 3.14)

    result_data = {
        "amp" : f"{float(amp):.2f}",
        "freq": f"{float(freq):.2f}",
        "f_amp" : f"{float(amp):.2f}",
        "f_freq": f"{float(m_speed):.2f}",
        "dur" : 1,  
        "inf" : False
    }

    # send_info_table()
    amp_label.configure(text=f"{float(m_dist)} mm")
    freq_label.configure(text=f"{float(new_speed):.2f} Hz")
    # plot_graph_sen()

def calibrate_slider(val, in_min, in_max, out_min, out_max):
    return (float(val) - in_min) * (out_max - out_min) / (in_max - in_min) + out_min

def get_max_vel(dist):
    return (0.00159962) * pow(dist, 3) - 0.41303215 * pow(dist, 2) + 20.83780711 * dist + 103.82640002

# -------------------------------

def get_files_arduino():
    global result_data, result_conn, result_file, result_txt
    try:
        if not result_conn:
            messagebox.showwarning("Advertencia", "No se puede establecer conexion o no ingreso IP")
            return
        else:
            result_txt = None

            ip = result_conn["ip"]
            response = requests.get(f'http://{ip}')

            if response.status_code == 200:
                file_list_response = response.json()
                result_file = response.json()

                file_list.delete(0, tk.END)

                for file in file_list_response:
                    file_list.insert(tk.END, f'{file["filename"]}')
            else:
                return

    except:
        messagebox.showwarning("Advertencia", "No se pudo obtener lista de Archivos")

def on_listbox_select_OG(event):
    global result_txt, result_conn, result_file

    seleccion = file_list.curselection()

    fileSelName = file_list.get(seleccion)

    obj_select = None

    for obj in result_file:
        if obj["filename"] == str(fileSelName):
            obj_select = obj
            break
    
    last_index = 0

    if not result_conn and not result_file:
        messagebox.showwarning("Advertencia", "No se puede establecer conexion o no ingreso IP")
        return
    
    if seleccion:
        file_name = file_list.get(seleccion)
        ip = result_conn["ip"]

        loop_req = int(obj_select["size"]) // 5000

        send_req = {
            "filename": file_name,
            "limit": 5000
        }

        response = requests.post(f'http://{ip}', json=send_req)
        
        if response.status_code == 200:
            req_resp = response.json()
            result_txt = req_resp["data"]

            for i in range(loop_req):
                send_req = {
                    "filename" : file_name,
                    "limit" : 5000,
                    "index" : 5000 * (i+1),
                }

                response = requests.post(f'http://{ip}', json=send_req)
                if response.status_code == 200:
                    req_resp = response.json()
                    result_txt += req_resp["data"]
                    last_index = req_resp["endIndex"]
                else:
                    result_txt += ""

            send_req = {
                "filename": file_name,
                "limit" : 5000,
                "index" : last_index,
            } 

            response = requests.post(f'http://{ip}', json=send_req)

            if response.status_code == 200:
                req_resp = response.json()
                result_txt += req_resp["data"]
            else:
                result_txt += ""

            messagebox.showinfo("Completo", "Se recibieron los datos")
        else:
            messagebox.showwarning("Advertencia", "No se reicibio datos")
            return

def on_listbox_select(event):
    global result_txt, result_conn, result_file, result_filename

    seleccion = file_list.curselection()

    if not seleccion:
        messagebox.showwarning("Advertencia", "No se seleccionó ningún archivo o la lista esta Vacia")
        return
    
    result_filename = file_list.get(seleccion)

def plot_file_from_arduino():
    global result_txt_arduino

    if not result_txt_arduino:
        messagebox.showwarning("Advertencia", "No se encontro datos para Graficar")
        return
    
    lineas = result_txt_arduino.splitlines()

    x = []
    y = []
    v = []

    for linea in lineas:
        print(linea)
        valores = linea.split()

        x.append(float(valores[0]))
        y.append(float(valores[1]))
        v.append(float(valores[2]))
    
    ax_2.clear()

    ar_x = np.array(x)
    ar_y = np.array(y)
    ar_v = np.array(v)

    for a, b, c in zip(ar_x, ar_y, ar_v):
        print(a, " -- ", b, " -- ", c)

    cycles = len(ar_x) - 1
    time =  ar_x[cycles] - ar_x[0]
    clc_frq = cycles / time

    ax_2.plot(ar_x, ar_y, '#ee7218')
    ax_2.set_xlabel("Tiempo (s)")
    ax_2.set_ylabel("Amplitud")

    index_max = np.argmax(np.abs(ar_y))

    plt.grid()

    ax_2.grid(True)
    ax_2.text(0, 1.05, f'Freq = {clc_frq:.2f} Hz | {len(ar_x)}',
            fontsize=10, verticalalignment='top', horizontalalignment='left', color='black', transform=ax_2.transAxes)
    
    ax_2.text(1, 1.05, f'Max Amp.= {ar_y[index_max]:.3f} mm',
            fontsize=10, verticalalignment='top', horizontalalignment='right', color='black', transform=ax_2.transAxes)

    canvas_2.draw()

def plot_file_from_local():
    global result_txt, result_unit

    if not result_txt:
        messagebox.showwarning("Advertencia", "No se encontro datos para Graficar")
        return
    
    lineas = result_txt.splitlines()
    
    x = []
    y = []

    for linea in lineas:
        valores = linea.split()

        try:
            x.append(float(valores[0]))
            y.append(float(valores[1]))
        except:
            result_txt = ''
            messagebox.showwarning("Advertencia", "El archivo no tiene el Formato Correcto")
            return
        
    
    ax_2.clear()

    ar_x = np.array(x)
    a_y = np.array(y)

    if result_unit == "cm":
        ar_y = a_y * 10
    elif result_unit == "m":
        ar_y = a_y * 1000
    else:
        ar_y = a_y * 1

    cycles = len(ar_x) - 1
    time =  ar_x[cycles] - ar_x[0]
    clc_frq = cycles / time

    index_max = np.argmax(np.abs(ar_y))

    ax_2.plot(ar_x, ar_y, '#ee7218')
    ax_2.set_xlabel("Tiempo (s)")
    ax_2.set_ylabel("Amplitud")

    
    plt.grid()
    ax_2.grid(True)

    ax_2.text(0, 1.05, f'Freq = {clc_frq:.2f} Hz | {len(x)}',
            fontsize=10, verticalalignment='top', horizontalalignment='left', color='black', transform=ax_2.transAxes)
    
    ax_2.text(1, 1.05, f'Max Amp.= {ar_y[index_max]:.3f} mm',
            fontsize=10, verticalalignment='top', horizontalalignment='right', color='black', transform=ax_2.transAxes)

    canvas_2.draw()

# -------------------------------

def load_file_data():
    global result_txt, result_conn, result_filename, result_txt_arduino

    if not result_conn:
        messagebox.showwarning("Advertencia", "No se puede establecer conexión o no ingresó IP")
        return

    ip = result_conn["ip"]

    if not result_filename:
        messagebox.showwarning("Advertencia", "Archivo no encontrado")
        return

    obj_select = next((obj for obj in result_file if obj["filename"] == str(result_filename)), None)
    
    if not obj_select:
        messagebox.showwarning("Advertencia", "Archivo no encontrado en la lista")
        return

    file_name = result_filename
    
    loop_req = int(obj_select["size"]) // 5000

    result_txt_arduino = ""

    for i in range(loop_req + 1):
        index = 5000 * i
        send_req = {
            "filename": file_name,
            "limit": 5000,
            "index": index
        }

        try:
            response = requests.post(f'http://{ip}', json=send_req)
            response.raise_for_status() 
        except requests.RequestException as e:
            messagebox.showwarning("Advertencia", f"Error en la solicitud: {e}")
            return

        req_resp = response.json()
        result_txt_arduino += req_resp.get("data", "")

    messagebox.showinfo("Completo", "Se recibieron los datos")
    plot_file_from_arduino()

def delete_file_arduino():
    global result_conn, result_filename

    if not result_conn:
        messagebox.showwarning("Advertencia", "No se puede establecer conexión o no ingresó IP")
        return

    ip = result_conn["ip"]

    if not result_filename:
        messagebox.showwarning("Advertencia", "Archivo no encontrado")
        return
    
    send_delete = {
        "filename": result_filename,
        "action": "delete"
    }
    
    response = requests.post(f'http://{ip}', json=send_delete)

    if response.status_code == 200:
        messagebox.showinfo("Completo", "Se elimino Archivo")
        get_files_arduino()
        return
    else:
        messagebox.showwarning("Advertencia", "Error al eliminar Archivos")
        get_files_arduino()
        return    

# -------------------------------

def open_file():
    global result_txt, filename_og

    filepath = filedialog.askopenfilename(filetypes=[('Text Files', '*.txt')])

    if not filepath:
        messagebox.showwarning("Advertencia", "No se Selecciono Archivo")
        return
    
    filename_og = os.path.basename(filepath)
    # file_size = os.path.getsize(filepath)

    with open(filepath, 'rb') as file:
        result_txt = file.read()

    dialog_select_unit(root)
   

def dialog_select_unit(root):
    global result_unit

    def on_submit():
        global result_unit

        plot_file_from_local()
        show_frame(frame2)

        dialog.destroy()
    
    def radio_change():
        global result_unit
        result_unit = opt_value.get()

    dialog = tk.Toplevel(root)
    dialog.title("Conexion con la Mesa")

    dialog.grid_columnconfigure(0, weight=1)

    opt_value = tk.StringVar(value="none")

    rad_utp = tk.Radiobutton(dialog, text="Unidad en Centimetros (cm)", variable=opt_value, value="cm", command=radio_change)
    rad_utp.grid(row=0, column=0)

    rad_wif = tk.Radiobutton(dialog, text="Unidad en Milimetros (mm)", variable=opt_value, value="mm", command=radio_change)
    rad_wif.grid(row=1, column=0)

    rad_ent = tk.Radiobutton(dialog, text="Unidad en Metros (m)", variable=opt_value, value="m", command=radio_change)
    rad_ent.grid(row=2, column=0)

    submit_button = tk.Button(dialog, text="Aplicar", command=on_submit)
    submit_button.grid(row=3, columnspan=2, padx=5, pady=5, sticky="ew")

    center_dialog(dialog, root)

def upload_file_in_chunks():
    global result_txt, result_conn, temp_file, filename_og

    if not result_conn:
        messagebox.showwarning("Advertencia", "No se puede establecer conexión o no ingresó IP")
        return

    ip = result_conn["ip"]

    if not temp_file:
        messagebox.showwarning("Advertencia", "No se puede leer datos de Archivo Auto Ajustado")
        return
    
    if not filename_og:
        messagebox.showwarning("Advertencia", "No se puede obtener el Nombre del Archivo")
        return

    file_size = os.path.getsize(temp_file.name)

    print(file_size)

    progress_bar.configure(mode="determinate")  
    progress_bar.set(0)  
    progress_bar.start()
    
    with open(temp_file.name, 'rb') as file:
        total_sent = 0
        while True:
            chunk_size = calculate_bytes_for_lines(file, 100)
            print(chunk_size)
            if chunk_size == 0:
                break

            file.seek(-chunk_size, os.SEEK_CUR)  
            chunk = file.read(chunk_size)

            if not chunk:
                break

            files = {'file': (filename_og, chunk)}
            response = requests.post(f'http://{ip}', files=files)
            if response.status_code != 200:
                messagebox.showwarning("Advertencia", "Simulacion Terminada")
                break

            total_sent += len(chunk)
            progress = total_sent / file_size  
            progress_bar.set(progress)  
            progress_bar.update_idletasks()  

        progress_bar.stop()
        messagebox.showinfo("Completo", "Se enviaron los datos")

    temp_file.close()
    
    get_files_arduino()

def calculate_bytes_for_lines(file, num_lines=1000):
    total_bytes = 0
    lines_count = 0

    while lines_count < num_lines:
        char = file.read(1)
        if not char:
            break  

        total_bytes += len(char)

        if char == b'\n':  
            lines_count += 1

    return total_bytes

def resample_data():
    global result_txt, temp_file, result_unit

    if not result_txt:
        messagebox.showwarning("Advertencia", "No se encontro datos para Graficar")
        return
    
    freq_val = resample_entry.get().strip()

    if freq_val == "":
        messagebox.showwarning("Advertencia", "Debe Ingresar valor de Reesampleo")
        return
    
    try:
        freq_val = float(freq_val)
    except ValueError:
        messagebox.showwarning("Advertencia", "El valor debe ser numérico")
        return
        
    lineas = result_txt.splitlines()

    x = []
    y = []
    v = []

    for linea in lineas:
        valores = linea.split()

        x.append(float(valores[0]))
        y.append(float(valores[1]))
    
    if result_unit == "cm":
        factor = 10
    elif result_unit == "m":
        factor = 1000
    else:
        factor = 1 
    
    x = np.array(x) 
    y = np.array(y) * factor

    x_re = np.arange(x[0], x[-1], 1/freq_val)

    y_re = np.interp(x_re, x, y)

    cycles = len(x_re) - 1
    time =  x_re[cycles] - x_re[0]
    clc_frq = cycles / time

    ax_2.clear()

    # max_value = max(y_re)

    max_value = abs(y_re[np.argmax(np.abs(y_re))])

    if max_value > 30:
        y_ree = ( y_re / max_value) * 30
    else:
        y_ree = y_re

    index_max = np.argmax(np.abs(y_ree))

    # v =  np.array(abs(get_max_vel(y_ree))) 
    v = np.diff(y_ree) / np.diff(x_re)
    v = np.insert(v, 0, 0)
    v = np.abs(v)

    ax_2.plot(x_re, y_ree, '#ee7218')
    # ax_2.plot(x_re,     v, '#1344d6')

    ax_2.set_xlabel("Tiempo (s)")
    ax_2.set_ylabel("Amplitud")
    plt.grid()
    ax_2.grid(True)

    ax_2.text(0, 1.05, f'Freq = {clc_frq:.2f} Hz | Npts = {len(x_re)}',
            fontsize=10, verticalalignment='top', horizontalalignment='left', color='black', transform=ax_2.transAxes)
    
    ax_2.text(1, 1.05, f'Max Amp.= {y_ree[index_max]:.3f} mm',
            fontsize=10, verticalalignment='top', horizontalalignment='right', color='black', transform=ax_2.transAxes)

    canvas_2.draw()

    temp_file = tempfile.NamedTemporaryFile(delete=False, mode='w', suffix='.txt')

    for x_val, y_val, v_val in zip(x_re, y_ree, v):
        print(f"{x_val:.3f}", " --- ", f" {y_val:.3f}", " --- " , f"{int(v_val)}")
        temp_file.write(f"   {x_val:.3f}      {y_val}      {v_val}\n")
    
    temp_file.flush()
    
# ------------------------------

def send_info_table():
    global result_data, result_conn, conn_estab

    if result_conn is not None and result_data is not None:
        try:
            ip = result_conn["ip"]
            conn_estab = True
            response = requests.post(f'http://{ip}', json=result_data, timeout=1)
            
            if response.status_code == 200:
                messagebox.showinfo("Enviado", f"Los datos se enviaron Correctamente")

        except requests.Timeout:
            t = ''
        except requests.RequestException as e:
            y = ''
    else:
        messagebox.showwarning("Advertencia", "Verificar medios de Conexion o datos")

def pause_loop():
    global result_conn

    send_d = {
        "aa" : "aaa"
    }

    if result_conn is not None:
        try:
            ip = result_conn["ip"]
            response = requests.post(f'http://{ip}', json=send_d, timeout=1)
            
            if response.status_code == 200:
                messagebox.showinfo("Enviado", f"Los datos se enviaron Correctamente")

        except requests.Timeout:
            t = ''
        except requests.RequestException as e:
            y = ''


    else:
        messagebox.showwarning("Advertencia", "Verificar medios de Conexion o datos")

# ------------------------------

def adjust_value_amp(increment):
    current_value = amp_value.get()
    if amp_10.get():
        step = 10
    elif amp_1.get():
        step = 1
    elif amp_0_1.get():
        step = 0.1
    elif amp_0_01.get():
        step = 0.01
    else:
        step = 0
    new_value = round(current_value + step * increment, 2)    

    m_dist = calibrate_slider(new_value, 0, 30, 30, 1015)
    
    if m_dist >= 1015:
        amp_value.set(30.00)
        amp_label.configure(text=f"{float(m_dist):.2f} mm")
    elif m_dist <= 0 or new_value <= 0:
        amp_value.set(0.00)
        amp_label.configure(text=f"{float(0.00):.2f} mm")
    else:
        amp_value.set(new_value)
        amp_label.configure(text=f"{float(m_dist):.2f} mm")
    
def adjust_value_freq(increment):
    current_value = freq_value.get()
    if freq_10.get():
        step = 10
    elif freq_1.get():
        step = 1
    elif freq_0_1.get():
        step = 0.1
    elif freq_0_01.get():
        step = 0.01
    else:
        step = 0
    new_value = round(current_value + step * increment, 2)
    freq_value.set(new_value)
    
    new_speed = new_value * (2 * 3.14)

    freq_label.configure(text=f"{float(new_speed):.2f} Hz")

def create_tooltip(widget, text):
    tooltip = customtkinter.CTkLabel(root, text=text, fg_color="#333332", bg_color="transparent", text_color="white", corner_radius=5)
    
    def show_tooltip(event):
        x = widget.winfo_rootx() - root.winfo_rootx() + widget.winfo_width() + 10 
        y = widget.winfo_rooty() - root.winfo_rooty()
        tooltip.place(x=x, y=y)
    
    def hide_tooltip(event):
        tooltip.place_forget()
    
    widget.bind("<Enter>", show_tooltip)
    widget.bind("<Leave>", hide_tooltip)

# ------------------------------------

def start_simulation():
    global result_txt, result_conn, temp_file, result_filename

    if not result_conn:
        messagebox.showwarning("Advertencia", "No se puede establecer conexión o no ingresó IP")
        return

    ip = result_conn["ip"]

    if not result_filename:
        messagebox.showwarning("Advertencia", "No se puede encontrar nombre de Archivo")
        return

    send_sim = {
        "filename" : result_filename,
        "sism" : "ss"
    }

    try:
        response = requests.post(f'http://{ip}', json=send_sim)

        if response.status_code == 200:
                    messagebox.showinfo("Enviado", f"Los datos se enviaron Correctamente")

    except requests.Timeout:
        t = ''
    except requests.RequestException as e:
        y = '' 
    

# ------------------------------------

root = customtkinter.CTk()
# root.overrideredirect(True)
customtkinter.set_appearance_mode("dark")

icon_path = os.path.abspath(resource_path('./img/NCN.ico'))

root.iconbitmap( icon_path )

root.title("NCN | Shake Table Controller - Nuevo Control")
root.geometry("900x600")

fig, ax = plt.subplots()
fig_2, ax_2 = plt.subplots()

text_artist = None

amplitud = []
frecuencia = []

duracion = 1
ani = None
infinite_duration = customtkinter.BooleanVar(value=False)


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

face_img  = customtkinter.CTkImage(load_and_resize_image("./img/facebook.png"),     size=(40,40))
link_img  = customtkinter.CTkImage(load_and_resize_image("./img/linkedin.png"),     size=(40,40))
quak_img  = customtkinter.CTkImage(load_and_resize_image("./img/quakesense.png"),   size=(230,65))

onlin_img = customtkinter.CTkImage(load_and_resize_image("./img/status_online.png"),size=(16,16))
error_img = customtkinter.CTkImage(load_and_resize_image("./img/status_error.png"), size=(16,16))

disco_img = customtkinter.CTkImage(load_and_resize_image("./img/status_disconected.png"), size=(16,16))
ncn_img   = customtkinter.CTkImage(load_and_resize_image("./img/NCN.ico"), size=(16,16))
logo_img  = customtkinter.CTkImage(load_and_resize_image("./img/NCN.ico"), size=(80,80))

ancho_pantalla = root.winfo_screenwidth() 
alto_pantalla = root.winfo_screenheight() 

ancho_ventana = 1100
alto_ventana = 620

posicion_x = (ancho_pantalla - ancho_ventana) // 2 
posicion_y = (alto_pantalla - alto_ventana) // 2

root.geometry(f"{ancho_ventana}x{alto_ventana}+{posicion_x}+{posicion_y}")
root.minsize(1100, 620)

bold_font = customtkinter.CTkFont(weight="bold")

bold_font_info = customtkinter.CTkFont(weight="bold", size=20)

important_info = customtkinter.CTkFont(size=16)

root.grid_columnconfigure(1, weight=1)
root.grid_rowconfigure(0, weight=1)

# ---------------------------------------------------------------------------------

frame = customtkinter.CTkFrame(root)
frame.grid(row=0, column=0, rowspan=9, sticky="ns")

frame.grid_rowconfigure(8, weight=1)

# ------------------------------------

frame_right = customtkinter.CTkFrame(root)
frame_right.grid(row=0, column=1,rowspan=9, sticky="nsew")

frame_right.grid_rowconfigure(2, weight=1)
frame_right.grid_columnconfigure(0, weight=1)

# ------------------------------------ 

open_button = customtkinter.CTkButton(frame, width=32, height=32,  fg_color="transparent", hover_color="#ee7218", image=open_img, text="", command=open_file)
open_button.grid(row=0, column=0, sticky="n")

create_tooltip(open_button, "Abrir")

# -------------------------

separator = customtkinter.CTkFrame(frame, width=1, height=2, fg_color="#d6d6d6")
separator.grid(row=1, column=0, padx=5, pady=2, sticky="we")

# -------------------------

conn_button = customtkinter.CTkButton(frame, width=32, height=32,  fg_color="transparent", hover_color="#ee7218", image=conn_img, text="", command=show_connect_dialog)
conn_button.grid(row=2, column=0, sticky="n")

create_tooltip(conn_button, "Conectar")

# -------------------------

separator_2 = customtkinter.CTkFrame(frame, width=1, height=2, fg_color="#d6d6d6")
separator_2.grid(row=3, column=0, padx=5, pady=2, sticky="we")

# -------------------------

harm_button = customtkinter.CTkButton(frame, width=32, height=32,  fg_color="transparent", hover_color="#ee7218", image=contr_img, text="", command=lambda: show_frame(frame1))
harm_button.grid(row=4, column=0, sticky="n")

create_tooltip(harm_button, "Modo Harmonico")

quake_button = customtkinter.CTkButton(frame, width=32, height=32, fg_color="transparent", hover_color="#ee7218", image=quake_img, text="", command=lambda: show_frame(frame2))
quake_button.grid(row=5, column=0, sticky="n")

create_tooltip(quake_button, "Modo Sismo")

# -------------------------

separator_3 = customtkinter.CTkFrame(frame, width=1, height=2, fg_color="#d6d6d6")
separator_3.grid(row=6, column=0, padx=5, pady=2, sticky="we")

# -------------------------

# send_button = customtkinter.CTkButton(frame, width=32, height=32, fg_color="transparent", hover_color="#ee7218", image=dsen_img, text="")
# send_button.grid(row=7, column=0, sticky="n")

# -------------------------

frame.grid_rowconfigure(8, weight=1)

info_button = customtkinter.CTkButton(frame, width=32, height=32,  fg_color="transparent", hover_color="#ee7218", image=help_img, text="", command=lambda: show_frame(frame3))
info_button.grid(row=9, column=0, sticky="s") 

# ----------------------------------------------------------------------------------------------------------------------------------------

frame1 = customtkinter.CTkFrame(frame_right)

frame2 = customtkinter.CTkFrame(frame_right)

frame3 = customtkinter.CTkFrame(frame_right)

# -----------------------------------------------------------------------------------------

info_panel = customtkinter.CTkFrame(frame3)
info_panel.grid(row=0, column=0, rowspan=8, sticky="nswe")

info_panel.grid_columnconfigure(0, weight=1)
info_panel.grid_rowconfigure(0, weight=1)
info_panel.grid_rowconfigure(11, weight=1)

customtkinter.CTkLabel(info_panel, text="", image=logo_img).grid(row=1, column=0, sticky="nswe")

customtkinter.CTkLabel(info_panel, text="NCN | Nuevo Control EIRL", font=bold_font_info).grid(row=2, column=0, sticky="nswe")

customtkinter.CTkLabel(info_panel, text="Soluciones sísmicas para un mundo en constante movimiento.").grid(row=3, column=0, sticky="we")

customtkinter.CTkLabel(info_panel, text="informes@ncn.pe | +51 945 962 848", font=bold_font).grid(row=4, column=0, sticky="we")

rd_panel = customtkinter.CTkFrame(info_panel)
rd_panel.grid(row=5, column=0)
rd_panel.grid_columnconfigure(0, weight=1)
rd_panel.grid_columnconfigure(3, weight=1)

link_link = customtkinter.CTkLabel(rd_panel, text="", image=link_img)
link_link.grid(row=0, column=1, padx=5, pady=5)

face_link = customtkinter.CTkLabel(rd_panel, text="", image=face_img)
face_link.grid(row=0, column=2, padx=5, pady=5)

link_link.bind("<Button-1>", lambda event: webbrowser.open("https://www.linkedin.com/company/ncnpe/"))
face_link.bind("<Button-1>", lambda event: webbrowser.open("https://www.facebook.com/ncnpe"))

customtkinter.CTkLabel(info_panel, text="Desarrollado por:", font=bold_font).grid(row=6, column=0, sticky="we")

customtkinter.CTkLabel(info_panel, text="Lucio Estacio Flores", font=important_info).grid(row=7, column=0, sticky="we")
customtkinter.CTkLabel(info_panel, text="Pedro Cruz Santos", font=important_info).grid(row=8, column=0, sticky="we")

customtkinter.CTkLabel(info_panel, text="Otras Soluciones", font=bold_font).grid(row=9, column=0, sticky="we")

quake_link = customtkinter.CTkLabel(info_panel, text="", image=quak_img)
quake_link.grid(row=10, column=0)

quake_link.bind("<Button-1>", lambda event: webbrowser.open("https://qs.ncn.pe/home"))
# -----------------------------------------------------------------------------------------

canvas_2 = FigureCanvasTkAgg(fig_2, master=frame2)
canvas_2.get_tk_widget().grid(row=0, column=0, sticky="nswe")

#----------------------------

sism_panel = customtkinter.CTkFrame(frame2)
sism_panel.grid(row=0, column=1, rowspan=8, sticky="nswe")

customtkinter.CTkLabel(sism_panel, text="Frecuencia (Hz)", font=bold_font).grid(row=0, column=0)

resample_entry = customtkinter.CTkEntry(sism_panel, corner_radius=0)
resample_entry.grid(row=1, column=0, padx=5, pady=3, sticky="we")

resample_entry.configure(justify="center")

resample_button = customtkinter.CTkButton(sism_panel, width=50, height=32, corner_radius=0, fg_color="#144196", hover_color="#0a204a", text="Auto Ajuste*", command=resample_data)
resample_button.grid(row=2, column=0, padx=5, pady=3, sticky="we")

upload_button = customtkinter.CTkButton(sism_panel, width=50, height=32, corner_radius=0, fg_color="#144196", hover_color="#0a204a", text="Subir Archivo", command=upload_file_in_chunks)
upload_button.grid(row=3, column=0, padx=5, pady=3, sticky="we")

#----------------------------

customtkinter.CTkFrame(sism_panel, width=1, height=2, fg_color="#d6d6d6").grid(row=4, column=0, padx=5, pady=2, sticky="we")

#----------------------------

search_button = customtkinter.CTkButton(sism_panel, width=50, height=32, corner_radius=0, fg_color="#ee7218", hover_color="#78390c", text="Buscar", command=get_files_arduino)
search_button.grid(row=5, column=0, padx=5, pady=3, sticky="we")

file_list = tk.Listbox(sism_panel, width=35, height=10)
file_list.grid(row=6, column=0, padx=5)
file_list.bind('<<ListboxSelect>>', on_listbox_select)

load_button = customtkinter.CTkButton(sism_panel, width=50, height=32, corner_radius=0, fg_color="#ee7218", hover_color="#78390c", text="Cargar Datos", command=load_file_data)
load_button.grid(row=7, column=0, padx=5, pady=3, sticky="we")

delete_button = customtkinter.CTkButton(sism_panel, width=50, height=32, corner_radius=0, fg_color="#ee7218", hover_color="#8f0303", text="Borrar Archivo", command=delete_file_arduino)
delete_button.grid(row=8, column=0, padx=5, pady=3, sticky="we")

#----------------------------

# customtkinter.CTkFrame(sism_panel, width=1, height=2, fg_color="#d6d6d6").grid(row=8, column=0, padx=5, pady=2, sticky="we")

#----------------------------

# graph2_button = customtkinter.CTkButton(sism_panel, width=50, height=32, corner_radius=0, fg_color="#3b9415", hover_color="#3e7d23", text="Inciar")
# graph2_button.grid(row=9, column=0, padx=5, pady=3, sticky="we")

#----------------------------

graph_control_2 = customtkinter.CTkFrame(frame2)
graph_control_2.grid(row=1, column=0, sticky="nswe")

play_button_2 = customtkinter.CTkButton(graph_control_2, width=32, height=32,  fg_color="transparent", hover_color="#ee7218", image=start_img, text="", command=start_simulation)
play_button_2.grid(row=0, column=0)

pause_button_2 = customtkinter.CTkButton(graph_control_2, width=32, height=32, fg_color="transparent", hover_color="#ee7218", image=pause_img, text="")
pause_button_2.grid(row=0, column=1)

reset_button_2 = customtkinter.CTkButton(graph_control_2, width=32, height=32, fg_color="transparent", hover_color="#ee7218", image=sstop_img, text="")
reset_button_2.grid(row=0, column=2)

save_button_2 = customtkinter.CTkButton(graph_control_2, width=32, height=32,  fg_color="transparent", hover_color="#ee7218", image=save_img, text="")
save_button_2.grid(row=0, column=3)

# -----------------------------------------------------------------------------------------

animating = True
frame_index = 0

canvas = FigureCanvasTkAgg(fig, master=frame1)
canvas.get_tk_widget().grid(row=0, column=0, sticky="nswe")

# ---------------------------

graph_control = customtkinter.CTkFrame(frame1)
graph_control.grid(row=1, column=0, sticky="nswe")

play_button = customtkinter.CTkButton(graph_control, width=32, height=32,  fg_color="transparent", hover_color="#ee7218", image=start_img, text="", command=start_animation)
play_button.grid(row=0, column=0)

pause_button = customtkinter.CTkButton(graph_control, width=32, height=32, fg_color="transparent", hover_color="#ee7218", image=pause_img, text="", command=stop_animation)
pause_button.grid(row=0, column=1)

reset_button = customtkinter.CTkButton(graph_control, width=32, height=32, fg_color="transparent", hover_color="#ee7218", image=sstop_img, text="", command=reset_graph)
reset_button.grid(row=0, column=2)

save_button = customtkinter.CTkButton(graph_control, width=32, height=32,  fg_color="transparent", hover_color="#ee7218", image=save_img, text="")
save_button.grid(row=0, column=3)

# ---------------------------

slider_control = customtkinter.CTkFrame(frame1, height=30)
slider_control.grid(row=2, column=0, sticky="nswe")

slider_control.grid_columnconfigure(0, weight=1)
slider_control.grid_columnconfigure(1, weight=1)

# ---------------------------

amp_control = customtkinter.CTkFrame(slider_control, corner_radius=0)
amp_control.grid(row=0, column=0)

# +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-

amp_control_panel = customtkinter.CTkFrame(amp_control, corner_radius=0)
amp_control_panel.grid(row=0, column=0, sticky="ewns")

amp_control_panel.grid_columnconfigure(1, weight=1)

customtkinter.CTkLabel(amp_control_panel, text="Amplitud (mm): ", font=bold_font, bg_color="transparent" ).grid(row=0, column=1)

amp_value = customtkinter.DoubleVar(value=1.00)

amp_input = customtkinter.CTkEntry(amp_control_panel, corner_radius=0, width=45, placeholder_text="1.00", textvariable=amp_value)
amp_input.grid(row=0, column=2)

amp_input.configure(justify="center")

amp_plus = customtkinter.CTkButton(amp_control_panel,  corner_radius=0, width=30, text="+", fg_color="#ee7218", hover_color="#78390c", command= lambda: adjust_value_amp(1))
amp_plus.grid(row=0, column=3)

amp_minus = customtkinter.CTkButton(amp_control_panel, corner_radius=0, width=30, text="-", fg_color="#ee7218", hover_color="#78390c", command= lambda: adjust_value_amp(-1))
amp_minus.grid(row=0, padx=1, column=4)

# +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-

amp_nro_panel = customtkinter.CTkFrame(amp_control, corner_radius=0)
amp_nro_panel.grid(row=1, column=0, sticky="ewns", pady=3)

amp_nro_panel.grid_rowconfigure(1, weight=1)

amp_10   = customtkinter.BooleanVar()
amp_1    = customtkinter.BooleanVar()
amp_0_1  = customtkinter.BooleanVar()
amp_0_01 = customtkinter.BooleanVar()

amp_ten  = customtkinter.CTkCheckBox(amp_nro_panel, corner_radius=0, width=60, fg_color="#ee7218", hover_color="#78390c", text="10"  , variable=amp_10).grid(sticky="ns", row=1, column=0, padx=5)
amp_one  = customtkinter.CTkCheckBox(amp_nro_panel, corner_radius=0, width=60, fg_color="#ee7218", hover_color="#78390c", text="1"   , variable=amp_1).grid(sticky="ns", row=1, column=1, padx=5)
amp_done = customtkinter.CTkCheckBox(amp_nro_panel, corner_radius=0, width=60, fg_color="#ee7218", hover_color="#78390c", text="0.1" , variable=amp_0_1).grid(sticky="ns", row=1, column=2, padx=5)
amp_dten = customtkinter.CTkCheckBox(amp_nro_panel, corner_radius=0, width=60, fg_color="#ee7218", hover_color="#78390c", text="0.01", variable=amp_0_01).grid(sticky="ns", row=1, column=3)

# ----------------------------------------------------------------------------------------------------------------

freq_control = customtkinter.CTkFrame(slider_control, corner_radius=0)
freq_control.grid(row=0, column=1, padx=5)

# +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-

freq_control_panel = customtkinter.CTkFrame(freq_control, corner_radius=0)
freq_control_panel.grid(row=0, column=0, sticky="ewns")

freq_control_panel.grid_columnconfigure(1, weight=1)
freq_control_panel.grid_rowconfigure(0, weight=1)

customtkinter.CTkLabel(freq_control_panel, text="Frecuencia (Hz): ", font=bold_font, bg_color="transparent" ).grid(row=0, column=1)

freq_value = customtkinter.DoubleVar(value=1.00)

freq_input = customtkinter.CTkEntry(freq_control_panel, corner_radius=0, width=45, placeholder_text="1.00", textvariable=freq_value)
freq_input.grid(row=0, column=2)

freq_input.configure(justify="center")

freq_plus = customtkinter.CTkButton(freq_control_panel,  corner_radius=0, width=30, text="+", fg_color="#ee7218", hover_color="#78390c", command= lambda: adjust_value_freq(1))
freq_plus.grid(row=0, column=3)

freq_minus = customtkinter.CTkButton(freq_control_panel, corner_radius=0, width=30, text="-", fg_color="#ee7218", hover_color="#78390c", command=lambda: adjust_value_freq(-1))
freq_minus.grid(row=0, padx=1, column=4)

# +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-

freq_nro_panel = customtkinter.CTkFrame(freq_control, corner_radius=0)
freq_nro_panel.grid(row=1, column=0, sticky="ewns", pady=3)

freq_nro_panel.grid_rowconfigure(1, weight=1)

freq_10   = customtkinter.BooleanVar()
freq_1    = customtkinter.BooleanVar()
freq_0_1  = customtkinter.BooleanVar()
freq_0_01 = customtkinter.BooleanVar()

freq_ten  = customtkinter.CTkCheckBox(freq_nro_panel, corner_radius=0, width=60, fg_color="#ee7218", hover_color="#78390c", text="10"  , variable=freq_10).grid(sticky="ns", row=1, column=0, padx=5)
freq_one  = customtkinter.CTkCheckBox(freq_nro_panel, corner_radius=0, width=60, fg_color="#ee7218", hover_color="#78390c", text="1"   , variable=freq_1).grid(sticky="ns", row=1, column=1, padx=5)
freq_done = customtkinter.CTkCheckBox(freq_nro_panel, corner_radius=0, width=60, fg_color="#ee7218", hover_color="#78390c", text="0.1" , variable=freq_0_1).grid(sticky="ns", row=1, column=2, padx=5)
freq_dten = customtkinter.CTkCheckBox(freq_nro_panel, corner_radius=0, width=60, fg_color="#ee7218", hover_color="#78390c", text="0.01", variable=freq_0_01).grid(sticky="ns", row=1, column=3)

# ----------------------------------------------------------------------------------------------------------------

footer = customtkinter.CTkFrame(root)
footer.grid(row=9, column=1, sticky="ew")

footer.grid_rowconfigure(0, weight=1)
footer.grid_columnconfigure(9, weight=1)

img_status = customtkinter.CTkLabel(footer, text="", image=disco_img)
img_status.grid(row=0, column=0, padx=5)

status_label  = customtkinter.CTkLabel(footer, text="Desconectado ")
status_label.grid(row=0, column=1, padx=1)

ip_label  = customtkinter.CTkLabel(footer, text="0.0.0.0")
ip_label.grid(row=0, column=2)

# --------------------------

customtkinter.CTkLabel(footer, text="|" , font=bold_font ).grid(row=0, column=3, padx=5)

# --------------------------

customtkinter.CTkLabel(footer, text="Amplitud:" , font=bold_font ).grid(row=0, column=4)

amp_label  = customtkinter.CTkLabel(footer, text=f"{amp_input.get()} mm")
amp_label.grid(row=0, column=5, padx=3)

customtkinter.CTkLabel(footer, text="Frecuencia:", font=bold_font).grid(row=0, column=6)

freq_label = customtkinter.CTkLabel(footer, text=f"{freq_input.get()} Hz")
freq_label.grid(row=0, column=7, padx=3)

progress_bar = customtkinter.CTkProgressBar(footer, orientation="horizontal", width=100, mode=["determinate"], height=15, corner_radius=0, progress_color="#ee7218")
progress_bar.grid(row=0, column=8, padx=5)

progress_bar.configure(mode="determinate")  
progress_bar.set(0)  
progress_bar.start()
progress_bar.stop() 

customtkinter.CTkLabel(footer, text="", image=ncn_img).grid(row=0, column=10)
customtkinter.CTkLabel(footer, text="NCN | Nuevo Control").grid(row=0, column=11, padx=5)

# ----------------------------

conn_estab = False

result_filename  = None
result_data = None
result_file = None
result_txt  = None
result_conn = None
result_unit = None

result_txt_arduino  = None

temp_file = None
filename_og = None
filesize_og = None

# ---------------------------

def show_frame(frame):
    frame1.grid_forget()
    frame2.grid_forget()
    frame3.grid_forget()
    frame.grid(row=0, column=0, rowspan=3, sticky="nswe")
    frame.grid_columnconfigure(0, weight=1)
    frame.grid_rowconfigure(0, weight=1)
    frame.grid_rowconfigure(1, weight=0)

show_frame(frame1)

root.bind("<Configure>", on_window_configure)

root.mainloop()
