from sdk.client import Client
from sdk.device import Device
import sys
import time
import random
from configparser import ConfigParser
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email.message import Message


class LogFile:
    def __init__(self, filename):
        self.out_file = open(filename, "w")
        self.old_stdout = sys.stdout
        sys.stdout = self

    def write(self, text):
        self.old_stdout.write(text)
        self.out_file.write(text)

    def __enter__(self):
        return self

    def __exit__(self, type, value, traceback):
        sys.stdout = self.old_stdout


def email_logfile(filename, client):
    config = ConfigParser()
    config.read(
        "/Users/rdottin/Documents/Personal/pythonstarships/collectallresources/.config"
    )

    try:
        email = config.get("MAIL_CONFIG", "SENDER_EMAIL")
        password = config.get("MAIL_CONFIG", "SENDER_PASSWD")
        recipient = config.get("MAIL_CONFIG", "RECIPIENT_EMAIL")
    except:
        print(
            "Unable to email log file because email authentication is not properly setup."
        )
        return None

    with open(filename, "rb") as f:
        logs = f.read()
    message = Message()
    message.set_payload(logs)
    subject = f"Pixel Starships Automation Log: {client.user.name}"

    try:
        session = smtplib.SMTP("smtp.gmail.com", 587)
        session.ehlo()
        session.starttls()
        session.ehlo()
        session.login(email, password)
        data = f"Subject: {subject} \n {message}"
        session.sendmail(email, recipient, data)
        session.quit()
    except Exception as e:
        print(e)


def authenticate(device, email=None, password=None):
    client = Client(device=device)

    if device.refreshToken:
        # print("# This device is already authorized, no need to input credentials.")
        if client.login():
            return client
        return False

    if not client.login(email=email, password=password):
        print("[authenticate]", "failed to login")
        return False

    return client


def main():
    logfilepath = "/Users/rdottin/Documents/Personal/pythonstarships/collectallresources/collectrss.log"
    with LogFile(logfilepath):
        device = Device(language="ru")
        client = None

        if device.refreshToken:
            client = authenticate(device)
        else:
            decide = input("Input G to login as guest. Input A to login as user : ")
            if decide == "G":
                client = authenticate(device)
            else:
                email = input("Enter email: ")
                password = input("Enter password: ")
                client = authenticate(device, email, password)

        while client:
            time.sleep(random.uniform(5.0, 10.0))
            client.heartbeat()
            time.sleep(random.uniform(0.1, 1.0))

            client.grabFlyingStarbux(random.randint(1, 2))
            time.sleep(random.uniform(5.0, 10.0))

            if client.freeStarbuxToday == 10:
                if client.collectDailyReward():
                    print("The script collected the daily reward from the dropship.")
                time.sleep(random.uniform(5.0, 10.0))

                # if client.collectMiningDrone(11638355):
                #    print("Collected a mine drone.")
                # time.sleep(random.uniform(5.0, 10.0))
                # if client.collectMiningDrone(11638356):
                #    print("Collected a mine drone.")
                # time.sleep(random.uniform(5.0, 10.0))
                # if client.collectMiningDrone(11638362):
                #    print("Collected a mine drone.")
                # time.sleep(random.uniform(5.0, 10.0))
                # if client.placeMiningDrone("299", "1651"):
                #    print("Successfully placed mining drone.")
                # time.sleep(random.uniform(5.0, 10.0))
                # if client.placeMiningDrone("299", "1651"):
                #    print("Successfully placed mining drone.")
                # time.sleep(random.uniform(5.0, 10.0))
                # if client.placeMiningDrone("299", "1651"):
                #    print("Successfully placed mining drone.")
                # time.sleep(random.uniform(5.0, 10.0))

                client.collectAllResources()
                time.sleep(random.uniform(5.0, 10.0))
                client.listActiveMarketplaceMessages()
                print(
                    f"A total of {client.freeStarbuxToday} free starbux was collected today."
                )
                print(f"You have a total of {client.credits} starbux.")
                break
    email_logfile(logfilepath, client)


if __name__ == "__main__":
    main()
