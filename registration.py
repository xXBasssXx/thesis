import tkinter as tk
from tkinter import messagebox
from tkinter import ttk
from datetime import datetime
from datetime import date
import psycopg2
from tkcalendar import DateEntry
import sms
# import thermal_sensor as ts
# import hr_or
# import bp

#initial data
global bp_sys, bp_dys, temp, hr, ox_r
bp_sys = 0
bp_dys = 0
temp = 0
hr = 0
ox_r = 0
now = datetime.now()
format_date = now.strftime("%d/%m/%Y %H:%M:%S")

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
    bp_sys = 0
    bp_dys = 0
    temp = 0
    hr = 0
    ox_r = 0
    
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
                    main_page()
                else:
                    messagebox.showwarning("Warning", "Patient ID not found")
            except Exception:
                  messagebox.showwarning("Warning", "Patient ID must be a number!")
        else:
            messagebox.showwarning("Warning", "Fill in input fields!")

    img = tk.PhotoImage(file="login.png")
    tk.Label(login, image=img, bg="#0583D2").place(x=105,y=8)

    appHeight = 300
    appWidth = 280

    screenHeight = login.winfo_screenheight()
    screenWidth = login.winfo_screenwidth()

    x = (screenHeight / 2) - (appHeight / 2)
    y = (screenWidth / 2) - (appWidth / 2)
    login.geometry(f'{appWidth}x{appHeight}+{int(y)}+{int(x)}')

    #patient ID
    global patient_id
    tk.Label(login, text="Patient ID:", background="#0583D2", font=("Arial", 15)).place(x=26, y=80)
    patient_id = tk.Entry(login, justify="left", width=20, font=("Arial", 14))
    patient_id.place(x=30, y=110)
    patient_id.focus_set()

    #Login Button
    tk.Button(login, text="LOGIN", height=2, width=18, font=("Arial", 13), background="#ee6c4d", command=login_fun).place(x=30, y=145)
    #Register Button
    tk.Button(login, text="Register", height=2, width=18, font=("Arial", 13), background="#293241", fg="white", command=register).place(x=30, y=200)    
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
                birthdate = age.get_date()
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
                login_page()
            except ValueError:
                messagebox.showwarning("Warning", "Invalid date format")
        else:
            messagebox.showwarning("Warning", "Fill in input fields!")
    
    appHeight = 470
    appWidth = 350

    screenHeight = registration.winfo_screenheight()
    screenWidth = registration.winfo_screenwidth()

    x = (screenHeight / 2) - (appHeight / 2)
    y = (screenWidth / 2) - (appWidth / 2)
    registration.geometry(f'{appWidth}x{appHeight}+{int(y)}+{int(x)}')

    #title
    tk.Label(registration, text="Personal Information", background="#0583D2", font=("Arial", 20, "bold")).place(x=35, y=5)

    #first name
    global first_name
    tk.Label(registration, text="First Name:", background="#0583D2", font=("Arial", 14), foreground="#FFFFFF").place(x=20, y=60)
    first_name = tk.Entry(registration, justify="left", width=25, font=("Arial", 13), background="#D3D3D3")
    first_name.place(x=24, y=85)
    first_name.focus_set()
    #last name
    global last_name
    tk.Label(registration, text="Last Name:", background="#0583D2", font=("Arial", 14), foreground="#FFFFFF").place(x=20, y=110)
    last_name = tk.Entry(registration, justify="left", width=25, font=("Arial", 13), background="#D3D3D3")
    last_name.place(x=24, y=135)

    today = date.today()
    max_year = today.year
    max_date = date(max_year, 12, 31)
    global age
    tk.Label(registration, text="Age:", background="#0583D2", font=("Arial", 14), foreground="#FFFFFF").place(x=20, y=160)
    age = DateEntry(registration, date_pattern='yyyy-mm-dd', width=12, background="#D3D3D3", font=("Arial", 13), maxdate=max_date)
    age.place(x=24, y=185)
    #address
    global address
    tk.Label(registration, text="Address:", background="#0583D2", font=("Arial", 14), foreground="#FFFFFF").place(x=20, y=210)
    address = tk.Entry(registration, justify="left", width=25, font=("Arial", 13), background="#D3D3D3")
    address.place(x=24, y=235)
    #doctors contact
    global doc_num
    tk.Label(registration, text="Doctor's Number:", background="#0583D2", font=("Arial", 14), foreground="#FFFFFF").place(x=20, y=260)
    doc_num = tk.Entry(registration, justify="left", width=25, font=("Arial", 13), background="#D3D3D3")
    doc_num.place(x=24, y=285)
    #relative contact
    global relative_num
    tk.Label(registration, text="Relative's Number:", background="#0583D2", font=("Arial", 14), foreground="#FFFFFF").place(x=20, y=310)
    relative_num = tk.Entry(registration, justify="left", width=25, font=("Arial", 13), background="#D3D3D3")
    relative_num.place(x=24, y=335)
    #Register Button
    tk.Button(registration, text="REGISTER", height=2, width=24, font=("Arial", 13), background="#ee6c4d", command=check_exceptions).place(x=40, y=380)

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
        main = tk.Tk()
        main.title("Main Page")
        main.resizable(0,0)
        main.configure(background="#0583D2")

        appHeight = 445
        appWidth = 742

        screenHeight = main.winfo_screenheight()
        screenWidth = main.winfo_screenwidth()

        x = (screenHeight / 2) - (appHeight / 2)
        y = (screenWidth / 2) - (appWidth / 2)
        main.geometry(f'{appWidth}x{appHeight}+{int(y)}+{int(x) - 20}')
        def goto_history():
            main.destroy()
            history_page()
        pf = tk.LabelFrame(main, text="Patient's Profile", background="#293241", fg="#e0fbfc", font=("Arial", 16))
        pf.grid(row=0, column=0, padx=1, pady=2)

        name = tk.Label(pf, text="Name: {0} {1}".format(info[1], info[2]), background="#293241", fg="#e0fbfc", font=("Arial", 10))
        name.grid(row=0, column=0, padx=0, pady=4, sticky="W")
    
        address = tk.Label(pf, text="Address: {0}".format(info[3]), background="#293241", fg="#e0fbfc", font=("Arial", 10))
        address.grid(row=1, column=0, padx=0, pady=2, sticky="W")

        age = tk.Label(pf, text="Age: {0}".format(info[4]), background="#293241", fg="#e0fbfc", font=("Arial", 10))
        age.grid(row=2, column=0, padx=0, pady=2, sticky="W")

        patientID = tk.Label(pf, text="Patient ID: {0}".format(info[0]), background="#293241", fg="#e0fbfc", font=("Arial", 10))
        patientID.grid(row=3, column=0, padx=0, pady=2, sticky="W")

        
        for r in range(4, 12):
            space1 = tk.Label(pf, background="#293241")
            space1.grid(row=r, column=0)

        get_vitals= tk.Button(pf, text="Check Vital Signs", height=2, width=15, font=("Arial", 10), background="#ee6c4d", command=check_vitals)
        get_vitals.grid(row=13, column=0, padx=10, pady=2)

        print(f"{bp_sys}, {bp_dys}, {temp}, {hr}, {ox_r}")
        view_history= tk.Button(pf, text="View History", height=2, width=15, font=("Arial", 10), background="#e0fbfc", command=goto_history)
        view_history.grid(row=14, column=0, padx=10, pady=2)

        def goto_login():
            main.destroy()
            login_page()

        logout = tk.Button(pf, text="Logout", height=1, width=15, font=("Arial", 10), background="#cf240a", command=goto_login)
        logout.grid(row=15, column=0, padx=10, pady=2)
        
        vital_signs = tk.LabelFrame(main, text="Vital Signs", background="#98C1D9", fg="#e0fbfc", font=("Arial", 16))
        vital_signs.grid(row=0, column=1, padx=1, pady=2, sticky="NW")
        #now = datetime.now()
        #format_date = now.strftime("%d/%m/%Y %H:%M:%S")
        date_time = tk.Label(vital_signs, text=format_date, background="#98C1D9", font=("Arial", 10))
        date_time.grid(row=0, column=1, padx=3, sticky="N")
        blood_pressure = tk.Label(vital_signs, text=f"Blood Pressure\n {bp_sys}/{bp_dys} mm/Hg \n Normal", background="#ee6c4d", font=("Arial", 12), width=15)
        blood_pressure.grid(row=0, column=0, padx=50, pady=73)
        body_temp = tk.Label(vital_signs, text=f"Body Temperature\n {temp}°C \n Normal", background="#ee6c4d", font=("Arial", 12), width=15)
        body_temp.grid(row=1, column=0, padx=50, pady=73)
        
        heart_rate = tk.Label(vital_signs, text=f"Heart Rate\n {hr} BPM \n Normal", background="#ee6c4d", font=("Arial", 12), width=15)
        heart_rate.grid(row=0, column=1, padx=90, pady=73)

        oxygen = tk.Label(vital_signs, text=f"Oxygen Saturation\n {ox_r}% \n Normal", background="#ee6c4d", font=("Arial", 12), width=15)
        oxygen.grid(row=1, column=1, padx=90, pady=73)

        main.mainloop()

