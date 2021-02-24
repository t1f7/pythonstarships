from datetime import datetime, timedelta

class DotNet(object):

    @classmethod
    def validDateTime(self):
        # I can't remember why I did this, but this could be a valid reason
        # why code won't work on your PC
        # timezone must be UTC (maybe)
        return datetime.now() - timedelta(hours=3)

    @classmethod
    def ticks(self, dt):
        return int((dt - datetime(1, 1, 1)).total_seconds() * 10000000)

    @classmethod
    def get_time(self):
        return self.ticks(self.validDateTime())
