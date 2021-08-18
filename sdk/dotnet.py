from datetime import datetime, timedelta

class DotNet(object):

    @classmethod
    def validDateTime(self):
        return datetime.utcnow()

    @classmethod
    def ticks(self, dt):
        return int((dt - datetime(1, 1, 1)).total_seconds() * 10000000)

    @classmethod
    def get_time(self):
        return self.ticks(self.validDateTime())
