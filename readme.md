<!---
This file is auto-generate by a github hook please modify readme.template if you don't want to loose your work
-->
# raelldottin/pythonstarships v0.5.114

Automate trivial tasks in Pixel Starships Mobile Starategy Sci-Fi MMORPG

[![ v0.5.114 ](https://github.com/raelldottin/pythonstarships/blob/main/pixelbot.png)](https://github.com/raelldottin/pythonstarships/blob/main/pixelbot.png)

# Requirements

`pip3 install xmltodict`

`pip3 install requests`

# Docs

It's super basic, one thing to note: `Device` class automatically saves generated device. Call `.reset()` method to cleanup saved data.

It also stores a token to relogin without credentials.

* One creates a device `device = Device(language='ru')`
* Then a client must be created `client = Client(device=device)`
* Use `client.login()` and `client.heartbeat()` to keep your session alive as a guest
* Use `client.login(email='supra@mail', password='1337')` and `client.heartbeat()` to keep authorized session alive
* Use `client.quickReload()` to re-authenticate your session
* Use `client.listActiveMarketplaceMessages()` to list all items you have available for sell in the marketplace
* Use `client.collectAllResources()` to collect all resources on your ship
* Use `client.collectDailyReward()` to collect the daily reward

It seems that battle is simulated server-side so we have to simulate it client-side, and I don't have enough time to make it. Maybe later.
But you could join first battle and leave. Server would insta-simulate data as soon as you reconnect.

---
[![GitHub Metrics Updates](https://github.com/raelldottin/pythonstarships/actions/workflows/daily-run.yml/badge.svg)](https://github.com/raelldottin/pythonstarships/actions/workflows/dail-run.yml)
