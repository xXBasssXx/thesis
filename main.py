import tkinter as tk
from tkinter import messagebox
from tkinter import ttk
from datetime import datetime
from datetime import date
import psycopg2

# # import sms
# # import thermal_sensor as ts
# # import hr_or
# # import bp
# # import RPi.GPIO as GPIO
import time
import subprocess

# Set up the GPIO pins
# GPIO.setwarnings(False)
# GPIO.setmode(GPIO.BCM)
# GPIO.setup(27, GPIO.OUT) # Red LED
# GPIO.setup(22, GPIO.OUT) # Green LED
# GPIO.setup(17, GPIO.OUT) # Buzzer
# 
# GPIO.output(22, GPIO.LOW) #red
# GPIO.output(27, GPIO.LOW) #green
# GPIO.output(17, GPIO.LOW) #buzzer
# time.sleep(1)
#initial data
global bp_sys, bp_dys, temp, hr, ox_r
bp_sys = 0
bp_dys = 0
temp = 0
hr = 0
ox_r = 0
global bp_classification, temp_classification, hr_classification, or_classification
bp_classification = "-"
temp_classification = "-"
hr_classification = "-"
or_classification = "-"
now = datetime.now()
format_date = now.strftime("%d/%m/%Y %H:%M:%S")


def activate_onboard(event):
    try:
        subprocess.Popen(['onboard'])
    except OSError as e:
        print(f"Error launching onboard: {e}")

    
def accessDB():
    conn = psycopg2.connect(database="emiylcge", user="emiylcge", password="u1IAQeuszoydrIv2tzOO81yqEYDX_ozG",
                        host="satao.db.elephantsql.com", port="5432")
    return conn

def dropUserDB():
    conn = accessDB()
    c = conn.cursor()
    c.execute('''DROP TABLE Patient''')
    conn.commit()
    conn.close()

def dropVitalsDB():
    conn = accessDB()
    c = conn.cursor()
    c.execute('''DROP TABLE VitalSigns''')
    conn.commit()
    conn.close()

def createUserTable():
    try:
        conn = accessDB()
        c = conn.cursor()

        c.execute('''CREATE TABLE IF NOT EXISTS Patient (
                patient_id SERIAL PRIMARY KEY,
                firstname TEXT, 
                lastname VARCHAR(100), 
                address VARCHAR(100), 
                age VARCHAR(5),
                doc_num VARCHAR(100),
                relative_num VARCHAR(100)
                )
                ''')
        conn.commit()
    except Exception as e:
        messagebox.showwarning("Warning", "Error: {}".format(e))
    finally:
        conn.close()

def createVitalsTable():
    try:
        conn = accessDB()
        c = conn.cursor()

        c.execute('''CREATE TABLE IF NOT EXISTS VitalSigns (
                date_time VARCHAR(50), 
                systolic_bp INTEGER, 
                diastolic_bp INTEGER, 
                body_temp DECIMAL,
                heart_rate INTEGER,
                oxygen_level INTEGER,
                vitals_id SERIAL PRIMARY KEY,
                patient_id INTEGER,
                CONSTRAINT fk_people_id
                    FOREIGN KEY(patient_id) 
                        REFERENCES Patient(patient_id))
                ''')
        conn.commit()
    except Exception as e:
        messagebox.showwarning("Warning", "Error: {}".format(e))
    finally:
        conn.close()

