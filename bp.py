import serial

def getBP():
    classification = ""
    # define serial port settings
    ser = serial.Serial('/dev/ttyS0', 9600, timeout=1)

    # initialize variables
    sbuffer = [''] * 30
    pos = 0
    read1 = 0
    read2 = 0
    read3 = 0

    # receive serial character from sensor (blocking while nothing received)
    def mygetchar():
        while True:
            if ser.in_waiting > 0:
                c = ser.read().decode('utf-8')
                
                if(c[0] <= 120 and c[1] <= 80):
                    classification = "Normal"
                elif((c[0] > 120 and c[0] <= 140) and (c[1] > 80 and c[1] <= 90)):
                    classification = "Pre-hypertension"
                elif((c[0] > 140 and c[0] <= 160) and (c[1] > 90 and c[1] <= 99)):
                    classification = "Stage 1 Hypertension"
                else:
                    classification = "Stage 2 Hypertension"
                return [c[0], c[1], classification]

    # send string to serial port
    def send_string(string):
        ser.write(string.encode())

    while True:
        ch = mygetchar() #loop till character received
        if ch == '\n': # if received character is <LF>, '\n', 10 then process buffer
            pos = 0 # buffer position reset for next reading
            
            # extract data from serial buffer to 8 bit integer value
            # convert data from ASCII to decimal
            read1 = ((ord(sbuffer[1])-ord('0'))*100) + ((ord(sbuffer[2])-ord('0'))*10) + (ord(sbuffer[3])-ord('0'))
            read2 = ((ord(sbuffer[6])-ord('0'))*100) + ((ord(sbuffer[7])-ord('0'))*10) + (ord(sbuffer[8])-ord('0'))
            read3 = ((ord(sbuffer[11])-ord('0'))*100) + ((ord(sbuffer[12])-ord('0'))*10) + (ord(sbuffer[13])-ord('0'))
            
            # Do whatever you wish to do with this sensor integer variables
            # Show on LCD or Do some action as per your application
            # Value of variables will be between 0-255
            
            # example: send demo output to serial monitor
            print(read1, read2, read3)
            
            # send a string to the serial port
            send_string('Hello from Raspberry Pi\n')
            return [read1, read2]
        else: #store serial data to buffer
            sbuffer[pos] = ch
            pos += 1
