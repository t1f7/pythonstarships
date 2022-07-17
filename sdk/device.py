import random
import os


class Device(object):

    name = "DeviceTypeMac"
    key = None
    refreshToken = None
    languageKey = "en"
    DB = "/Users/rdottin/Documents/Personal/pythonstarships/collectallresources/.device"

    def __init__(self, name="DeviceTypeMac", key=None, language="en"):

        if not key:
            key = "{}-{}-{}-{}-{}".format(
                "".join(random.choice("0123456789abcdef") for n in range(8)),
                "".join(random.choice("0123456789abcdef") for n in range(4)),
                "".join(random.choice("0123456789abcdef") for n in range(4)),
                "".join(random.choice("0123456789abcdef") for n in range(4)),
                "".join(random.choice("0123456789abcdef") for n in range(12)),
            )

        self.name = name
        self.key = key
        self.languageKey = language

        if not self.load():
            self.save()

    def refreshTokenAcquire(self, refreshToken):

        self.refreshToken = refreshToken
        self.save()

    def reset(self):

        os.unlink(self.DB)

    def save(self):

        with open(self.DB, "w+") as f:
            f.write(
                "{}|{}|{}|{}".format(
                    self.name, self.key, self.refreshToken, self.languageKey
                )
            )

    def load(self):

        if not os.path.isfile(self.DB):
            return False

        with open(self.DB, "r") as f:
            data = f.read().split("|")

        self.name = data[0]
        self.key = data[1]
        self.refreshToken = data[2] if len(data[2]) > 3 else None
        self.languageKey = data[3]

        return True
