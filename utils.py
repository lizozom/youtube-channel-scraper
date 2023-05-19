from datetime import datetime

def get_datetime(timestr):
    return datetime.fromisoformat(timestr.replace("Z", "+00:00"))