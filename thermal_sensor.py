import board
import busio as io
import adafruit_mlx90614
import tkinter as tk
from tkinter import ttk
from tkinter import HORIZONTAL
from time import sleep

def createRoot():
    root = tk.Tk()
    root.title("Getting Temperature")
    root.resizable(0,0)
    root.configure(background="#0583D2")

    appHeight = 150
    appWidth = 300

    screenHeight = root.winfo_screenheight()
    screenWidth = root.winfo_screenwidth()

    x = (screenHeight / 2) - (appHeight / 2)
    y = (screenWidth / 2) - (appWidth / 2)
    root.geometry(f'{appWidth}x{appHeight}+{int(y)}+{int(x) - 20}')
    
    return root

def progressBar(root):
    progress_label = tk.Label(root, text="Acquiring Temperature...", font=("Arial", 12), background="#0583D2")
    progress_label.pack(pady=10)
    progress_bar = ttk.Progressbar(root, orient=HORIZONTAL,
                                       length=180, mode="determinate")
    progress_bar.pack(pady=20)
    
    return progress_bar

def step(progress_bar):
    progress_bar.start(10)

def getTemperature():
    root = createRoot()
    progress_bar = progressBar(root)
    step(progress_bar)

    i = 0
    while(i < 20):
        i2c = io.I2C(board.SCL, board.SDA, frequency=100000)
        mlx = adafruit_mlx90614.MLX90614(i2c)

        ambientTemp = "{:.2f}".format(mlx.ambient_temperature)
        targetTemp = "{:.2f}".format(mlx.object_temperature)
        print("Target Temperature:", targetTemp,"°C")
        root.update()
        
        i = i + 1
        sleep(1)
        
        progress_bar.step(100/20)

    root.destroy()

    return targetTemp