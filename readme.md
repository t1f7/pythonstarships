
# [![Integration Tests](https://github.com/{{ repository.name }}/actions/workflows/integration-tests.yaml/badge.svg?branch={{ current.branch }})](https://github.com/{{ repository.name }}/actions/workflows/integration-tests.yaml?query=branch%3A{{ current.branch }})

[![ {{ current.version }} ](https://github.com/raelldottin/{{ repository.name }}/blob/main/pixelbot.png)](https://github.com/raelldottin/{{ repository.name }}/blob/main/pixelbot.png)

# Requirements

`pip3 install xmltodict`

`pip3 install requests`

+ to update `sdk/dotnet.validDateTime` - I messed with timezones and you should update this place if authentication doesn't work.

# Docs

It's super basic, one thing to note: `Device` class automatically saves generated device. Call `.reset()` method to cleanup saved data.

It also stores a token to relogin without credentials.

* One creates a device `device = Device(language='ru')`
* Then a client must be created `client = Client(device=device)`
* Use `client.login()` and `client.heartbeat()` to keep your session alive as a guest
* Use `client.login(email='supra@mail', password='1337')` and `client.heartbeat()` to keep authorized session alive
* Use `client.quickReload()` to re-authenticate your session


It seems that battle is simulated server-side so we have to simulate it client-side, and I don't have enough time to make it. Maybe later.
But you could join first battle and leave. Server would insta-simulate data as soon as you reconnect.