def login_page():
    
    login = tk.Tk()
    login.title("Login Page")
    login.resizable(0,0)
    login.configure(background="#0583D2")

    def register():
        login.destroy()
        registration_page()
    def login_fun():
        conn = accessDB()
        c = conn.cursor()
        if patient_id.get():
            try:
                int(patient_id.get())
                global pat_id_check
                pat_id_check = patient_id.get()
                global fk_patient_id 
                fk_patient_id = patient_id.get()
                c.execute('''SELECT patient_id FROM Patient WHERE patient_id = %s''', [pat_id_check])
                result = c.fetchone()
                if result:
                    login.destroy()
                    subprocess.Popen(['killall', 'onboard'])
                    main_page()
                else:
                    messagebox.showwarning("Warning", "Patient ID not found")
            except Exception:
                  messagebox.showwarning("Warning", "Patient ID must be a number!")
        else:
            messagebox.showwarning("Warning", "Fill in input fields!")

    #img = tk.PhotoImage(file="./login.png")
    #tk.Label(login, image=img, bg="#0583D2").place(x=140,y=8)

    appHeight = 400
    appWidth = 350

    screenHeight = login.winfo_screenheight()
    screenWidth = login.winfo_screenwidth()

    y = 0
    x = (screenWidth / 2) - (appWidth / 2)
    login.geometry(f'{appWidth}x{appHeight}+{int(x)}+{int(y)}')

    #patient ID
    global patient_id
    tk.Label(login, text="Patient ID:", background="#0583D2", fg="#e0fbfc", font=("Arial", 18, "bold")).place(x=26, y=80)
    patient_id = tk.Entry(login, justify="left", width=22, font=("Arial", 17))
    patient_id.place(x=25, y=110)
    patient_id.focus_set()
    patient_id.bind("<FocusIn>", activate_onboard)
    #Login Button
    tk.Button(login, text="LOGIN", height=3, width=20, font=("Arial", 18, "bold"), background="#ee6c4d", fg="#e0fbfc", command=login_fun).place(x=30, y=150)
    #Register Button
    tk.Button(login, text="REGISTER", height=3, width=20, font=("Arial", 18, "bold"), background="#293241", fg="#e0fbfc", command=register).place(x=30, y=250)    
    login.mainloop()

def registration_page():
    registration = tk.Tk()
    registration.title("Registration Page")
    registration.resizable(0,0)
    registration.configure(background="#0583D2")

    def check_exceptions():
        if first_name.get() and last_name.get() and age.get() and doc_num.get() and address.get() and relative_num.get():
            try:
                # calculate age
                birthdate = datetime.strptime(age.get(), '%Y-%m-%d').date()
                today = date.today()
                p_age = today.year - birthdate.year - ((today.month, today.day) < (birthdate.month, birthdate.day))

                # database
                conn = accessDB()

                c = conn.cursor()

                # insert data
                fname = first_name.get()
                lname = last_name.get()
                p_address = address.get()
                doc_no = doc_num.get()
                rel_no = relative_num.get()
                c.execute('''INSERT INTO Patient (firstname, lastname, address, age, doc_num, relative_num)
                            VALUES (%s, %s, %s, %s, %s, %s);''', (fname, lname, p_address, p_age, doc_no, rel_no))

                c.execute('''SELECT patient_id FROM Patient''')
                patient_num = c.fetchall()
                length = len(patient_num)

                p_id = str(patient_num[length - 1][0])
                conn.commit()
                conn.close()
                messagebox.showinfo("Patient ID", "Your Patient ID is {0}".format(p_id))
                registration.destroy()
                subprocess.Popen(['killall', 'onboard'])
                login_page()
            except ValueError:
                messagebox.showwarning("Warning", "Invalid date format")
        else:
            messagebox.showwarning("Warning", "Fill in input fields!")
    
    appHeight = 600
    appWidth = 450

    screenHeight = registration.winfo_screenheight()
    screenWidth = registration.winfo_screenwidth()

    y = 0
    x = (screenWidth / 2) - (appWidth / 2)
    registration.geometry(f'{appWidth}x{appHeight}+{int(x)}+{int(y)}')

    #title
    tk.Label(registration, text="Personal Information", background="#0583D2", font=("Arial", 22, "bold"), foreground="#FFFFFF").place(x=85, y=5)

    #first name
    global first_name
    tk.Label(registration, text="First Name:", background="#0583D2", font=("Arial", 17, "bold"), foreground="#FFFFFF").place(x=20, y=60)
    first_name = tk.Entry(registration, justify="left", width=25, font=("Arial", 17), background="#D3D3D3")
    first_name.place(x=24, y=85)
    first_name.focus_set()
    first_name.bind("<FocusIn>", activate_onboard)
    #last name
    global last_name
    tk.Label(registration, text="Last Name:", background="#0583D2", font=("Arial", 17, "bold"), foreground="#FFFFFF").place(x=20, y=120)
    last_name = tk.Entry(registration, justify="left", width=25, font=("Arial", 17), background="#D3D3D3")
    last_name.place(x=24, y=145)

    today = date.today()
    max_year = today.year
    max_date = date(max_year, 12, 31)
    global age
    tk.Label(registration, text="Age (YYYY-MM-DD):", background="#0583D2", font=("Arial", 17, "bold"), foreground="#FFFFFF").place(x=20, y=180)
    age = tk.Entry(registration, justify="left", width=12, font=("Arial", 17), background="#D3D3D3")
    age.place(x=24, y=205)
    #address
    global address
    tk.Label(registration, text="Address:", background="#0583D2", font=("Arial", 17, "bold"), foreground="#FFFFFF").place(x=20, y=240)
    address = tk.Entry(registration, justify="left", width=25, font=("Arial", 17), background="#D3D3D3")
    address.place(x=24, y=265)
    #doctors contact
    global doc_num
    tk.Label(registration, text="Doctor's Number:", background="#0583D2", font=("Arial", 17, "bold"), foreground="#FFFFFF").place(x=20, y=300)
    doc_num = tk.Entry(registration, justify="left", width=25, font=("Arial", 17), background="#D3D3D3")
    doc_num.place(x=24, y=325)
    #relative contact
    global relative_num
    tk.Label(registration, text="Relative's Number:", background="#0583D2", font=("Arial", 17, "bold"), foreground="#FFFFFF").place(x=20, y=360)
    relative_num = tk.Entry(registration, justify="left", width=25, font=("Arial", 17), background="#D3D3D3")
    relative_num.place(x=24, y=395)
    #Register Button
    tk.Button(registration, text="REGISTER", height=2, width=25, font=("Arial", 16, "bold"), foreground="#FFFFFF", background="#ee6c4d", command=check_exceptions).place(x=60, y=460)

    registration.mainloop()

