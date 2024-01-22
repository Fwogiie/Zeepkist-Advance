import datetime
import nextcord
from discord.ext import commands, tasks
import inspect
import pytz
import requests
import json

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


def getgtruser(id: int):
    """
    remember fwogiie,
    to get username: steamName
    to get user steam ID: steamId
    to get user discord ID: discordId

    stay awesome girl <3
    """
    return json.loads(requests.get(f"https://api.zeepkist-gtr.com/users/{id}").text)


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
