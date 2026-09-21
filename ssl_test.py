import smtplib

EMAIL = "bsetestmail@gmail.com"
PASSWORD = "avpxplclngbjrcdi"

try:
    print("Connecting...")

    with smtplib.SMTP_SSL("smtp.gmail.com", 465, timeout=30) as smtp:
        smtp.login(EMAIL, PASSWORD)
        print("✅ LOGIN SUCCESSFUL!")

except Exception as e:
    print(type(e).__name__)
    print(e)