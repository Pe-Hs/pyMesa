import tkinter as tk
from tkinter import ttk
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.animation import FuncAnimation

class SineWaveAnimation:
    def __init__(self, root):
        self.root = root
        self.root.title("Animación de Onda Senoidal")

        self.amplitude = tk.DoubleVar()
        self.frequency = tk.DoubleVar()
        self.duration = tk.DoubleVar()

        self.create_widgets()
        self.create_plot()

    def create_widgets(self):
        # Crear entrada para la amplitud
        ttk.Label(self.root, text="Amplitud:").grid(column=0, row=0, padx=10, pady=5)
        ttk.Entry(self.root, textvariable=self.amplitude).grid(column=1, row=0, padx=10, pady=5)
        
        # Crear entrada para la frecuencia
        ttk.Label(self.root, text="Frecuencia:").grid(column=0, row=1, padx=10, pady=5)
        ttk.Entry(self.root, textvariable=self.frequency).grid(column=1, row=1, padx=10, pady=5)
        
        # Crear entrada para la duración
        ttk.Label(self.root, text="Duración:").grid(column=0, row=2, padx=10, pady=5)
        ttk.Entry(self.root, textvariable=self.duration).grid(column=1, row=2, padx=10, pady=5)
        
        # Botón para iniciar la animación
        ttk.Button(self.root, text="Iniciar", command=self.start_animation).grid(column=0, row=3, columnspan=2, pady=10)

    def create_plot(self):
        self.fig, self.ax = plt.subplots()
        self.canvas = FigureCanvasTkAgg(self.fig, master=self.root)
        self.canvas.get_tk_widget().grid(column=0, row=4, columnspan=2)
        self.line, = self.ax.plot([], [], lw=2)
        self.ax.set_xlim(0, 10)
        self.ax.set_ylim(-1, 1)

    def start_animation(self):
        amplitude = self.amplitude.get()
        frequency = self.frequency.get()
        duration = self.duration.get()

        self.x_data = np.linspace(0, duration, 1000)
        self.y_data = amplitude * np.sin(2 * np.pi * frequency * self.x_data)

        self.ax.set_xlim(0, duration)
        self.ax.set_ylim(-amplitude, amplitude)

        self.ani = FuncAnimation(self.fig, self.update_plot, frames=len(self.x_data), interval=20, blit=True)
        self.canvas.draw()

    def update_plot(self, frame):
        self.line.set_data(self.x_data[:frame], self.y_data[:frame])
        return self.line,

if __name__ == "__main__":
    root = tk.Tk()
    app = SineWaveAnimation(root)
    root.mainloop()
