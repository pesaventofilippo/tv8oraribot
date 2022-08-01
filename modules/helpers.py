from datetime import datetime
from json import load as jsload
from os.path import abspath, dirname, join

with open(join(dirname(abspath(__file__)), "../settings.json")) as settings_file:
    js_settings = jsload(settings_file)

adminIds = js_settings["admins"]

_days = {
    1: "Lunedì",
    2: "Martedì",
    3: "Mercoledì",
    4: "Giovedì",
    5: "Venerdì",
    6: "Sabato",
    7: "Domenica"
}

def dateToString(date: datetime):
    today = datetime.now().date()
    return f"{_days[date.isoweekday()]} {date.day}" if date.date() != today else "Oggi"

def isAdmin(chatId=None):
    return adminIds if not chatId else (chatId in adminIds)
