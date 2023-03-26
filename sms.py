from twilio.rest import Client

account_sid = 'ACaabd9d8eedd8d3b809b8beb19fee172c'
auth_token = 'cac0059be910da5bbe4a42866b8c23a3'

twilio_number = '+12762939463'
client = Client(account_sid, auth_token)

#target_numbers = ['+639070581582', '+639919621957']

def send_alert(docs_num, rel_num, patient_id, temp, ox_r, hr, bp_sys, bp_dys):
    try:
        target_numbers = [docs_num, rel_num]
        for number in target_numbers:
            message = client.messages.create(
                body=f"Patient ID: {patient_id}\nTemperature: {temp}°C\nHeart Rate: {hr}bpm\nOxygen Level: {ox_r}%\nBlood Pressure: {bp_sys}/{bp_dys}mm/Hg",
                from_ = twilio_number,
                to = number
            )

        print(message)
    except:
        pass