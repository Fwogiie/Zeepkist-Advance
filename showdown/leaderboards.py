import json
from datetime import datetime
import nextcord
from nextcord.ext import tasks
import fwogutils
from fwogutils import bot, log
import time

async def startup_logic():
    log("Showndown Leaderboards statup logic has been called.")

# TODO quali leaderboard
@tasks.loop(minutes=5, reconnect=True)
async def quali_leaderboard():
    log("Qualifier leaderboard updating...")
    with open("showdown/storage.json", "r") as read:
        storage = json.loads(read.read())
