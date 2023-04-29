import time
import os
import max30100
import tkinter as tk
from tkinter import ttk
from tkinter import HORIZONTAL
import RPi.GPIO as GPIO

# Set up the GPIO pins
GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)
GPIO.setup(27, GPIO.OUT) # Red LED
GPIO.setup(22, GPIO.OUT) # Green LED
GPIO.setup(17, GPIO.OUT) # Buzzer

mx30 = max30100.MAX30100()
mx30.enable_spo2()

# Generates Moving Average - This will filter data and improve stability of readings
def moving_average(numbers):
    window_size = 4
    i = 0
    # moving_averages = []
    while i < len(numbers) - window_size + 1:
        this_window = numbers[i : i + window_size]
        window_average = sum(this_window) / window_size
        # moving_averages.append(window_average)
        i += 1
    try:
        return int((window_average/100))
    except:
        pass

# If HeartRate is <10 function assumes Finger Not present and will not show incorrect data
# Also If SpO2 readings goes beyond 100. It will be shown as 100.
def display_filter(moving_average_bpm,moving_average_sp02):
    try:
        if(moving_average_bpm<10):
            moving_average_bpm ='NA'
            moving_average_sp02 = 'NA'
        else:
            if(moving_average_sp02>100):
                moving_average_sp02 = 100
        return moving_average_bpm, moving_average_sp02
    except:
        return moving_average_bpm, moving_average_sp02

def createRoot():
    root = tk.Tk()
    root.title("MAX30100 Sensor")
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
    progress_label = tk.Label(root, text="Acquiring Heart Rate and SpO2...", font=("Arial", 12), background="#0583D2")
    progress_label.pack(pady=10)
    progress_bar = ttk.Progressbar(root, orient=HORIZONTAL,
                                       length=180, mode="determinate")
    progress_bar.pack(pady=20)
    
    return progress_bar

def step(progress_bar):
    progress_bar.start(10)

def getReadings():
    hr_classification = ""
    or_classification = ""
    root = createRoot()
    progress_bar = progressBar(root)
    step(progress_bar)
    
    GPIO.output(22, GPIO.LOW) #red
    GPIO.output(27, GPIO.LOW) #green
    GPIO.output(17, GPIO.LOW) #buzzer
    time.sleep(1)
    i = 0
    while(i < 60):
        mx30.read_sensor()
        hb = int(mx30.ir / 100)
        spo2 = int(mx30.red / 100)
        if mx30.ir != mx30.buffer_ir :
            moving_average_bpm = (moving_average(mx30.buffer_ir))
        if mx30.red != mx30.buffer_red:
            moving_average_sp02 = (moving_average(mx30.buffer_red))
        bpm, spo2 = display_filter(moving_average_bpm,moving_average_sp02)
        print("Heart Rate:", bpm,"bpm")
        print("SpO2:", spo2,"%")
        root.update()
        
        i = i + 1
        time.sleep(1)
        
        progress_bar.step(100/20)

    root.destroy()
    if bpm >= 60 and bpm <= 100:
        hr_classification = "Normal"
        GPIO.output(22, GPIO.LOW) #red
        GPIO.output(27, GPIO.HIGH) #green
        GPIO.output(17, GPIO.LOW) #buzzer
        time.sleep(2)
    else:
        hr_classification = "Warning!"
        GPIO.output(22, GPIO.HIGH) #red
        GPIO.output(27, GPIO.LOW) #green
        GPIO.output(17, GPIO.HIGH) #buzzer
        time.sleep(2)

    if spo2 >= 95 and spo2 <= 100:
        or_classification = "Normal"
        GPIO.output(22, GPIO.LOW) #red
        GPIO.output(27, GPIO.HIGH) #green
        GPIO.output(17, GPIO.LOW) #buzzer
        time.sleep(2)
    else:
        or_classification = "Warning!"
        GPIO.output(22, GPIO.HIGH) #red
        GPIO.output(27, GPIO.LOW) #green
        GPIO.output(17, GPIO.HIGH) #buzzer
        time.sleep(2)
    
    GPIO.output(22, GPIO.LOW) #red
    GPIO.output(27, GPIO.LOW) #green
    GPIO.output(17, GPIO.LOW) #buzzer
    return [bpm, spo2, hr_classification, or_classification]
