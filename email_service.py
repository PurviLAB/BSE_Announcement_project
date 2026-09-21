# import os
# import smtplib
# from dotenv import load_dotenv
# from email.message import EmailMessage

# load_dotenv()

# EMAIL = os.getenv("EMAIL_ADDRESS")
# PASSWORD = os.getenv("EMAIL_PASSWORD")
# RECEIVER = os.getenv("RECEIVER_EMAIL")


# def send_email(subject, body, attachment):

#     print("Step 1: Creating email")

#     msg = EmailMessage()
#     msg["Subject"] = subject
#     msg["From"] = EMAIL
#     msg["To"] = RECEIVER
#     msg.set_content(body)

#     print("Step 2: Attaching PDF")

#     with open(attachment, "rb") as f:
#         msg.add_attachment(
#             f.read(),
#             maintype="application",
#             subtype="pdf",
#             filename=attachment
#         )

#     print("Step 3: Connecting to Gmail")

#     smtp = smtplib.SMTP("smtp.gmail.com", 587, timeout=30)

#     print("Step 4: EHLO")
#     smtp.ehlo()

#     print("Step 5: STARTTLS")
#     smtp.starttls()

#     print("Step 6: EHLO Again")
#     smtp.ehlo()

#     print("Step 7: Login")
#     print(f"EMAIL='{EMAIL}'")
#     print(f"PASSWORD='{PASSWORD}'")
#     smtp.login(EMAIL.strip(), PASSWORD.strip())

#     print("Step 8: Sending")
#     smtp.send_message(msg)

#     print("Step 9: Quit")
#     smtp.quit()

#     print("Email sent successfully!")

import os
import smtplib
from dotenv import load_dotenv
from email.message import EmailMessage

load_dotenv()

EMAIL = os.getenv("EMAIL_ADDRESS")
PASSWORD = os.getenv("EMAIL_PASSWORD")
RECEIVERS = os.getenv("RECEIVER_EMAILS")

print("EMAIL     =", EMAIL)
print("PASSWORD? =", PASSWORD is not None)
print("RECEIVERS =", RECEIVERS)


def send_email(subject, body, attachment):

    msg = EmailMessage()

    msg["Subject"] = subject
    msg["From"] = EMAIL
    msg["To"] = RECEIVERS

    msg.set_content(body)

    with open(attachment, "rb") as f:
        msg.add_attachment(
            f.read(),
            maintype="application",
            subtype="pdf",
            filename=attachment
        )

    smtp = smtplib.SMTP("smtp.gmail.com", 587)
    smtp.ehlo()
    smtp.starttls()
    smtp.ehlo()

    smtp.login(EMAIL.strip(), PASSWORD.strip())

    smtp.send_message(msg)

    smtp.quit()

    print("Email sent successfully!")