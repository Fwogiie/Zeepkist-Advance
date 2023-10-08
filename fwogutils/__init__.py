import datetime
import requests
import json
import os
import nextcord
import re
import discord
from discord.ext import commands, tasks
from nextcord.errors import HTTPException
import privaat
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
import inspect
import pytz
import calendar
import urllib
import subprocess
import ast
import copy
import sys

intents = nextcord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix='!',
                   intents=intents,
                   help_command=None,
                   owner_id=785037540155195424)

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
            logging.write(f"{txt}\nin {inspect.stack()[1].function} @ {datetime.datetime.now(tz=pytz.timezone('Europe/Brussels')).strftime('%m/%d, %H:%M')} : {text}")

def errormessage(error):
    return f"An error occured. if this persists please report it in the zeepkist modding server: [here](https://discord.gg/a4FxG9RpV3) in this thread: https://discord.com/channels/972933002516647986/1126438917420359691 \n \n Error: `{str(error)}`"
