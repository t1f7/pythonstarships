from sdk.client import Client
from sdk.device import Device

# for 'think'ing method
import time
import random


def think(client):

    while True:
        time.sleep(random.uniform(1.5, 3.5))
        if client.heartbeat():
            print('heartbeat OK')


def guestLoop(device):

    client = Client(device=device)
    if not client.login():
        print('> failed to login :(')
        return

    if not client.user:
        print('> no user found..')
        return

    print('> Logged in as ', client.user.name)

    think(client)
    
    return True


def userLoop(email, password, device):

    client = Client(device=device)
    if not client.login(email=email, password=password):
        print('> failed to login :(')
        return

    if not client.user:
        print('> no user found..')
        return

    print('> Logged in as ', client.user.name)
    # ship = client.loadShip()

    think(client)
    
    return True


device = Device(language='ru')
if device.refreshToken:
    print('This device is already authorized, no need to input credentials or join as a guest.')
    guestLoop(device)
else:
    decide = input("Input G to login as guest. Input A to login as user : ")
    if decide == "G":
        guestLoop(device)
    else:
        email = input("Enter email: ")
        password = input("Enter password: ")
        userLoop(email, password, device)
