import tkinter as tk
import serial
import time

import socket
import netifaces as ni
import time

from tkinter import filedialog, messagebox
from serial.tools import list_ports

from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

def list_interfaces():
    interfaces = ni.interfaces()
    interfaces_red = []
    for interface in interfaces:
        try:
            addrs = ni.ifaddresses(interface)
            ip_info = addrs[ni.AF_INET][0] if ni.AF_INET in addrs else {'addr': 'No tiene IP'}
            interfaces_red.append(ip_info)
        except KeyError:
            no_ip = "Red Desconectada"
            interfaces_red.append(no_ip)
    return interfaces_red

def get_network_config(interface):
    ni.ifaddresses(interface)
    return ni.ifaddresses(interface)[ni.AF_INET][0]

def connect_to_webserver(host, port):
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        sock.connect((host, port))
        print(f"Conectado a {host}:{port}")
        
        request = "GET / HTTP/1.1\r\nHost: {}\r\n\r\n".format(host)
        sock.sendall(request.encode())
        
        response = sock.recv(4096)
        print("Respuesta del servidor:")
        print(response.decode())
        
        sock.close()
    except Exception as e:
        print(f"Error al conectar al servidor: {e}")

def update_interfaces():
    ports = list_interfaces()
    port_entry.delete(0, tk.END)
    sub_entry.delete(0, tk.END)
    if ports:
        port_entry.insert(0, ports[0]["addr"])
        if 'broadcast' in ports[0]:
            sub_entry.insert(0, ports[0]["netmask"])
        else:
            sub_entry.insert(0, '')
        
        ports_list.delete(0, tk.END)
        for port in ports:
            if 'broadcast' in port or 'netmask' in port:
                ports_list.insert(tk.END, f'{port["addr"]}, {port["netmask"]},  {port["broadcast"]} ')
            else: 
                ports_list.insert(tk.END, f'{port["addr"]}, --, --')
    else:
        messagebox.showinfo("Info", "No hay dispositivos")


# Scaneo de puertos Seriales

def scan_ports():
    ports = list_ports.comports()
    arduino_ports = []
    for port in ports:
        try:
            s = serial.Serial(port.device)
            s.close()
            arduino_ports.append(port.device)
        except (OSError, serial.SerialException):
            pass
    return arduino_ports

def update_ports():
    ports = scan_ports()
    port_entry.delete(0, tk.END)
    if ports:
        port_entry.insert(0, ports[0])
        ports_list.delete(0, tk.END)
        for port in ports:
            ports_list.insert(tk.END, port)
    else:
        messagebox.showinfo("Info", "No hay dispositivos")


# Funcion mandar archivos por Serial Port

def send_file_to_arduino(port, baudrate, filepath):
    try:
        with open(filepath, 'r') as file:
            data = file.read()
        with serial.Serial(port, baudrate, timeout=1) as ser:
            time.sleep(2)
            ser.write(data.encode('utf-8'))
            print(f"Data sent from file: {filepath} ")

            response = ser.read(ser.in_waiting or 1)
            print(f"Response: {response.decode('utf-8')} ")

    except serial.SerialException as e:
        messagebox.showerror("Serial error", f"Error: {e}")
    except FileNotFoundError:
        messagebox.showerror("File Error", "File not found")

def select_file():
    filepath = filedialog.askopenfilename()
    if filepath:
        port = port_entry.get()
        baudrate = int(sub_entry.get())
        send_file_to_arduino(port, baudrate, filepath)


# Funciones para graficar

arr_dist = []
arr_acce = []

fig = Figure(figsize=(5, 4), dpi=100)
ax = fig.add_subplot(111)

text_artist = None

def plot_graph():
    x = [1,2,3,4,5]
    y = [5,10,15,20,25]
    fig = Figure(figsize=(5,4), dpi=100)
    ax = fig.add_subplot(111)
    ax.plot(x,y)
    canvas = FigureCanvasTkAgg(fig, master=root)
    canvas.draw()
    canvas.get_tk_widget().grid(row=0,column=2, rowspan=11, sticky="SNEW")

def plot_graph_test():
    global text_artist

    dist = dist_entry.get()
    acce = acce_entry.get()

    if dist != '' or acce != '':
        
        if is_float(dist) and is_float(acce):

            arr_dist.append(float(dist))
            arr_acce.append(float(acce))
            
            pga_a_value_ac1e = max_abs_value(arr_acce)

            ax.plot(arr_dist, arr_acce, 'b-')
            if text_artist:
                text_artist.remove()  
            text_artist = ax.text(0.81, 1.05, f'PGA: {pga_a_value_ac1e} cm/s²',
                                  horizontalalignment='left',
                                  verticalalignment='top',
                                  transform=ax.transAxes,
                                  fontsize=10,
                                  bbox=dict(facecolor='white', edgecolor='none', pad=1))
            ax.grid()
            canvas.draw()
            
        else:
            messagebox.showinfo("Info", "Datos deben ser Numeros")

    else:
        messagebox.showinfo("Info", "Ingrese datos")

def plot_delete_lastValue():
    global text_artist

    if arr_dist == [] and dist_entry == []:
         messagebox.showinfo("Info", "No hay Datos")
    else:
        arr_dist.pop()
        arr_acce.pop()

        pga_a_value_ac1e = max_abs_value(arr_acce)

        ax.clear()
        ax.plot(arr_dist, arr_acce, 'b-')
        if text_artist:
                text_artist.remove()  
        text_artist = ax.text(0.81, 1.05, f'PGA: {pga_a_value_ac1e} cm/s²',
                                horizontalalignment='left',
                                verticalalignment='top',
                                transform=ax.transAxes,
                                fontsize=10,
                                bbox=dict(facecolor='white', edgecolor='none', pad=1))
        ax.grid()
        canvas.draw()
    
