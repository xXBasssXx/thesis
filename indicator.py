import RPi.GPIO as GPIO
import time

# Set up the GPIO pins
GPIO.setmode(GPIO.BCM)
GPIO.setup(27, GPIO.OUT) # Red LED
GPIO.setup(22, GPIO.OUT) # Green LED
GPIO.setup(17, GPIO.OUT) # Buzzer

# Initialize the state
greenled_on = True
redled_on = True
buzzer_on = False


# Loop indefinitely
while True:
    if greenled_on or redled_on:
        GPIO.output(22, GPIO.HIGH) #green
        GPIO.output(27, GPIO.HIGH) #red
        GPIO.output(17, GPIO.LOW) #buzzer
        buzzer_on = False
    else:
        GPIO.output(17, GPIO.HIGH)
        GPIO.output(22, GPIO.LOW)
        GPIO.output(27, GPIO.LOW)
        buzzer_on = True
        
    greenled_on = not greenled_on # Toggle the state of the LED
    redled_on = not redled_on
    
    time.sleep(1) # Wait for 1 second