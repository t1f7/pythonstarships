import random
import os


class Device(object):

    name = "Android"
    key = None
    refreshToken = None
    languageKey = "en"
    DB = "/Users/rdottin/Documents/Personal/pythonstarships/collectallresources/.device"
    authentication_string = None

    def __init__(
        self, name="DeviceTypeMac", key=None, language="en", authentication_string=None
    ):

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
        self.authentication_string = authentication_string
        if authentication_string:
            self.DB = None

        if not self.load():
            self.save()

    def refreshTokenAcquire(self, refreshToken):

        self.refreshToken = refreshToken
        self.save()

    def reset(self):
        if self.DB:
            os.unlink(self.DB)

    def save(self):
        if self.DB:
            with open(self.DB, "w+") as f:
                f.write(
                    "{}|{}|{}|{}".format(
                        self.name, self.key, self.refreshToken, self.languageKey
                    )
                )

    def load(self):
        if self.authentication_string:
            data = self.authentication_string.split("|")

        elif not os.path.isfile(self.DB):
            return False

        else:
            with open(self.DB, "r") as f:
                data = f.read().split("|")

        self.name = data[0]
        self.key = data[1]
        self.refreshToken = data[2] if len(data[2]) > 3 else None
        self.languageKey = data[3]

        return True