def check_vitals():
    try:
        global bp_sys, bp_dys, temp, hr, ox_r
#         temp = ts.getTemperature()
#         [hr, ox_r] = hr_or.getReadings()
#         [bp_sys, bp_dys] = bp.getBP()
        print("niari diri")
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
        sms.send_alert(infoPatient[-1][5], infoPatient[-1][6], infoPatient[-1][0], infoVitals[-1][3], infoVitals[-1][5], infoVitals[-1][4], infoVitals[-1][1], infoVitals[-1][2])
        global main
        main.destroy()
        main_page()
    except Exception as e:
        messagebox.showwarning("Warning", "Error: {}".format(e))

def history_page():
    try:
        conn = accessDB()
        c = conn.cursor()
        c.execute('''SELECT * FROM VitalSigns WHERE patient_id = %s''', [fk_patient_id])
        rows = c.fetchall()

        # Divide data into chunks of 5 rows
        data_chunks = [rows[i:i+5] for i in range(0, len(rows), 6)]
        current_chunk = 0

        history = tk.Tk()
        history.title("History")
        history.resizable(0,0)
        history.configure(background="#0583D2")

        appHeight = 445
        appWidth = 742

        screenHeight = history.winfo_screenheight()
        screenWidth = history.winfo_screenwidth()

        x = (screenHeight / 2) - (appHeight / 2)
        y = (screenWidth / 2) - (appWidth / 2)
        history.geometry(f'{appWidth}x{appHeight}+{int(y)}+{int(x) - 20}')

        history_frame = tk.Frame(history)
        history_frame.pack()

        table = ttk.Treeview(history_frame, columns=(1,2,3,4,5,6), show="headings", height=7)
        table.pack(pady=2)
        
        table.column(1, stretch="NO", width=135)
        table.heading(1, text="Date-Time")
        table.column(2, stretch="NO", width=120)
        table.heading(2, text="SystolicBP")
        table.column(3, stretch="NO", width=120)
        table.heading(3, text="DiastolicBP")
        table.column(4, stretch="NO", width=120)
        table.heading(4, text="Temperature")
        table.column(5, stretch="NO", width=120)
        table.heading(5, text="Heart Rate")
        table.column(6, stretch="NO", width=120)
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
        tk.Button(history, text="Prev", height=1, width=8, font=("Arial", 10), background="#ee6c4d", command=prev_page).place(x=10, y=410)
        tk.Button(history, text="Next", height=1, width=8, font=("Arial", 10), background="#ee6c4d", command=next_page).place(x=650, y=410)

        # Show first page
        update_table()

        def back_to_main():
            history.destroy()
            main_page()

        tk.Button(history, text="BACK", height=1, width=10, font=("Arial", 10), background="#ee6c4d", command=back_to_main).place(x=330, y=410)
    except:
        messagebox.showwarning("Warning", "Exception Failed")
if __name__ == "__main__":
    createUserTable()
    login_page()