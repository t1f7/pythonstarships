import xmltodict
import requests
import urllib.parse
import time
import datetime
from pprint import pprint
import random

from .security import (
    ChecksumCreateDevice,
    ChecksumTimeForDate,
    ChecksumPasswordWithString,
    ChecksumEmailAuthorize,
)
from .dotnet import DotNet


class User(object):

    id = 0
    name = None
    isAuthorized = False
    lastHeartBeat = 0

    def __init__(self, id, name, lastHeartBeat, isAuthorized):
        self.id = id
        self.name = name
        self.lastHeartBeat = lastHeartBeat
        self.isAuthorized = True if isAuthorized else False


class Client(object):

    # device data
    device = None

    # configuration
    salt = "5343"
    headers = {
        "Accept": "*/*",
        "Accept-Encoding": "identity",
        "User-Agent": "UnityPlayer/5.6.0f3 (UnityWebRequest/1.0, libcurl/7.51.0-DEV)",
        "X-Unity-Version": "5.6.0f3",
    }
    baseUrl = "https://api.pixelstarships.com/UserService/"

    # runtime data
    user = None
    accessToken = None
    freeStarbuxToday = 0
    freeStarbuxTodayTimestamp = 0
    dailyReward = 0
    dailyRewardTimestamp = 0
    rssCollected = 0
    rssCollectedTimestamp = 0
    mineralCollected = 0
    gasCollected = 0
    dronesCollected = dict()

    def __init__(self, device):
        self.device = device

    def parseUserLoginData(self, r):

        d = xmltodict.parse(r.content, xml_attribs=True)

        info = d["UserService"]["UserLogin"]
        userId = d["UserService"]["UserLogin"]["@UserId"]

        if not self.device.refreshToken:
            myName = "guest"
        else:
            myName = d["UserService"]["UserLogin"]["User"]["@Name"]
        LastHeartBeat = d["UserService"]["UserLogin"]["User"]["@LastHeartBeatDate"]

        if "FreeStarbuxReceivedToday" in r.text:
            self.freeStarbuxToday = int(
                r.text.split('FreeStarbuxReceivedToday="')[1].split('"')[0]
            )

        # keep it
        self.user = User(
            userId,
            myName,
            LastHeartBeat,
            self.device.refreshToken,
        )

    def getAccessToken(self, refreshToken=None):

        if self.accessToken:
            return self.accessToken

        url = (
            self.baseUrl
            + "DeviceLogin8?deviceKey="
            + self.device.key
            + "&advertisingKey=&isJailBroken=False&checksum="
            + ChecksumCreateDevice(self.device.key, self.device.name)
            + "&deviceType=DeviceType"
            + self.device.name
            + "&signal=False&languageKey="
            + self.device.languageKey
        )
        url += "&refreshToken=" + (
            self.device.refreshToken if self.device.refreshToken else ""
        )

        r = self.request(url, "POST")
        if not r or r.status_code != 200:
            print("[getAccessToken]", "failed with data:", r.text)
            return None

        if "errorCode" in r.text:
            print("[getAccessToken]", "got an error with data:", r.text)
            return None

        self.parseUserLoginData(r)

        if "accessToken" not in r.text:
            print("[getAccessToken]", "got no accessToken with data:", r.text)
            return None

        self.accessToken = r.text.split('accessToken="')[1].split('"')[0]

        return True

    def quickReload(self):
        self.accessToken = None
        return self.getAccessToken(self.device.refreshToken)

    def login(self, email=None, password=None):

        if not self.getAccessToken(self.device.refreshToken):
            print("[login] failed to get access token")
            return

        # double check if something goes wrong
        if not self.accessToken:
            return

        # authorization just fine with refreshToken, we're in da house
        if self.device.refreshToken and self.accessToken:
            return True

        # accessToken is enough for guest to play a tutorial
        if self.accessToken and not email:
            return True

        # login with credentials and accessToken
        ts = "{0:%Y-%m-%dT%H:%M:%S}".format(DotNet.validDateTime())
        checksum = ChecksumEmailAuthorize(
            self.device.key, email, ts, self.accessToken, self.salt
        )

        # if refreshToken was used we get acquire session without credentials
        if self.device.refreshToken:
            url = (
                self.baseUrl
                + "UserEmailPasswordAuthorize2?clientDateTime={}&checksum={}&deviceKey={}&accessToken={}&refreshToken={}".format(
                    ts,
                    checksum,
                    self.device.key,
                    self.accessToken,
                    self.device.refreshToken,
                )
            )

            r = self.request(url, "POST")

            if "Email=" not in r.text:
                print("[login] failed to authenticate with refreshToken:", r.text)
                return None

            self.parseUserLoginData(r)

        else:

            email = urllib.parse.quote(email)

            url = (
                self.baseUrl
                + "UserEmailPasswordAuthorize2?clientDateTime={}&checksum={}&deviceKey={}&email={}&password={}&accessToken={}".format(
                    ts, checksum, self.device.key, email, password, self.accessToken
                )
            )

            r = self.request(url, "POST")

            if "errorMessage=" in r.text:
                print(
                    "[login] failed to authorize with credentials with the reason:",
                    r.text,
                )
                return False

            if "refreshToken" not in r.text:
                print("[login] failed to acquire refreshToken with th reason", r.text)
                return False

            self.device.refreshTokenAcquire(
                r.text.split('refreshToken="')[1].split('"')[0]
            )

            if 'RequireReload="True"' in r.text:
                return self.quickReload()

        if "refreshToken" in r.text:
            self.device.refreshTokenAcquire(
                r.text.split('refreshToken="')[1].split('"')[0]
            )

        return True

    def loadShip(self):
        url = "https://api.pixelstarships.com/ShipService/GetShipByUserId?userId={}&accessToken={}&clientDateTime={}".format(
            self.user.id,
            self.accessToken,
            "{0:%Y-%m-%dT%H:%M:%S}".format(DotNet.validDateTime()),
        )
        r = self.request(url, "GET")
        print("loadShip", r, r.text)
        return r

    def collectAllResources(self):
        if self.user.isAuthorized and self.rssCollectedTimestamp + 120 < time.time():
            url = "https://api.pixelstarships.com/RoomService/CollectAllResources?itemType=None&collectDate={}&accessToken={}".format(
                "{0:%Y-%m-%dT%H:%M:%S}".format(DotNet.validDateTime()),
                self.accessToken,
            )
            r = self.request(url, "POST")
            if "errorMessage=" in r.text:
                d = xmltodict.parse(r.content, xml_attribs=True)
                pprint(d)

            self.rssCollectedTimestamp = time.time()
            mineralCollected = int(
                p["RoomService"]["CollectResources"]["Items"]["Item"][0]["@Quantity"]
            )
            gasCollected = int(
                p["RoomService"]["CollectResources"]["Items"]["Item"][1]["@Quantity"]
            )

            if self.mineralCollected and self.mineralCollected is not mineralCollected:
                print(f"Collected {mineralCollected - self.mineralCollected} minerals.")

            if self.gasCollected and self.gasCollected is not gasCollected:
                print(f"Collected {gasCollected - self.gasCollected} gas.")

            self.mineralCollected = mineralCollected
            self.gasCollected = gasCollected
            return True
        return False

    def collectDailyReward(self, argument=0):
        if datetime.datetime.now().time() == datetime.time(20, 0):
            self.dailyReward = 0

        if self.user.isAuthorized and not self.dailyReward:
            url = "https://api.pixelstarships.com/UserService/CollectDailyReward2?dailyRewardStatus=Box&argument={}&accessToken={}".format(
                argument,
                self.accessToken,
            )
            r = self.request(url, "POST")

            self.dailyReward = 1
            self.dailyRewardTimestamp = time.time()

            if "Rewards have been changed" in r.text:
                for i in range(9):
                    if self.collectDailyReward(i):
                        return True
                    else:
                        return False
                    time.sleep(random.uniform(2.0, 2.5))

            if "errorMessage=" in r.text:
                print("Daily reward was already collected from the dropship.")
                d = xmltodict.parse(r.content, xml_attribs=True)
                pprint(d)
                return False

            return True
        return False

    def collectMiningDrone(self, starSystemMarkerId):
        if self.user.isAuthorized and starSystemMarkerId not in self.dronesCollected:
            url = "https://api.pixelstarships.com/GalaxyService/CollectMarker2?starSystemMarkerId={}&checksum={}&clientDateTime={}&accessToken={}".format(
                starSystemMarkerId,
                (
                    ChecksumTimeForDate(DotNet.get_time())
                    + ChecksumPasswordWithString(self.accessToken)
                ),
                "{0:%Y-%m-%dT%H:%M:%S}".format(DotNet.validDateTime()),
                self.accessToken,
            )
            r = self.request(url, "POST")
            if "errorMessage=" in r.text:
                d = xmltodict.parse(r.content, xml_attribs=True)
                pprint(d)
                print(url)
                return False

            self.dronesCollected[starSystemMarkerId] = 1
            return True
        return False

    def placeMiningDrone(self, missionDesignId, missionEventId):
        if self.user.isAuthorized:
            url = "https://api.pixelstarships.com/MissionService/SelectInstantMission3?missionDesignId={}&missionEventId={}&messageId=0&clientDateTime={},clientNumber=0&checksum={}&accessToken={}".format(
                missionDesignId,
                missionEventId,
                "{0:%Y-%m-%dT%H:%M:%S}".format(DotNet.validDateTime()),
                (
                    ChecksumTimeForDate(DotNet.get_time())
                    + ChecksumPasswordWithString(self.accessToken)
                ),
                self.accessToken,
            )
            r = self.request(url, "POST")
            if "errorMessage=" in r.text:
                d = xmltodict.parse(r.content, xml_attribs=True)
                pprint(d)
                print(url)
                return False
            return True
        return False

    def grabFlyingStarbux(self, quantity):
        if datetime.datetime.now().time() == datetime.time(20, 0):
            self.freeStarbuxToday = 0

        if (
            self.user.isAuthorized
            and self.freeStarbuxToday < 10
            and self.freeStarbuxTodayTimestamp + 120 < time.time()
        ):
            t = DotNet.validDateTime()

            url = (
                self.baseUrl
                + "AddStarbux2?quantity={}&clientDateTime={}&checksum={}&accessToken={}".format(
                    quantity,
                    "{0:%Y-%m-%dT%H:%M:%S}".format(t),
                    ChecksumTimeForDate(DotNet.get_time())
                    + ChecksumPasswordWithString(self.accessToken),
                    self.accessToken,
                )
            )
            r = self.request(url, "POST")

            if "Email=" not in r.text:
                d = xmltodict.parse(r.content, xml_attribs=True)
                pprint(d)
                print(f"[grabFlyingStarbux] failed with next issue: {r.text}")
                return False

            self.freeStarbuxToday = int(
                r.text.split('FreeStarbuxReceivedToday="')[1].split('"')[0]
            )
            self.freeStarbuxTodayTimestamp = time.time()

            return True
        return False

    def heartbeat(self):

        if self.user.lastHeartBeat:
            hours = self.user.lastHeartBeat.split("T")[1]
            seconds = hours.split(":")[-1]
            if DotNet.validDateTime().second == int(seconds):
                return

        t = DotNet.validDateTime()

        url = (
            self.baseUrl
            + "HeartBeat4?clientDateTime={}&checksum={}&accessToken={}".format(
                "{0:%Y-%m-%dT%H:%M:%S}".format(t),
                ChecksumTimeForDate(DotNet.get_time())
                + ChecksumPasswordWithString(self.accessToken),
                self.accessToken,
            )
        )

        r = self.request(url, "POST")
        success = False

        if r.status_code == 200 and 'success="t' in r.text:
            success = True
        else:
            print("Heartbeat fail")

        self.user.lastHeartBeat = "{0:%Y-%m-%dT%H:%M:%S}".format(t)

        return success

    def request(self, url, method=None, data=None):
        r = requests.request(method, url, headers=self.headers, data=data)
        return r
