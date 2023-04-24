from smbus2 import SMBus
from mlx90614 import MLX90614
import tkinter as tk
from tkinter import ttk
from tkinter import HORIZONTAL
import time

bus = SMBus(3)
sensor = MLX90614(bus, address=0x5A)

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
    classification = ""
    root = createRoot()
    progress_bar = progressBar(root)
    step(progress_bar)

    temperature_list = []
    i = 0
    while(i < 20):
        objectTemp = sensor.get_object_1()
        if objectTemp < 60:
            print("Object Temperature:", objectTemp,"°C")
            temperature_list.append(float(objectTemp))
        root.update()
        
        i = i + 1
        time.sleep(1.5)
        
        progress_bar.step(100/20)

    root.destroy()

    avg_temperature = sum(temperature_list) / len(temperature_list)
    print("{:.2f}°C".format(avg_temperature))
    if(avg_temperature >= 33 and avg_temperature < 37):
        classification = "Normal"
    else:
        classification = "Not Normal Temperature"
    return ["{:.2f}".format(avg_temperature), classification]


