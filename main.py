from sdk.client import Client
from sdk.device import Device
import sys
import time
import random
from configparser import ConfigParser
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText


class LogFile:
    def __init__(self, filename):
        self.out_file = open(filename, "a")
        self.old_stdout = sys.stdout
        sys.stdout = self

    def write(self, text):
        self.old_stdout.write(text)
        self.out_file.write(text)

    def __enter__(self):
        return self

    def __exit__(self, type, value, traceback):
        sys.stdout = self.old_stdout


def email_logfile(filename):
    mail_content = ""

    with open(filename) as f:
        mail_content = """{}""".format(f.readlines())

    config = ConfigParser()
    config.read(
        "/Users/rdottin/Documents/Personal/pythonstarships/collectallresources/.config"
    )

    try:
        email = config.get("MAIL_CONFIG", "SENDER_EMAIL")
        password = config.get("MAIL_CONFIG", "SENDER_PASSWD")
        recipient = config.get("MAIL_CONFIG", "RECIPIENT_EMAIL")
    except:
        print("Authentication not properly setup to email log file")
        return None

    message = MIMEMultipart()
    message["From"] = email
    message["To"] = recipient
    message["Subject"] = "Pixel Starships Automation Log"

    message.attach(MIMEText(mail_content, "plain"))

    session = smtplib.SMTP("smtp.gmail.com", 587)
    session.starttls()
    session.login(email, password)
    text = message.as_string()
    session.sendmail(email, recipient, text)
    session.quit()


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
        device = Device(language="en")
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

            if client.freeStarbuxToday >= 10:
                time.sleep(random.uniform(15.5, 30.5))
                client.heartbeat()
                time.sleep(random.uniform(0.1, 1.0))

                if client.collectDailyReward():
                    print("Collected daily reward from the dropship.")
                time.sleep(random.uniform(5.0, 10.0))

                client.grabFlyingStarbux(random.randint(1, 2))
                time.sleep(random.uniform(5.0, 10.0))

                #        if client.collectMiningDrone(11638355):
                #            print("Collected a mine drone.")
                #            time.sleep(random.uniform(5.0, 10.0))
                #
                #        if client.collectMiningDrone(11638356):
                #            print("Collected a mine drone.")
                #            time.sleep(random.uniform(5.0, 10.0))
                #
                #        if client.collectMiningDrone(11638362):
                #            print("Collected a mine drone.")
                #            time.sleep(random.uniform(5.0, 10.0))
                #
                #        if client.placeMiningDrone("299", "1651"):
                #            print("Successfully placed mining drone.")
                #            time.sleep(random.uniform(5.0, 10.0))
                #
                #        if client.placeMiningDrone("299", "1651"):
                #            print("Successfully placed mining drone.")
                #            time.sleep(random.uniform(5.0, 10.0))
                #
                #        if client.placeMiningDrone("299", "1651"):
                #            print("Successfully placed mining drone.")
                #            time.sleep(random.uniform(5.0, 10.0))
                #
                # print("I collected", client.freeStarbuxToday, "free starbux today.")
                client.collectAllResources()
                time.sleep(random.uniform(5.0, 10.0))
                client.listActiveMarketplaceMessages()
                print("Collected all available free starbux.")
                break
    email_logfile(logfilepath)


if __name__ == "__main__":
    main()
