from datetime import datetime

def getDatetime(timestr):
    return datetime.fromisoformat(timestr.replace("Z", "+00:00"))