import datetime
import nextcord
from discord.ext import commands, tasks
import inspect
import pytz
import requests
import json
import os

intents = nextcord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix='!',
                   intents=intents,
                   owner_id=785037540155195424)

bot_ids = [1143521016031744025, 1126430942924386315]


def log(text: str, type: str=None):
    with open("log.txt", mode="r+") as logging:
        txt = logging.read()
        if type == "clear":
            logging.truncate(0)
            logging.seek(0)
            logging.write("Cleared")
        else:
            logging.truncate(0)
            logging.seek(0)
            logging.write(f"{txt}\nin {inspect.stack()[1].function} @ {datetime.datetime.now(tz=pytz.timezone('Europe/Brussels')).strftime('%m/%d, %H:%M:%S')} : {text}")


def errormessage(error):
    return f"An error occured. if this persists please report it in the zeepkist modding server: [here](https://discord.gg/a4FxG9RpV3) in this thread: https://discord.com/channels/972933002516647986/1126438917420359691 \n \n Error: `{str(error)}`"

def format_time(time: float):
    """
    you go girl <3
    """
    minutes = int(time // 60)
    seconds = int(time % 60)
    milliseconds = int((time % 1) * 1000)
    formatted_time = f"{minutes:02d}:{seconds:02d}:{milliseconds:03d}"
    return formatted_time

def hex_to_rgb(hex):
  return tuple(int(hex[i:i+2], 16) for i in (0, 2, 4))


def getgtruser(id: int=None, discid: int=None):
    """
    remember fwogiie,
    to get username: steamName
    to get user steam ID: steamId
    to get user discord ID: discordId

    stay awesome girl <3
    """
    if id != None:
        req = requests.get(f"https://api.zeepkist-gtr.com/users/{id}")
        if req.status_code != 200:
            return [False, req.status_code]
        else:
            return [True, json.loads(req.text)]
    elif discid != None:
        req = requests.get(f"https://api.zeepkist-gtr.com/users/discord/{discid}")
        if req.status_code != 200:
            return [False, req.status_code]
        else:
            return [True, json.loads(req.text)]


def getgtrrecord(id: int):
    """
    {
  "id": 0,
  "time": 0,
  "splits": [
    0
  ],
  "isValid": true,
  "gameVersion": "string",
  "modVersion": "string",
  "level": "string",
  "user": 0
   }

stay silly girl :3
    """
    return json.loads(requests.get(f"https://api.zeepkist-gtr.com/records/{id}").text)

def getgtruserrankings(limit: int, offset: int):
    """
    {
  "totalAmount": 0,
  "rankings": [
    {
      "user": {
        "id": 0,
        "steamId": "string",
        "steamName": "string",
        "discordId": "string"
      },
      "amountOfWorldRecords": 0,
      "position": 0,
      "score": 0
    }
  ]
}

good girl :>
    """
    return json.loads(requests.get(f"https://api.zeepkist-gtr.com/users/rankings?Limit={limit}&Offset={offset}").text)

def getgtruserrank(id: int):
    """
    {
  "amountOfWorldRecords": 0,
  "position": 0,
  "score": 0
}

girl!
    """
    return json.loads(requests.get(f"https://api.zeepkist-gtr.com/users/ranking/{id}").text)

def checkzeeplist(filename: str):
    """
    returns True if the filename is "zeeplist"
    useful for quite a bit of stuff :3

    go girl! :>
    """
    if filename.split(".")[1:][0] == "zeeplist":
        return True
    else:
        return False

def dumppl(pl):
    with open("playlist.zeeplist", 'w') as f:
        json.dump(pl, f, indent=2)

def renamepl(name):
    os.rename("playlist.zeeplist", f"{name}.zeeplist")

def undorename(name):
    os.rename(f"{name}.zeeplist", "playlist.zeeplist")

def addgtruser(discid: str, user: str):
    with open("users.json", 'r') as f:
        data = json.loads(f.read())
    with open("users.json", 'w') as ft:
        data["linked"][discid] = user
        json.dump(data, ft, indent=2)

def add_usercache(id: int):
    """
    this is obsolete, don't use this fwogiie <3
    """
    user = getgtruser(id=id)
    if user[0]:
        with open("users.json", 'r') as f:
            data = json.loads(f.read())
        with open("users.json", 'w') as ft:
            data["usercache"][str(id)] = user[1]
            json.dump(data, ft, indent=2)

def get_linked_users():
    with open("users.json", 'r') as f:
        return json.loads(f.read())["linked"]

def all_24hours():
    return [
        datetime.time(hour=0, minute=1), datetime.time(hour=1, minute=1), datetime.time(hour=2, minute=1),
        datetime.time(hour=3, minute=1), datetime.time(hour=4, minute=1), datetime.time(hour=5, minute=1),
        datetime.time(hour=6, minute=1), datetime.time(hour=7, minute=1), datetime.time(hour=8, minute=1),
        datetime.time(hour=9, minute=1), datetime.time(hour=10, minute=1), datetime.time(hour=11, minute=1),
        datetime.time(hour=12, minute=1), datetime.time(hour=13, minute=1), datetime.time(hour=14, minute=1),
        datetime.time(hour=15, minute=1), datetime.time(hour=16, minute=1), datetime.time(hour=17, minute=1),
        datetime.time(hour=18, minute=1), datetime.time(hour=19, minute=1), datetime.time(hour=20, minute=1),
        datetime.time(hour=21, minute=1), datetime.time(hour=22, minute=1), datetime.time(hour=23, minute=1)
    ]