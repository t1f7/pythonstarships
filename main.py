from sdk.client import Client
from sdk.device import Device

# for 'think'ing method
import time
import random


def authenticate(device, email=None, password=None):

    client = Client(device=device)

    if device.refreshToken:
        print("# This device is already authorized, no need to input credentials.")
        if client.login():
            return client
        return False

    if not client.login(email=email, password=password):
        print("[authenticate]", "failed to login")
        return False

    return client


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

    time.sleep(random.uniform(15.5, 30.5))

    if client.heartbeat():
        print("heartbeat OK")

    time.sleep(random.uniform(0.1, 1.0))

    if client.readyForFreeStabux():
        client.grabFlyingStarbux(random.randint(1, 2))
        print("I got", client.freeStarbuxToday, "free starbux today")
        time.sleep(random.uniform(5.0, 10.0))
        client.collectAllResources()
        print("Collected all resources from the ship.")
