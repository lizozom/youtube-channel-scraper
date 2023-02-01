from datetime import datetime

def getDatetime(timestr):
    datetime.fromisoformat(timestr.replace("Z", "+00:00"))