def main_page():
        try:
            createVitalsTable()

            conn = accessDB()
            c = conn.cursor()
            c.execute('''SELECT * FROM Patient WHERE patient_id = %s''', [pat_id_check])
            info = c.fetchone()
            print(info)
            conn.commit()
        except Exception as e:
            messagebox.showwarning("Warning", "Error: {}".format(e))
        finally:
            conn.close()

        global main
        global bp_classification, temp_classification, hr_classification, or_classification
        main = tk.Tk()
        main.title("Main Page")
        main.resizable(0,0)
        main.configure(background="#0583D2")

        appHeight = 535
        appWidth = 1015

        screenHeight = main.winfo_screenheight()
        screenWidth = main.winfo_screenwidth()

        x = (screenHeight / 2) - (appHeight / 2)
        y = (screenWidth / 2) - (appWidth / 2)
        main.geometry(f'{appWidth}x{appHeight}+{int(y)}+{int(x) + 5}')
        def goto_history():
            main.destroy()
            history_page()
        pf = tk.LabelFrame(main, text="Patient's Profile", background="#293241", fg="#e0fbfc", font=("Arial", 18))
        pf.grid(row=0, column=0, padx=1, pady=2, sticky="NW")

        name = tk.Label(pf, text="Name: {0} {1}".format(info[1], info[2]), background="#293241", fg="#e0fbfc", font=("Arial", 12, "bold"))
        name.grid(row=0, column=0, padx=0, pady=12, sticky="W")
    
        address = tk.Label(pf, text="Address: {0}".format(info[3]), background="#293241", fg="#e0fbfc", font=("Arial", 12, "bold"))
        address.grid(row=1, column=0, padx=0, pady=12, sticky="W")

        age = tk.Label(pf, text="Age: {0}".format(info[4]), background="#293241", fg="#e0fbfc", font=("Arial", 12, "bold"))
        age.grid(row=2, column=0, padx=0, pady=12, sticky="W")

        patientID = tk.Label(pf, text="Patient ID: {0}".format(info[0]), background="#293241", fg="#e0fbfc", font=("Arial", 12, "bold"))
        patientID.grid(row=3, column=0, padx=0, pady=12, sticky="W")

        
        for r in range(12, 15):
            space1 = tk.Label(pf, background="#293241")
            space1.grid(row=r, column=0)

        get_vitals= tk.Button(pf, text="Check Vital Signs", height=4, width=18, font=("Arial", 14, "bold"), background="#ee6c4d", fg="#e0fbfc", command=check_vitals)
        get_vitals.grid(row=13, column=0, padx=10, pady=2)

        print(f"{bp_sys}, {bp_dys}, {temp}, {hr}, {ox_r}")
        view_history= tk.Button(pf, text="View History", height=4, width=18, font=("Arial", 14, "bold"), background="#e0fbfc", command=goto_history)
        view_history.grid(row=14, column=0, padx=10, pady=2)

        def goto_login():
            global bp_sys, bp_dys, temp, hr, ox_r
            bp_sys = 0
            bp_dys = 0
            temp = 0
            hr = 0
            ox_r = 0
            main.destroy()
            login_page()

        logout = tk.Button(pf, text="Logout", height=3, width=18, font=("Arial", 14, "bold"), background="#cf240a", fg="#e0fbfc", command=goto_login)
        logout.grid(row=15, column=0, padx=10, pady=2)
        
        vital_signs = tk.LabelFrame(main, text="Vital Signs", background="#98C1D9", font=("Arial", 18))
        vital_signs.grid(row=0, column=1, padx=1, pady=2, sticky="NW")
        #now = datetime.now()
        #format_date = now.strftime("%d/%m/%Y %H:%M:%S")
        date_time = tk.Label(vital_signs, text=format_date, background="#98C1D9", font=("Arial", 12))
        date_time.grid(row=0, column=3, padx=3, sticky="N")
        blood_pressure = tk.Label(vital_signs, text=f"Blood Pressure\n {bp_sys}/{bp_dys} mm/Hg \n {bp_classification}", background="#ee6c4d", fg="#e0fbfc", font=("Arial", 16, "bold"), width=17)
        blood_pressure.grid(row=0, column=2, padx=90, pady=90)
        body_temp = tk.Label(vital_signs, text=f"Body Temperature\n {temp}°C \n {temp_classification}", background="#ee6c4d", fg="#e0fbfc", font=("Arial", 16, "bold"), width=17)
        body_temp.grid(row=1, column=2, padx=90, pady=90)
        
        heart_rate = tk.Label(vital_signs, text=f"Heart Rate\n {hr} BPM \n {hr_classification}", background="#ee6c4d", fg="#e0fbfc", font=("Arial", 16, "bold"), width=17)
        heart_rate.grid(row=0, column=3, padx=90, pady=90)

        oxygen = tk.Label(vital_signs, text=f"Oxygen Saturation\n {ox_r}% \n {or_classification}", background="#ee6c4d", fg="#e0fbfc", font=("Arial", 16, "bold"), width=17)
        oxygen.grid(row=1, column=3, padx=90, pady=90)

        main.mainloop()

