import smtplib
from email.message import EmailMessage

EMAIL = "bsetestmail@gmail.com"
PASSWORD = "avpxplclngbjrcdi"

try:
    print("Connecting to Gmail...")

    smtp = smtplib.SMTP("smtp.gmail.com", 587, timeout=30)

    print("Connected")

    smtp.ehlo()

    print("Starting TLS...")

    smtp.starttls()

    smtp.ehlo()

    print("Logging in...")

    smtp.login(EMAIL, PASSWORD)

    print(" LOGIN SUCCESSFUL!")

    msg = EmailMessage()

    msg["Subject"] = "Test Email"
    msg["From"] = EMAIL
    msg["To"] = EMAIL

    msg.set_content("This is a test email from Python.")

    smtp.send_message(msg)

    print(" EMAIL SENT!")

    smtp.quit()

except Exception as e:
    print("ERROR:")
    print(type(e).__name__)
    print(e)