def plot_delete_all():
    global text_artist

    respuesta = messagebox.askyesno("Confirmación", "¿Estás seguro de borrar el grafico?")
    if respuesta:
        arr_dist.clear()
        arr_acce.clear()

        pga_a_value_ac1e = 0.00

        ax.clear()
        ax.plot(arr_dist, arr_acce, 'b-')
        if text_artist:
                text_artist.remove()  
        text_artist = ax.text(0.81, 1.05, f'PGA: {pga_a_value_ac1e} cm/s²',
                                horizontalalignment='left',
                                verticalalignment='top',
                                transform=ax.transAxes,
                                fontsize=10,
                                bbox=dict(facecolor='white', edgecolor='none', pad=1))
        ax.grid()
        canvas.draw()

    else:
        return


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
    
def on_listbox_select(event):
    seleccion = ports_list.curselection()
    if seleccion:
        texto = ports_list.get(seleccion)

        port_entry.delete(0, tk.END)
        sub_entry.delete(0, tk.END)

        if ',' in texto:
            split_ports = texto.split(',')
            port_entry.insert(0, split_ports[0])
            if len(split_ports) > 1:
                sub_entry.insert(0, split_ports[1])
            else:
                sub_entry.insert(0, '')
        else:
            port_entry.insert(0, texto)
            sub_entry.insert(0, '')



list_interfaces()

root = tk.Tk()
root.title("NCN | ShakeTable Controller")

ancho_pantalla = root.winfo_screenwidth() 
alto_pantalla = root.winfo_screenheight() 

ancho_ventana = 900
alto_ventana = 600

posicion_x = (ancho_pantalla - ancho_ventana) // 2 
posicion_y = (alto_pantalla - alto_ventana) // 2

root.geometry(f"{ancho_ventana}x{alto_ventana}+{posicion_x}+{posicion_y}")
root.minsize(800, 600)

root.grid_columnconfigure(2, weight=1)    

menu_bar = tk.Menu(root)
root.config(menu=menu_bar)

file_menu = tk.Menu(menu_bar, tearoff=0)  
menu_bar.add_cascade(label="File", menu=file_menu)

file_menu.add_command(label="Abrir", command=select_file)

edit_menu = tk.Menu(file_menu, tearoff=0)
file_menu.add_cascade(label="Conectar..", menu=edit_menu)

edit_menu.add_command(label="MODO INTERNET", command=lambda: print("Cut selected"))
edit_menu.add_command(label="USB", command=lambda: print("Copy selected"))
edit_menu.add_command(label="MODO WIFI", command=lambda: print("Paste selected"))

file_menu.add_separator()  
file_menu.add_command(label="Salir", command=exit_application)

# --------------------

scan_button = tk.Button(root, text="PUERTOS", command=update_ports)
scan_button.grid(row=0, column=0, sticky="SNEW", padx=5)

scan_networks = tk.Button(root, text="RED", command=update_interfaces)
scan_networks.grid(row=0, column=1, sticky="SNEW", padx=5)

# -------------------

ports_list = tk.Listbox(root)
ports_list.grid(row=2, column=0, columnspan=2, sticky="ewns", padx=5, pady=5)
ports_list.bind('<<ListboxSelect>>', on_listbox_select)

# -------------------

tk.Label(root, text="IP/COM Port:").grid(row=3, column=0, sticky="w", padx=5, pady=5)
entry_var = tk.StringVar()
port_entry = tk.Entry(root, textvariable=entry_var)
port_entry.grid(row=3, column=1, sticky="ew", padx=5, pady=5)

tk.Label(root, text="Subnet/Baudrate:").grid(row=4, column=0, sticky="w", padx=5, pady=5)
sub_entry = tk.Entry(root)
sub_entry.grid(row=4, column=1, sticky="ew", padx=5, pady=5)
sub_entry.insert(0, '9600')

# -------------------

conect_button = tk.Button(root, text="Conectar")
conect_button.grid(row=5, column=0, columnspan=2, sticky="ew", padx=5, pady=5)

select_button = tk.Button(root, text="Seleccionar Archivo", command=select_file)
select_button.grid(row=6, column=0, columnspan=2, sticky="ew", padx=5, pady=5)

# -------------------

tk.Label(root, text="Distancia (cm) ").grid(row=7, column=0, sticky="w", padx=5, pady=5)
dist_entry = tk.Entry(root)
dist_entry.grid(row=7, column=1, sticky="ew", padx=5, pady=5)

tk.Label(root, text="Aceleración (cm/s2) ").grid(row=8, column=0, sticky="w", padx=5, pady=5)
acce_entry = tk.Entry(root)
acce_entry.grid(row=8, column=1, sticky="ew", padx=5, pady=5)

# -------------------------

plot_button = tk.Button(root, text="Añadir Datos", command=plot_graph_test)
plot_button.grid(row=9, column=0, columnspan=2, sticky="ew", padx=5, pady=5)

plot_button = tk.Button(root, text="Borrar ultimo", command=plot_delete_lastValue)
plot_button.grid(row=10, column=0, columnspan=2, sticky="ew", padx=5, pady=5)

plot_button = tk.Button(root, text="Borrar Todo", command=plot_delete_all)
plot_button.grid(row=11, column=0, columnspan=2, sticky="ew", padx=5, pady=5)

plot_button = tk.Button(root, text="Enviar Datos")
plot_button.grid(row=12, column=0, columnspan=2, sticky="ew", padx=5, pady=5)


canvas = FigureCanvasTkAgg(fig, master=root)
canvas.get_tk_widget().grid(row=0,column=2, rowspan=13, sticky="SNEW")

root.mainloop()