def check_vitals():
    try:
        global bp_sys, bp_dys, temp, hr, ox_r
        global bp_classification, temp_classification, hr_classification, or_classification
#         [temp, temp_classification] = ts.getTemperature()
#         [hr, ox_r, hr_classification, or_classification] = hr_or.getReadings()
#         [bp_sys, bp_dys] = bp.getBP()
#         if(int(bp_sys) <= 120 or int(bp_dys) <= 80):
#             bp_classification = "Normal"
#             GPIO.output(22, GPIO.LOW) #red
#             GPIO.output(27, GPIO.HIGH) #green
#             GPIO.output(17, GPIO.LOW) #buzzer
#         elif((int(bp_sys) > 120 and int(bp_sys) <= 140) or (int(bp_dys) > 80 and int(bp_dys) <= 90)):
#             bp_classification = "Pre-hypertension"
#             GPIO.output(22, GPIO.HIGH) #red
#             GPIO.output(27, GPIO.LOW) #green
#             GPIO.output(17, GPIO.HIGH) #buzzer
#         elif((int(bp_sys) > 140 and int(bp_sys) <= 160) or (int(bp_dys) > 90 and int(bp_dys) <= 99)):
#             bp_classification = "Stage 1 Hypertension"
#             GPIO.output(22, GPIO.HIGH) #red
#             GPIO.output(27, GPIO.LOW) #green
#             GPIO.output(17, GPIO.HIGH) #buzzer
#         elif((int(bp_sys) > 160) or  (int(bp_dys) >= 100)):
#             bp_classification = "Stage 2 Hypertension"
#             GPIO.output(22, GPIO.HIGH) #red
#             GPIO.output(27, GPIO.LOW) #green
#             GPIO.output(17, GPIO.HIGH) #buzzer
        time.sleep(2)
        conn = accessDB()
        patient = conn.cursor()
        vitals = conn.cursor()

        vitals.execute('''INSERT INTO VitalSigns (date_time, systolic_bp, diastolic_bp, body_temp, heart_rate, oxygen_level, patient_id)
                                VALUES (%s, %s, %s, %s, %s, %s, %s);''', (str(format_date), str(bp_sys), str(bp_dys), temp, hr, ox_r, fk_patient_id))
        
        patient.execute('''SELECT * FROM Patient WHERE patient_id = %s''', [pat_id_check])
        vitals.execute('''SELECT * FROM VitalSigns WHERE patient_id = %s''', [pat_id_check])
        infoPatient = patient.fetchall()
        infoVitals = vitals.fetchall()
        
        
        conn.commit()
        conn.close()
        #print(infoPatient[-1] + infoVitals[-1])
        GPIO.output(22, GPIO.LOW) #red
        GPIO.output(27, GPIO.LOW) #green
        GPIO.output(17, GPIO.LOW) #buzzer
        time.sleep(1)
        #sms.send_alert(infoPatient[-1][5], infoPatient[-1][6], infoPatient[-1][0], infoVitals[-1][3], infoVitals[-1][5], infoVitals[-1][4], infoVitals[-1][1], infoVitals[-1][2])
        global main
        main.destroy()
        main_page()
    except Exception as e:
        messagebox.showwarning("Warning", "Error: {}".format(e))

def history_page():
    
    def back_to_main():
            history.destroy()
            main_page()
            
    try:
        conn = accessDB()
        c = conn.cursor()
        c.execute('''SELECT * FROM VitalSigns WHERE patient_id = %s''', [fk_patient_id])
        rows = c.fetchall()
    
        # Divide data into chunks of 10 rows
        data_chunks = [rows[i:i+10] for i in range(0, len(rows), 6)]
        current_chunk = 0

        history = tk.Tk()
        history.title("History")
        history.resizable(0,0)
        history.configure(background="#0583D2")

        appHeight = 535
        appWidth = 1015

        screenHeight = history.winfo_screenheight()
        screenWidth = history.winfo_screenwidth()

        x = (screenHeight / 2) - (appHeight / 2)
        y = (screenWidth / 2) - (appWidth / 2)
        history.geometry(f'{appWidth}x{appHeight}+{int(y)}+{int(x) + 5}')

        history_frame = tk.Frame(history)
        history_frame.pack()
        
        style = ttk.Style()
        style.configure("my.Treeview", rowheight=27, padding=30)

        table = ttk.Treeview(history_frame, columns=(1,2,3,4,5,6), show="headings", height=15, style="my.Treeview")
        table.pack(pady=15)
        
        table.column(1, stretch="NO", width=180)
        table.heading(1, text="Date-Time")
        table.column(2, stretch="NO", width=160)
        table.heading(2, text="SystolicBP")
        table.column(3, stretch="NO", width=160)
        table.heading(3, text="DiastolicBP")
        table.column(4, stretch="NO", width=160)
        table.heading(4, text="Temperature")
        table.column(5, stretch="NO", width=160)
        table.heading(5, text="Heart Rate")
        table.column(6, stretch="NO", width=160)
        table.heading(6, text="Oxygen Level")

        # Function to update table with current data chunk
        def update_table():
            table.delete(*table.get_children())
            for row in data_chunks[current_chunk]:
                table.insert('', 'end', values=row)

        # Functions to handle pagination
        def prev_page():
            nonlocal current_chunk
            if current_chunk > 0:
                current_chunk -= 1
                update_table()

        def next_page():
            nonlocal current_chunk
            if current_chunk < len(data_chunks) - 1:
                current_chunk += 1
                update_table()

        # Add pagination buttons
        tk.Button(history, text="Prev", height=2, width=10, font=("Arial", 14), background="#ee6c4d", command=prev_page).place(x=8, y=440)
        tk.Button(history, text="Next", height=2, width=10, font=("Arial", 14), background="#ee6c4d", command=next_page).place(x=880, y=440)

        # Show first page
        update_table()

    except:
        messagebox.showwarning("Warning", "History is empty...")
    finally:
        tk.Button(history, text="BACK", height=2, width=12, font=("Arial", 14), background="#ee6c4d", command=back_to_main).place(x=440, y=440)
        
if __name__ == "__main__":
    createUserTable()
    login_page()