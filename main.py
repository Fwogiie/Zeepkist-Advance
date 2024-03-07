import datetime
import time
import aiohttp
import requests
import json
import os
import nextcord
import re
import discord
from discord.ext import commands, tasks
from nextcord.errors import HTTPException
import privaat
import urllib
from urllib.parse import quote
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
import inspect
import pytz
import calendar
import subprocess
import ast
import copy
import sys
import fwogutils
from fwogutils import bot as bot
from fwogutils import log as log
from fwogutils import format_time as format_time
from fwogutils import views
from nextcord import webhook, Webhook
import random
from nextcord.components import Button
import asyncio
import websockets
from itertools import count
from fwogutils import GTR as GTR
from fwogutils import Zworp as Zworp

bot.load_extension("onami")

ids = []
lvlsamount = 0
gitgud = bool


async def fetch(channelid: int, amount: int, oldest_first: bool, fetched_react: int, messageid: int=0):
    global ids, lvlsamount, gitgud
    log(f"reached with channelid: {channelid}, amount: {amount}, oldest_first: {oldest_first}, fetched_react: {fetched_react}, messageid: {messageid}")
    gitgud = False
    ids = []
    patterna = r'https://steamcommunity\.com/sharedfiles/filedetails/\?id=\d+'
    channel = bot.get_channel(channelid)
    await status(f"Fetching messages.")
    async for x in channel.history(limit=amount, oldest_first=False):
        if gitgud is True:
            if oldest_first is True:
                ids.reverse()
            return
        if x.id == messageid:
            gitgud = True
            log("set gitgud to True.")
        if fetched_react == 1:
            await x.add_reaction("✅")
        if re.findall(patterna, x.content):
            if fetched_react == 2:
                await x.add_reaction("✅")
            workshop_urls = re.findall(patterna, x.content)
            for url in workshop_urls:
                pattern = r'id=(\d+)'
                tmp = re.findall(pattern, url)
                for x in tmp:
                    lvlsamount += 1
                    ids.append(x)
                    if makekoc is True:
                        ids.append(2973690373)
    await status(f"\nFetched {lvlsamount} levels.\n")

cont = nextcord.InteractionMessage
statuslog = ""


async def status(status: str, reset: bool=False):
    global cont, statuslog
    log(f"reached with status: {status}, reset: {reset}")
    statuslog += f"{status}\n"
    try:
        if reset is False:
            await cont.edit(content=f"Creating playlist. please wait. this might take a hot minute depending on the amount of levels. \n \n Status log: ```{statuslog}```")
        else:
            statuslog = "Log has been Reset.\n\n"
            await cont.edit(content=f"Creating playlist. please wait. this might take a hot minute depending on the amount of levels. \n \n Status log: ```{statuslog}```")
    except HTTPException:
        statuslog = "Cleared log Because of character limit.\n\n"
        await cont.edit(content=f"Creating playlist. please wait. this might take a hot minute depending on the amount of levels. \n \n Status log: ```{statuslog}```")

levelnames = []
lvluids = []
unfound = 0


@bot.slash_command(name="create_playlist", description="Create a playlist from a discord level submissions channel! (works for zeepkist only!)")
async def bigstuff(ctx,
                   channel: nextcord.TextChannel=nextcord.SlashOption(description="The channel to subtract the levels from", required=True),
                   amount_of_messages: int=nextcord.SlashOption(description="The amount of levels to subtract", required=True),
                   playlistname: str=nextcord.SlashOption(description="The name of the playlist that gets sent once the playlist is done!", required=True),
                   oldest_first: bool=nextcord.SlashOption(description="When True (wich it is defaulted to) the oldest level fetched will be first in the playlist!", required=False, default=True),
                   react_on_fetched: int=nextcord.SlashOption(description="Choose how the bot reacts with '✅' (useful to keep track of already played levels)", required=False,
                                                              choices={"React to every single fetched message.": 1, "React to only the level submissions. (Default)": 2, "React to nothing.": 3}, default=2),
                   private: bool = nextcord.SlashOption(description="Sends the playlist in a type of message that only you can see.", required=False, default=False),
                   thread: nextcord.Thread=nextcord.SlashOption(description="If you want to fetch levels from a thread.", required=False, default=None)):
    global ids, lvlsamount, cont, lvlnames, statuslog, unfound
    log(f"reached by {ctx.user} with: channel: {channel}, amount_of_messages: {amount_of_messages},"
        f" playlistname: {playlistname}, oldest_first: {oldest_first}, react_on_fetched: {react_on_fetched},"
        f" private: {private}, thread: {thread}, ")
    statuslog = "Executing command:\n\n"
    cont = ctx
    lvlsamount = 0
    unfound = 0
    ids = []
    cont = await ctx.send("Waiting for status.", ephemeral=private)
    if thread != None:
        await fetch(channelid=thread.id, amount=amount_of_messages, oldest_first=oldest_first, fetched_react=react_on_fetched)
    else:
        await fetch(channelid=channel.id, amount=amount_of_messages, oldest_first=oldest_first, fetched_react=react_on_fetched)
    print(ids)
    await create_playlist(playlistname, lvlsamount)
    await status("Fetching all required info and Adding levels to playlist. . .")
    for i in ids:
        req = requests.get(f"https://api.zworpshop.com/levels/workshop/{i}")
        if req.status_code == 404:
            unfound += 1
            await status("Couldnt find a level.")
        else:
            reqtxt = req.text
            lvl = json.loads(reqtxt)[0]
            await add_level(lvl)
    os.rename("playlist.zeeplist", f"{playlistname}.zeeplist")
    await cont.edit("The playlist has been generated."
                   " To import the playlist into the host controls simply drag the file below into this specific directory: `%userprofile%\AppData\Roaming\Zeepkist\Playlists`."
                   " to easily access this directory: (for windows only) press Win+R and paste the directory in the text box.", file=nextcord.File(f'{playlistname}.zeeplist'))
    os.rename(f"{playlistname}.zeeplist", "playlist.zeeplist")
    if unfound > 0:
        await ctx.send(f"Failed to find {unfound} levels.")


async def create_playlist(name: str, amountoflvls: int):
    log(f"name: {name}, amountoflvls: {amountoflvls}")
    await status(f"Creating playlist {name} for {amountoflvls} levels. . .")
    playlist = {
    "name": name,
    "amountOfLevels": amountoflvls,
    "roundLength": 480.0,
    "shufflePlaylist": False,
    "UID": [],
    "levels": []
}

# Save the playlist as JSON in a file
    with open("playlist.zeeplist", "w") as file:
        json.dump(playlist, file, indent=2)


async def add_level(lvl: str):
    log(f"called! with level WSID: {lvl['workshopId']}")
    with open("playlist.zeeplist", "r") as file:
        playlist = json.load(file)

    # Create a new level tuple
    new_level = (
        {
            "UID": lvl["fileUid"],
            "WorkshopID": lvl["workshopId"],
            "Name": lvl["name"],
            "Author": lvl["fileAuthor"]
        }
    )

    # Add the new level tuple to the "levels" list
    playlist["levels"].append(new_level)

    # Save the updated playlist back to the file
    with open("playlist.zeeplist", "w") as file:
        json.dump(playlist, file, indent=2)


@bot.event
async def on_application_command_error(ctx, error):
    log(error)
    print(error)
    try:
        await ctx.send(f"{fwogutils.errormessage(error)}", ephemeral=True)
    except nextcord.errors.InteractionResponded:
        pass


@bot.event
async def on_command_error(ctx, error):
    log(error)


@bot.is_owner
@bot.command(name="log")
async def ownlog(ctx, type: str, *, text: str=None):
    try:
        if type == "send" and text is None:
            await ctx.reply("yes ma'am", file=nextcord.File("log.txt"))
        elif type == "send" and text == "true":
            with open("log.txt", 'r') as fr:
                ctn = {1: "", 2: 0, 3: 5}
                block = False
                splitted = fr.read().split('\n')
                while block is False:
                    logblock = splitted[ctn[2]:ctn[3]]
                    if logblock:
                        for x in logblock:
                            ctn[1] += f"{x}\n"
                        ctn[3] += 5
                        ctn[2] += 5
                        await ctx.send(f"```{ctn[1]}```")
                        ctn[1] = ""
                    else:
                        block = True
        elif type == "add":
            log(text)
            await ctx.reply(f"Added `{text}` to log.txt")
        elif type == "clear":
            log("bruh", "clear")
            await ctx.reply("cleared log.txt")
        else:
            await ctx.reply("Yo fucking stupid bruv?")
    except HTTPException as ewwor:
        await ctx.send(f"HTTPSException: {ewwor}")


@bot.is_owner
@bot.command(name="debug")
async def debug(ctx, type: str, value: str):
    if type == "exe":
        try:
            func = globals()[value]
            await func()
        except Exception as ewwor:
            log(ewwor)
            await ctx.send("Something wrong happened.")
    else:
        await ctx.send("No such type found.")

cmdmsg = int


@bot.message_command(name="create-playlist")
async def msgcmd(ctx, msg):
    log(f"msgcmd called by {ctx.user} for msg {msg.content} ({msg.id})")
    global cmdmsg, makekoc, makemontly, tooold
    makekoc = False
    makemontly = False
    tooold = 0
    modal = Crtpl(guildid=ctx.guild.id)
    cmdmsg = msg.id
    await ctx.response.send_modal(modal)

makekoc = bool


class Kocfake(nextcord.ui.Select):
    def __init__(self):
        options = [
            nextcord.SelectOption(label="Yes", value="True"),
            nextcord.SelectOption(label="No", value="False")
        ]
        super().__init__(
            placeholder="Make KoC compatible?",
            options=options,
            min_values=1,
            max_values=1
        )

    async def callback(self, ctx: nextcord.Interaction) -> None:
        global makekoc, ids, lvlsamount, cont, lvlnames, statuslog, unfound, plname
        log("from Kocfake: callback called")
        Koc().stop()
        if self.values[0] == 'True':
            makekoc = True
        elif self.values[0] == 'False':
            makekoc = False
        cont = ctx
        lvlsamount = 0
        unfound = 0
        ids = []
        cont = await ctx.send("Waiting for status.", ephemeral=True)
        await fetch(channelid=ctx.channel.id, amount=9999, oldest_first=True, fetched_react=2, messageid=cmdmsg)
        print(ids)
        await create_playlist(plname, lvlsamount)
        await status("Fetching all required info and Adding levels to playlist. . .")
        for i in ids:
            req = requests.get(f"https://api.zworpshop.com/levels/workshop/{i}")
            if req.status_code == 404:
                unfound += 1
                await status("Couldnt find a level.")
            else:
                reqtxt = req.text
                lvl = json.loads(reqtxt)[0]

                await add_level(lvl)
        os.rename("playlist.zeeplist", f"{plname}.zeeplist")
        await cont.edit("The playlist has been generated."
                        " To import the playlist into the host controls simply drag the file below into this specific directory: `%userprofile%\AppData\Roaming\Zeepkist\Playlists`."
                        " to easily access this directory: (for windows only) press Win+R and paste the directory in the text box.",
                        file=nextcord.File(f'{plname}.zeeplist'))
        os.rename(f"{plname}.zeeplist", "playlist.zeeplist")
        if unfound > 0:
            await ctx.send(f"Failed to find {unfound} levels.", ephemeral=True)


class Koc(nextcord.ui.View):
    def __init__(self):
        super().__init__(timeout=60)
        self.add_item(Kocfake())


class Mn(nextcord.ui.Modal):
    def __init__(self):
        super().__init__("Monthly Playlist Creation")  # Modal title

        # Create a text input and add it to the modal
        self.month = nextcord.ui.TextInput(
            label="Month Number the level has to be created in",
            min_length=0,
            max_length=2,
            placeholder=f"example: {datetime.datetime.now().month}",
            default_value=f"{datetime.datetime.now().month - 1}"
        )
        self.add_item(self.month)

    async def callback(self, ctx: nextcord.Interaction) -> None:
        global makemontly, ids, lvlsamount, cont, lvlnames, statuslog, unfound, plname, tooold
        log("from Mn: callback called")
        cont = ctx
        lvlsamount = 0
        unfound = 0
        ids = []
        cont = await ctx.send("Waiting for status.", ephemeral=True)
        await fetch(channelid=ctx.channel.id, amount=9999, oldest_first=True, fetched_react=2, messageid=cmdmsg)
        await create_playlist(plname, lvlsamount)
        await status("Fetching all required info and Adding levels to playlist. . .")
        for i in ids:
            req = requests.get(f"https://api.zworpshop.com/levels/workshop/{i}")
            if req.status_code == 404:
                unfound += 1
            else:
                reqtxt = req.text
                lvl = json.loads(reqtxt)[0]
                crtm = lvl["createdAt"]
                parts = crtm.split("-")
                lvlmonthfake = parts[1]
                lvlmonth = int(lvlmonthfake[1])
                if lvlmonth == int(self.month.value):
                    await add_level(lvl)
                else:
                    tooold += 1
        os.rename("playlist.zeeplist", f"{plname}.zeeplist")
        await cont.edit("The playlist has been generated."
                        " To import the playlist into the host controls simply drag the file below into this specific directory: `%userprofile%\AppData\Roaming\Zeepkist\Playlists`."
                        " to easily access this directory: (for windows only) press Win+R and paste the directory in the text box.",
                        file=nextcord.File(f'{plname}.zeeplist'))
        os.rename(f"{plname}.zeeplist", "playlist.zeeplist")
        if unfound > 0:
            await ctx.send(f"Failed to find {unfound} levels.", ephemeral=True)
        if tooold > 0:
            await ctx.send(f"{tooold} Levels were too old.", ephemeral=True)


tooold = 0
makemontly = bool

class Monthlyfake(nextcord.ui.Select):
    def __init__(self):
        options = [
            nextcord.SelectOption(label="Yes", value="True"),
            nextcord.SelectOption(label="No", value="False")
        ]
        super().__init__(
            placeholder="Make monthly compatible?",
            options=options,
            min_values=1,
            max_values=1
        )

    async def callback(self, ctx: nextcord.Interaction) -> None:
        global makemontly, ids, lvlsamount, cont, lvlnames, statuslog, unfound, plname, tooold
        log("from Monthlyfake: callback called")
        Monthly().stop()
        if self.values[0] == 'True':
            makemontly = True
        elif self.values[0] == 'False':
            makemontly = False
        if makemontly is True:
            await ctx.response.send_modal(Mn())
            await Mn().wait()
        cont = ctx
        lvlsamount = 0
        unfound = 0
        ids = []
        cont = await ctx.send("Waiting for status.", ephemeral=True)
        await fetch(channelid=ctx.channel.id, amount=9999, oldest_first=True, fetched_react=2, messageid=cmdmsg)
        await create_playlist(plname, lvlsamount)
        await status("Fetching all required info and Adding levels to playlist. . .")
        for i in ids:
            req = requests.get(f"https://api.zworpshop.com/levels/workshop/{i}")
            if req.status_code == 404:
                unfound += 1
                await status("Couldnt find a level.")
            else:
                reqtxt = req.text
                lvl = json.loads(reqtxt)[0]
                await add_level(lvl)
        os.rename("playlist.zeeplist", f"{plname}.zeeplist")
        await cont.edit("The playlist has been generated."
                        " To import the playlist into the host controls simply drag the file below into this specific directory: `%userprofile%\AppData\Roaming\Zeepkist\Playlists`."
                        " to easily access this directory: (for windows only) press Win+R and paste the directory in the text box.",
                        file=nextcord.File(f'{plname}.zeeplist'))
        os.rename(f"{plname}.zeeplist", "playlist.zeeplist")
        if unfound > 0:
            await ctx.send(f"Failed to find {unfound} levels.", ephemeral=True)


class Monthly(nextcord.ui.View):
    def __init__(self):
        super().__init__(timeout=60)
        self.add_item(Monthlyfake())

plname = ""
class Crtpl(nextcord.ui.Modal):
    def __init__(self, guildid: int):
        super().__init__("playlist creation")  # Modal title

        # Create a text input and add it to the modal
        self.name = nextcord.ui.TextInput(
            label="Playlist name",
            min_length=2,
            max_length=50,
        )
        self.add_item(self.name)
        self.guildid = guildid

    async def callback(self, ctx: nextcord.Interaction) -> None:
        global ids, lvlsamount, cont, lvlnames, statuslog, unfound, plname
        log("from Crtpl: callback called")
        statuslog = "Executing command:\n\n"
        plname = self.name.value
        if ctx.guild.id == 1083812526917177514:
            await ctx.send(
                "This server is marked as the CTR discord, would you like to make this playlist Kick or Clutch compatible? clicking yes below will make it so the playlist has the KoC voting level inbetween each level!",
                view=Koc(), ephemeral=True)
            await Koc().wait()
        elif ctx.guild.id == 966694897799286784:
            await ctx.send("This server is marked as R0nanC's Content server, do you wish to make this playlist compatible for the monthly playlist?", view=Monthly(), ephemeral=True)
            await Monthly().wait()
        cont = ctx
        lvlsamount = 0
        unfound = 0
        ids = []
        cont = await ctx.send("Waiting for status.", ephemeral=True)
        await fetch(channelid=ctx.channel.id, amount=9999, oldest_first=True, fetched_react=2, messageid=cmdmsg)
        print(ids)
        await create_playlist(self.name.value, lvlsamount)
        await status("Fetching all required info and Adding levels to playlist. . .")
        for i in ids:
            req = requests.get(f"https://api.zworpshop.com/levels/workshop/{i}")
            if req.status_code == 404:
                unfound += 1
                await status("Couldnt find a level.")
            else:
                reqtxt = req.text
                lvl = json.loads(reqtxt)[0]
                await add_level(lvl)
        os.rename("playlist.zeeplist", f"{self.name.value}.zeeplist")
        await cont.edit("The playlist has been generated."
                        " To import the playlist into the host controls simply drag the file below into this specific directory: `%userprofile%\AppData\Roaming\Zeepkist\Playlists`."
                        " to easily access this directory: (for windows only) press Win+R and paste the directory in the text box.",
                        file=nextcord.File(f'{self.name.value}.zeeplist'))
        os.rename(f"{self.name.value}.zeeplist", "playlist.zeeplist")
        if unfound > 0:
            await ctx.send(f"Failed to find {unfound} levels.", ephemeral=True)


submissionschannels = []
leaderboards = {}
@bot.event
async def on_ready():
    global submissionschannels, leaderboards
    log(f"Loaded up! with bot ID: {bot.user.id}")
    log("initializing startup guilds")
    await bot.change_presence(activity=discord.Activity(type=discord.ActivityType.watching, name="For level submissions"))
    for guild in bot.guilds:
        print(f"Connected to guild: {guild.name} ({guild.id}) with {guild.member_count} members.")
        log(f"Connected to guild: {guild.name} ({guild.id}) with {guild.member_count} members.")
    log("initializing startup cache for submission channels.")
    # with open("data.json", "r") as f:
        # data = json.load(f)
        # submissionschannels = data["submission-channels"]
        # log(f"submission channels cache succeeded.")
    log("initializing startup cache for live leaderboards.")
    with open("data.json", "r") as f:
        data = json.load(f)
        leaderboards = data["leaderboards"]
        log(f"leaderboards cache succeeded.")
        log("updating the live leaderboards cause of restart.")
        leaderboard = await bot.get_channel(1203645881279184948).fetch_message(leaderboards['rankings'])
        await rankingsfunc(fwogutils.getgtruserrankings(limit=100, offset=0))
        log("Process done to the GTR rankings leaderboard.")
        await listen_forever()

def updatesubchannels():
    global submissionschannels
    log("called")
    with open("data.json", "r") as f:
        data = json.load(f)
        submissionschannels = data["submission-channels"]


def addlvl(lvl: dict, channelid: int):
    with open("data.json", 'r') as f:
        data = json.load(f)
    with open("data.json", 'w') as ft:
        for x in data["submission-channels"]:
            if x['channelid'] == channelid:
                x['levels'].append({"wsid": lvl['wsid'], "lvlname": lvl['lvlname'], "lvluid": lvl['lvluid'], "lvlatn": lvl['lvlatn']})
        json.dump(data, ft, indent=2)


async def lastmsgsaction(type: int, chan: int, msgs: list):
    log(f"reached with channel: {chan} for msgs {msgs}")
    with open("data.json", 'r') as f:
        data = json.load(f)
        for x in data["submission-channels"]:
            if x['channelid'] == chan and type == 1:
                x['lastsentmsgs'] = msgs
            elif x['channelid'] == chan and type == 2:
                try:
                    if len(x['lastsentmsgs']) > 0:
                        for w in x["lastsentmsgs"]:
                            chan = await bot.fetch_channel(x['channelid'])
                            msg = await chan.fetch_message(w)
                            await msg.delete()
                except nextcord.errors.Forbidden:
                    log("Did not have permissions to delete.")
        if type == 1:
            with open("data.json", 'w') as ft:
                json.dump(data, ft, indent=2)


def checkduplicate(data: list, id: int=None):
    duplicheck = []
    duplilevels = []
    hasdupli = False
    if id is None:
        for x in data:
            if x not in duplicheck:
                duplicheck.append(x)
            elif x in duplicheck and x not in duplilevels:
                duplilevels.append(x)
                hasdupli = True
        if hasdupli is False:
            return False
        else:
            return {"duplilvls": duplilevels}
    elif id is not None:
        for x in data:
            if id == x["wsid"]:
                return True
        return False


def clearlevels(channelid: int):
    with open("data.json", 'r') as f:
        data = json.load(f)
    with open("data.json", 'w') as ft:
        for x in data["submission-channels"]:
            if x['channelid'] == channelid:
                x['levels'] = []
        json.dump(data, ft, indent=2)


@tasks.loop(seconds=5, reconnect=True)
async def submission_checker():
    global submissionschannels
    pattern = r'id=(\d+)'
    for info in submissionschannels:
        msgs = []
        try:
            channel = await bot.fetch_channel(info['channelid'])
            logchannel = await bot.fetch_channel(info['logchannel'])
            checkage = await fetchmessages({"fetchtype":1, "channel":info["channelid"], "customfeature": 1, "fetchobject": 6969})
            if checkage["code"] == 404 and checkage["objectcode"] == 0:
                pass
            else:
                for x in checkage['message']['usermessages']:
                    if x["code"] == 404 and x['objectcode'] == 0:
                        msg = await channel.send(f"<@{x['userid']}>, '{x['message']}' is not a valid submission! Please provide a valid steam workshop link!")
                        msgs.append(msg.id)
                        await x['rawmessage'].delete()
                    elif x["code"] == 404 and x['objectcode'] == 1:
                        msg = await channel.send(f"<@{x['userid']}> Your submission has several of the same links. so i did not process it.")
                        msgs.append(msg.id)
                        await x['rawmessage'].delete()
                    elif x['code'] == 200:
                        id = re.findall(pattern, x['message'])
                        req = requests.get(f"https://api.zworpshop.com/levels/workshop/{id[0]}?IncludeReplaced=true")
                        if req.status_code == 404:
                            await x["rawmessage"].add_reaction("❌")
                            msg = await x['rawmessage'].reply(f":warning: I could not find the level. The playlist creator will have to manually add this level! :warning:")
                            msgs.append(msg.id)
                            await logchannel.send(f"i could not find a submission where this was linked: {x['message']}\nThis is either an invalid level or a level i could not find!")
                        elif req.status_code == 200:
                            lvl = json.loads(req.text)
                            if len(lvl) > 1:
                                await x["rawmessage"].add_reaction("❌")
                                msg = await x['rawmessage'].reply(f":warning: This submission has several levels in it! Please stop using level packs and upload all levels separately! :warning:")
                                msgs.append(msg.id)
                            else:
                                if not checkduplicate(info["levels"], lvl[0]['workshopId']):
                                    addlvl({"wsid": lvl[0]['workshopId'], "lvlname": lvl[0]['name'], "lvluid": lvl[0]['fileUid'], "lvlatn": lvl[0]['fileAuthor']}, channelid=info['channelid'])
                                    updatesubchannels()
                                    await x["rawmessage"].add_reaction("✅")
                                    msg = await x['rawmessage'].reply(f"Level '{lvl[0]['name']}' added!")
                                    msgs.append(msg.id)
                                else:
                                    await x["rawmessage"].add_reaction("❌")
                                    msg = await x['rawmessage'].reply(":warning: this level is already submitted! :warning:")
                                    msgs.append(msg.id)
                    else:
                        await x['rawmessage'].reply(f":warning: Something really wrong happened! :warning:")
                if len(msgs) > 0:
                    await lastmsgsaction(type=2, chan=channel.id, msgs=msgs)
                    await lastmsgsaction(type=1, chan=channel.id, msgs=msgs)
        except Exception as ewwor:
            if isinstance(ewwor, TypeError):
               pass
            else:
                await logchannel.send(f"{fwogutils.errormessage(ewwor)}")
                log(str(ewwor))


@bot.slash_command(name="create")
async def create(ctx):
    pass


@create.subcommand(name="submission")
async def subm(ctx):
    pass


@subm.subcommand(name="channel")
async def subchannel(ctx, submissionschannel: nextcord.TextChannel, logchannel: nextcord.TextChannel):
    global submissionschannels
    log(f"called by: {ctx.user} for submissionschannel: {submissionschannel.name} ({submissionschannel.id}), with logchannel: {logchannel.name} ({logchannel.id})")
    if ctx.user.id in [bot.owner_id, ctx.guild.owner_id]:
        with open("data.json", 'r') as f:
            data = json.load(f)
        with open("data.json", 'w') as ft:
            data["submission-channels"].append({"guildid": ctx.guild.id, "channelid": submissionschannel.id, "logchannel": logchannel.id, "lastsentmsgs": [], "levels": []})
            json.dump(data, ft, indent=2)
        await submissionschannel.send("This channel has been set as a submissions channel! all levels that are sent in here will now be automatically moderated")
        updatesubchannels()
        await ctx.send(f"Submissions channel set to: <#{submissionschannel.id}>")
    else:
        await ctx.send("You do not have the permission to use this.", ephemeral=True)


@bot.slash_command(name="get")
async def get(ctx):
    pass


def create_filepl(name: str):
    playlist = {
    "name": name,
    "amountOfLevels": 0,
    "roundLength": 480.0,
    "shufflePlaylist": False,
    "UID": [],
    "levels": []
    }
    with open("playlist.zeeplist", "w") as file:
        json.dump(playlist, file, indent=2)


def add_levels(lvl: list):
    with open("playlist.zeeplist", "r") as file:
        playlist = json.load(file)
    lvls = []
    if len(lvl) > 1:
        for x in lvl:
            code = requests.get(f"https://api.zworpshop.com/levels/uid/{x['lvluid']}?IncludeReplaced=false&IncludeDeleted=false").status_code
            if code == 200:
                lvls.append(
                    {
                        "UID": x["lvluid"],
                        "WorkshopID": x["wsid"],
                        "Name": x["lvlname"],
                        "Author": x["lvlatn"]
                    }
                )
            elif code == 404:
                txt = json.loads(requests.get(f"https://api.zworpshop.com/levels/workshop/{x['wsid']}?IncludeReplaced=false&IncludeDeleted=false").text)[0]
                lvls.append(
                    {
                        "UID": txt["fileUid"],
                        "WorkshopID": txt["workshopId"],
                        "Name": txt["name"],
                        "Author": txt["fileAuthor"]
                    }
                )
        playlist["levels"] = lvls
        with open("playlist.zeeplist", "w") as file:
            json.dump(playlist, file, indent=2)
    else:
        return False


@get.subcommand(name="playlist")
async def getpl(ctx, playlistname: str, channel: nextcord.TextChannel):
    log(f"called by: {ctx.user} for channel: {channel.name} ({channel.id}) as playlistname: {playlistname}")
    ctx = await ctx.send("processing")
    if ctx.user.id in [bot.owner_id, ctx.guild.owner_id]:
        for x in submissionschannels:
            if x['channelid'] == channel.id:
                create_filepl(playlistname)
                if add_levels(x['levels']) is not False:
                    os.rename("playlist.zeeplist", f"{playlistname}.zeeplist")
                    await ctx.edit("The playlist has been generated."
                                   " To import the playlist into the host controls simply drag the file below into this specific directory: `%userprofile%\AppData\Roaming\Zeepkist\Playlists`."
                                   " to easily access this directory: (for windows only) press Win+R and paste the directory in the text box.", file=nextcord.File(f'{playlistname}.zeeplist'))
                    os.rename(f"{playlistname}.zeeplist", "playlist.zeeplist")
                    clearlevels(channel.id)
                    updatesubchannels()
                    return
                else:
                    await ctx.edit("The playlist you requested is either empty or only has 1 level. so i did not make it.")
                    return
        await ctx.send("The mentioned channel is not a submissions channel.")
    else:
        await ctx.send("You do not have the permission to use this.", ephemeral=True)


@bot.slash_command(name="remove")
async def dell(ctx):
    pass


@dell.subcommand(name="submission")
async def delsub(ctx):
    pass


@delsub.subcommand(name="channel")
async def delsubchannel(ctx, channel: nextcord.TextChannel):
    log(f"called by: {ctx.user} for channel: {channel.name} ({channel.id})")
    if ctx.user.id in [ctx.guild.owner_id, bot.owner_id]:
        with open("data.json", 'r') as f:
            data = json.load(f)
            for x in data["submission-channels"]:
                if x['channelid'] == channel.id:
                    with open("data.json", 'w') as ft:
                        data["submission-channels"].remove(x)
                        json.dump(data, ft, indent=2)
                        await ctx.send(f"<#{channel.id}> Is not a submission channel anymore.")
                        updatesubchannels()
                    return
            await ctx.send(f"<#{channel.id}> Is not a submission channel. Please select a submissions channel!")
    else:
        await ctx.send("You do not have the required permissions to use this.")


async def fetchmessages(data: dict):
    try:
        channel = bot.get_channel(data["channel"])
        patterna = r'https://steamcommunity\.com/sharedfiles/filedetails/\?id=\d+'
        messages = []
        if data["fetchtype"] == 1 and data["customfeature"] == 0:
            log(f"fetching message with id {data['fetchobject']}")
            async for message in channel.history(limit=6969, oldest_first=False):
                log(message.id)
                if re.findall(patterna, message.content):
                    messages.append(message.content)
                if message.id == data["fetchobject"]:
                    if re.findall(patterna, message.content):
                        messages.append(message.content)
                    await data["fromctx"].send(messages)
        elif data["fetchtype"] == 2 and data["customfeature"] == 0:
            log(f"fetching {data['fetchobject']} messages")
            async for message in channel.history(limit=int(data["fetchobject"]), oldest_first=True):
                messages.append(message.content)
            await data["fromctx"].send(messages)
            log(f"messages: {messages}")
        elif data["fetchtype"] == 1 and data["customfeature"] == 1:
            async for message in channel.history(limit=6969, oldest_first=False):
                if message.author.id in [bot.user.id]:
                    if len(messages) == 0:
                        return {"code": 404, "objectcode": 0}
                    else:
                        messages.reverse()
                        return {"code": 200, "message": {'usermessages': messages}, "objectcode": 1}
                if re.findall(patterna, message.content):
                    urls = re.findall(patterna, message.content)
                    if len(urls) > 1:
                        duplicheck = checkduplicate(urls)
                        if duplicheck:
                            messages.append({'code': 404, "objectcode":1, 'userid': message.author.id, "message": message.content, 'rawmessage': message})
                        else:
                            for l in urls:
                                messages.append({'code': 200, 'userid': message.author.id, "message": l, 'rawmessage': message})
                    else:
                        messages.append({'code': 200, 'userid': message.author.id, "message": urls[0], 'rawmessage': message})
                else:
                    if message.author.id == message.guild.owner_id:
                        pass
                    else:
                        messages.append({'code': 404, "objectcode": 0, 'userid': message.author.id, "message": message.content, 'rawmessage': message})
    except Exception as ewwor:
        await channel.send(fwogutils.errormessage(ewwor))
        log(str(ewwor))

emb = nextcord.InteractionResponse
page = {"page": 1, "limit": 10, "offset": 0}


@bot.slash_command(name="rankings")
async def rankings(ctx):
    global emb, page
    log(f"called by: {ctx.user}")
    page = {"page": 1, "limit": 10, "offset": 0}
    class Lbpage(nextcord.ui.View):
        def __init__(self):
            super().__init__(timeout=30)
            self.page = page

        @nextcord.ui.button(label="<", style=nextcord.ButtonStyle.blurple)
        async def left(self, ctx: nextcord.Interaction, button: nextcord.Button):
            if self.page['page'] > 1:
                self.page['limit'] -= 10
                self.page['offset'] -= 10
                self.page['page'] -= 1
                lb = json.loads(requests.get(f"https://api.zeepkist-gtr.com/users/rankings?Limit={self.page['limit']}&Offset={self.page['offset']}").text)
                embed = discord.Embed(title="GTR Rankings", color=nextcord.Color.purple(), timestamp=datetime.datetime.now())
                embed = discord.Embed.set_footer(self=embed, text=f"page: {page['page']}, Total amount: {lb['totalAmount']}")
                for x in lb["rankings"]:
                    embed.add_field(name=f"{x['position']}. {x['user']['steamName']}", inline=False,
                                    value=f"World Records: {x['amountOfWorldRecords']}\nScore: {x['score']}")
                await emb.edit(embed=embed, view=Lbpage())

        @nextcord.ui.button(label=">", style=nextcord.ButtonStyle.blurple)
        async def right(self, ctx: nextcord.Interaction, button: nextcord.Button):
            self.page['limit'] += 10
            self.page['offset'] += 10
            self.page['page'] += 1
            lb = json.loads(requests.get(f"https://api.zeepkist-gtr.com/users/rankings?Limit={self.page['limit']}&Offset={self.page['offset']}").text)
            embed = discord.Embed(title="GTR Rankings", color=nextcord.Color.purple(), timestamp=datetime.datetime.now())
            embed = discord.Embed.set_footer(self=embed, text=f"page: {page['page']}, Total amount: {lb['totalAmount']}")
            for x in lb["rankings"]:
                embed.add_field(name=f"{x['position']}. {x['user']['steamName']}", inline=False,
                                value=f"World Records: {x['amountOfWorldRecords']}\nScore: {x['score']}")
            await emb.edit(embed=embed, view=Lbpage())

    lbb = json.loads(requests.get("https://api.zeepkist-gtr.com/users/rankings?Limit=10&Offset=0").text)
    embedd = discord.Embed(title="GTR Rankings", color=nextcord.Color.purple(), timestamp=datetime.datetime.now())
    embedd = discord.Embed.set_footer(self=embedd, text=f"page: {page['page']}, Total amount: {lbb['totalAmount']}")
    for x in lbb["rankings"]:
        embedd.add_field(name=f"{x['position']}. {x['user']['steamName']}", inline=False,
                        value=f"World Records: {x['amountOfWorldRecords']}\nScore: {x['score']}")
    emb = await ctx.send(embed=embedd, view=Lbpage())


@bot.slash_command(name="combine")
async def comb(ctx):
    pass


@comb.subcommand(name="playlists", description="Combine two playlists together!")
async def combpl(ctx, pla: nextcord.Attachment = nextcord.SlashOption(name="playlist", description="The Playlist you want to combine", required=True),
                 plb: nextcord.Attachment = nextcord.SlashOption(name="to_playlist", description="The Playlist you want to combine to", required=True),
                 name: str = nextcord.SlashOption(description="The name you want the combined playlist to be named", required=True)):
    log(f"called by user: {ctx.user} ({ctx.user.id}) with plname: {name}")
    try:
        if pla.filename.split(".")[1:][0] and plb.filename.split(".")[1:][0] == "zeeplist":
            plbr = json.loads(await plb.read())
            for a in json.loads(await pla.read())["levels"]:
                plbr["levels"].append(a)
            plbr["name"] = name
            plbr["amountOfLevels"] = len(plbr["levels"])
            with open("playlist.zeeplist", 'w') as f:
                json.dump(plbr, f, indent=2)
            os.rename("playlist.zeeplist", f"{name}.zeeplist")
            await ctx.send("The playlist has been generated."
                           " To import the playlist into the host controls simply drag the file below into this specific directory: `%userprofile%\AppData\Roaming\Zeepkist\Playlists`."
                           " to easily access this directory: (for windows only) press Win+R and paste the directory in the text box.",
                           file=nextcord.File(f'{name}.zeeplist'))
            os.rename(f"{name}.zeeplist", "playlist.zeeplist")
        else:
            await ctx.send(f"please attach a valid .zeeplist file")
    except Exception as ewwor:
        log(str(ewwor))
        await ctx.user(fwogutils.errormessage(ewwor))


@bot.slash_command(name="update")
async def upd(ctx):
    pass


@upd.subcommand(name="playlist", description="Update outdated levels in a playlist!")
async def updpl(ctx, playlist: nextcord.Attachment=nextcord.SlashOption(description="Update this playlist to newer levels!", required=True),
                removeduplicates: bool=nextcord.SlashOption(description="Removes duplicates if there are any.", required=True)):
    log(f"reached by {ctx.user} ({ctx.user.id}) with playlist name: {playlist.filename}")
    if playlist.filename.split(".")[1:][0] == "zeeplist":
        ctx = await ctx.send("processing")
        pllvls = json.loads(await playlist.read())
        pllvlsupd = {"name": f"{pllvls['name']}",
                     "amountOfLevels": pllvls["amountOfLevels"],
                     "roundLength": pllvls["roundLength"],
                     "shufflePlaylist": bool(pllvls["shufflePlaylist"]),
                     "UID": [],
                     "levels": []}
        data = {'updlvls': 0, 'updlvlsnames': "", 'dellvls': 0, 'dellvlsnames': "", 'nflvls': 0, 'nflvlsnames': "",
                'duplilvls': 0, 'duplilvlsnames': "", 'duplicheck': []}
        try:
            for x in pllvls["levels"]:
                s = x['UID']
                code = requests.get(f"https://api.zworpshop.com/levels/uid/{urllib.parse.quote_plus(s, encoding='UTF-8')}").status_code
                if code == 404:
                    req = requests.get(f"https://api.zworpshop.com/levels/workshop/{x['WorkshopID']}?IncludeReplaced=false&IncludeDeleted=false")
                    if req.status_code == 200:
                        reqtxt = json.loads(req.text)
                        if len(reqtxt) == 1:
                            log("len reach 1")
                            if x['WorkshopID'] in data['duplicheck'] and removeduplicates is True:
                                data['duplilvls'] += 1
                                data['duplilvlsnames'] += f"> - {x['Name']}\n"
                            else:
                                pllvlsupd["levels"].append({"UID": f"{reqtxt[0]['fileUid']}", "WorkshopID": int(reqtxt[0]['workshopId']),
                                                            "Name": f"{reqtxt[0]['name']}", "Author": f"{reqtxt[0]['fileAuthor']}"})
                                data['duplicheck'].append(x['WorkshopID'])
                            data['updlvls'] += 1
                            data['updlvlsnames'] += f"> - {x['Name']}\n"
                        elif len(reqtxt) > 1:
                            log("len reach bigger than 1")
                            data['nflvls'] += 1
                            data['nflvlsnames'] += f"> - {x['Name']}\n"
                    elif req.status_code == 404:
                        log("req 404")
                        data['dellvls'] += 1
                        data['dellvlsnames'] += f"> - {x['Name']}\n"
                elif code == 200:
                    if x['WorkshopID'] in data['duplicheck'] and removeduplicates is True:
                        data['duplilvls'] += 1
                        data['duplilvlsnames'] += f"> - {x['Name']}\n"
                    else:
                        pllvlsupd["levels"].append(x)
                        data['duplicheck'].append(x['WorkshopID'])
            name = playlist.filename.split(".")[:1][0]
            with open("playlist.zeeplist", 'w') as f:
                json.dump(pllvlsupd, f, indent=2)
            os.rename("playlist.zeeplist", f"{name}.zeeplist")
            await ctx.edit(f"## {data['updlvls']} level(s) were updated.\n> ### Updated level(s):\n{data['updlvlsnames']}\n"
                           f"## {data['dellvls']} level(s) were deleted from the workshop. (These can manually be added!)\n> ### Deleted level(s):\n{data['dellvlsnames']}\n"
                           f"## {data['nflvls']} level(s) were not found. (These can manually be added!)\n> ### Not Found level(s):\n{data['nflvlsnames']}\n"
                           f"## {data['duplilvls']} level(s) were duplicated.\n> ### Duplicated level(s):\n{data['duplilvlsnames']}",
                           file=nextcord.File(f"{name}.zeeplist"))
            os.rename(f"{name}.zeeplist", "playlist.zeeplist")
        except Exception as ewwor:
            await ctx.edit(fwogutils.errormessage(ewwor))
            log(ewwor)
    else:
        await ctx.send("Please attach a valid .zeeplist file.")


@bot.slash_command(name="reverse")
async def rev(ctx):
    pass


@rev.subcommand(name="playlist", description="Reverse a playlist!")
async def revpl(ctx, playlist: nextcord.Attachment=nextcord.SlashOption(description="The playlist to reverse.", required=True)):
    log(f"reached by {ctx.user} ({ctx.user.id}) with playlist name: {playlist.filename}")
    if playlist.filename.split(".")[1:][0] == "zeeplist":
        ctx = await ctx.send("processing")
        pl = json.loads(await playlist.read())
        pl['levels'].reverse()
        name = playlist.filename.split(".")[:1][0]
        with open("playlist.zeeplist", 'w') as f:
            json.dump(pl, f, indent=2)
        os.rename("playlist.zeeplist", f"{name}.zeeplist")
        await ctx.edit("Your playlist has been reversed!", file=nextcord.File(f"{name}.zeeplist"))
        os.rename(f"{name}.zeeplist", "playlist.zeeplist")
    else:
        await ctx.send("Please attach a valid .zeeplist file!")

@bot.slash_command(name="shuffle")
async def shuf(ctx):
    pass

@shuf.subcommand(name="playlist", description="Shuffle a playlist!")
async def shufpl(ctx, playlist: nextcord.Attachment=nextcord.SlashOption(description="The playlist to Shuffle.", required=True)):
    log(f"reached by {ctx.user} ({ctx.user.id})")
    if fwogutils.checkzeeplist(playlist.filename):
        ctx = await ctx.send("processing")
        pl = json.loads(await playlist.read())
        random.shuffle(pl['levels'])
        fwogutils.dumppl(pl)
        name = playlist.filename.split(".")[:1][0]
        fwogutils.renamepl(name)
        await ctx.edit("Your playlist has been shuffled!", file=nextcord.File(f"{name}.zeeplist"))
        fwogutils.undorename(name)
    else:
        await ctx.send("Please attach a valid .zeeplist file!")

@get.subcommand(name="top")
async def gettop(ctx):
    pass

@gettop.subcommand(name="levels", description="Get a playlist from levels worth the most points in GTR!")
async def gettoplvls(ctx, amount: int=nextcord.SlashOption(description="Amount of levels to have in the playlist! (Maximum 999)"), playlistname: str=nextcord.SlashOption(description="The name of the playlist!")):
    log(f"reached by {ctx.user} ({ctx.user.id})")
    ctx = await ctx.send("processing (this might take a while)")
    toplvls = fwogutils.jsonapi_get_toplevelpoints(limit=amount)
    if toplvls is not False:
        sepplevels = fwogutils.converturlsepperations(toplvls)
        levelhashes = fwogutils.zworp_getlevelsbyhashlist(sepplevels)
        levels = []
        for x in toplvls:
            try:
                levels.append(levelhashes[x])
            except KeyError as notfound:
                log(f"did not find level: {notfound}")
        fwogutils.dumppl({
            "name": playlistname,
            "amountOfLevels": len(levels),
            "roundLength": 480.0,
            "shufflePlaylist": False,
            "UID": [],
            "levels": levels
        })
        fwogutils.renamepl(playlistname)
        await ctx.edit(f"Your playlist has been generated! {len(levels)}/{amount} levels were found!", file=nextcord.File(f"{playlistname}.zeeplist"))
        fwogutils.undorename(playlistname)
    else:
        await ctx.edit("Error! Limit is 999!")


sent = False
conx = nextcord.Interaction
@tasks.loop(seconds=10, reconnect=True)
async def emb():
    global sent, conx
    chan = await bot.fetch_channel(1144730662000136315)
    try:
        this = json.loads(requests.get("https://zeepkist-showdown-4215308f4ce4.herokuapp.com/api/qualifier").text)['qualifier']
        wr = json.loads(requests.get("https://api.zeepkist-gtr.com/records?Level=D94C0982CE0BA4D261DF1A79BF2267B47DFEF715&ValidOnly=true&Limit=1&Offset=0").text)['records'][0]
        wruser = json.loads(requests.get(f"https://api.zeepkist-gtr.com/users/{wr['user']}").text)
        embed = discord.Embed(title="Pool 1", description="", color=nextcord.Color.red())
        embeda = discord.Embed(title="Pool 2", description="", color=nextcord.Color.blue())
        embedb = discord.Embed(title="Substitutes", description="", color=nextcord.Color.dark_grey())
        wrembed = discord.Embed(title="GTR World Record", description="", color=nextcord.Color.purple())
        count = 1
        for x in this[:8]:
            embed.add_field(name=f"{count}. {x['time']}", value=f"by {x['name']}")
            count += 1
        embed.add_field(name=f"", value=f"")
        for x in this[:16][8:]:
            embeda.add_field(name=f"{count}. {x['time']}", value=f"by {x['name']}")
            count += 1
        embeda.add_field(name=f"", value=f"")
        for x in this[16:41]:
            embedb.add_field(name=f"{count}. {x['time']}", value=f"by {x['name']}")
            count += 1
        wrembed.add_field(name=f"{format_time(wr['time'])}", value=f"by {wruser['steamName']}")
        if sent:
            await conx.edit(f"# Showdown Qualifier Season 2", embeds=[embed, embeda, embedb, wrembed])
        else:
            conx = await chan.send(f"# Showdown Qualifier Season 2", embeds=[embed, embeda, embedb, wrembed])
            sent = True
    except Exception as ewwor:
        await chan.send(f"an error occurred.\n\n```{ewwor}```")


@bot.command(name="startemb")
async def startemb(ctx):
    if ctx.author.id in [785037540155195424, 257321046611329026]:
        emb.start()
    else:
        pass


@bot.command(name="stopemb")
async def stopemb(ctx):
    global sent
    if ctx.author.id in [785037540155195424, 257321046611329026]:
        emb.stop()
        sent = False
    else:
        pass


@bot.slash_command(name='crtteam', guild_ids=[1127321762686836798])
async def crtteam(ctx, teamname: str, teamtag: str, pa: str, pb: str, color: str):
    color = fwogutils.hex_to_rgb(color)
    embed = discord.Embed(title=f"[{teamtag}] {teamname}", description=f"{pa}\n{pb}",
                          color=nextcord.Color.from_rgb(color[0], color[1], color[2]))
    await ctx.send(embed=embed)


@bot.command(name='sendteams')
async def sendteams(ctx):
    teams = json.loads(requests.get("https://zeepkist-showdown-4215308f4ce4.herokuapp.com/api/test/teams").text)
    embeds = []
    for x in teams['teams']:
        color = fwogutils.hex_to_rgb(x['color'][1:69])
        embeds.append(discord.Embed(title=f'[{x["tag"]}] {x["name"][:247]}',
                                    description=f"{x['participants'][0]['steamName']}\n{x['participants'][1]['steamName']}",
                                    color=nextcord.Color.from_rgb(color[0], color[1], color[2])))
    await ctx.send(embeds=embeds)


sentlb = False
conxlb = nextcord.Interaction
@tasks.loop(minutes=5, reconnect=True)
async def lb():
    global sentlb, conxlb, cache
    sdlvls = [{'hash': "6CCAB651EC9FD760D1BE0E71C453290C2A2CD16D", 'name': "Abyssal Windows"},
              {'hash': "2D9CDA53B58EA5FB3E4D62F9DB1A60DE3DB201A1", 'name': "Crystal Sands"},
              {'hash': "FE488367F99D07F1D795381E6726C5603495EF6F", 'name': "OOoOoooOooOOOO stairs"},
              {'hash': "05BD3B69BD469BC9DC24DC89C1E7929445E46D0C", 'name': "Other Green Hills"},
              {'hash': "29036E8F39B3682BA1576F4268C9BBA278D88C21", 'name': "Schmetterling"},
              {'hash': "544EF863C7740AEB32D708EE269C3C5D03FF8E9A", 'name': "The Red One"},
              {'hash': "11ED3D54B27698564A6499B6FEEE996B1D13CE0B", 'name': "Whirlpool"}]
    chan = await bot.fetch_channel(1198606669123424357)
    embed = discord.Embed(title="Showdown Levels", description=" ", color=nextcord.Color.purple())
    embeda = discord.Embed(color=nextcord.Color.purple(), description=" ")
    embedb = discord.Embed(color=nextcord.Color.purple(), description=" ")
    embedc = discord.Embed(color=nextcord.Color.purple(), description=" ", timestamp=datetime.datetime.now())
    embedc.set_footer(text="last updated")
    try:
        for x in sdlvls:
            records = json.loads(requests.get(f"https://api.zeepkist-gtr.com/records?Level={x['hash']}&ValidOnly=true&Limit=75&Offset=0").text)
            data = {"levelrecs": "", "rcount": 0, "users": []}
            for a in records['records']:
                user = fwogutils.getgtruser(id=a['user'])[1]['steamName']
                if user not in data['users']:
                    data['levelrecs'] += f"1. `{format_time(a['time'])}` by **{user}**\n"
                    data['users'].append(user)
                    data['rcount'] += 1
                    if data["rcount"] == 5:
                        break
            if x['name'] in ['Abyssal Windows', 'Crystal Sands']:
                embed.add_field(name=x['name'], value=data['levelrecs'], inline=True)
            elif x['name'] in ['OOoOoooOooOOOO stairs', 'Other Green Hills']:
                embeda.add_field(name=x['name'], value=data['levelrecs'], inline=True)
            elif x['name'] in ['Schmetterling', 'The Red One']:
                embedb.add_field(name=x['name'], value=data['levelrecs'], inline=True)
            elif x['name'] in ['Whirlpool']:
                embedc.add_field(name=x['name'], value=data['levelrecs'], inline=True)
        if sentlb is not True:
            embedc.timestamp = datetime.datetime.now()
            conxlb = await chan.send(embeds=[embed, embeda, embedb, embedc])
            sentlb = True
        else:
            embedc.timestamp = datetime.datetime.now()
            await conxlb.edit(embeds=[embed, embeda, embedb, embedc])
    except Exception as ewwor:
        log(str(ewwor))


@bot.command(name="startlb")
async def startemb(ctx):
    if ctx.author.id in [785037540155195424, 257321046611329026]:
        lb.start()
    else:
        pass


@bot.command(name="stoplb")
async def stopemb(ctx):
    global sentlb
    if ctx.author.id in [785037540155195424, 257321046611329026]:
        lb.stop()
        sentlb = False
    else:
        pass

@bot.slash_command(name="verify", description="Verify that you are not a bot!", guild_ids=[1200812715527114824])
async def verify(ctx):
    log(f"called by user: {ctx.user} ({ctx.user.id})")
    if ctx.guild.get_role(1201928108769554442) not in ctx.user.roles:
        gtrcheck = fwogutils.getgtruser(discid=ctx.user.id)
        if gtrcheck[0]:
            log(f"gtrcheck index 0 returned true")
            class YesOrNoButtons(nextcord.ui.View):
                @nextcord.ui.button(label="Yes", style=nextcord.ButtonStyle.green)
                async def yes(self, button: nextcord.Button, ctx: nextcord.Interaction):
                    try:
                        self.stop()
                        fwogutils.addgtruser(str(ctx.user.id), gtrcheck[1])
                        await ctx.user.add_roles(ctx.guild.get_role(1201928108769554442))
                        log(f"verified user {ctx.user} ({ctx.user.id}), also accepted to link their GTR :3")
                        await ctx.send("You have been verified!", ephemeral=True)
                    except Exception as ewwor:
                        await ctx.send(fwogutils.errormessage(ewwor), ephemeral=True)

                @nextcord.ui.button(label="No", style=nextcord.ButtonStyle.red)
                async def no(self, button: nextcord.Button, ctx: nextcord.Interaction):
                    self.stop()
                    await ctx.user.add_roles(ctx.guild.get_role(1201928108769554442))
                    log(f"verified user {ctx.user} ({ctx.user.id}) without linkage to GTR")
                    await ctx.send("You have been verified!", ephemeral=True)

            await ctx.send(f"Hello there! i have detected that you have a GTR account by the name of **{gtrcheck[1]['steamName']}**,"
                           f" do you wish to link it to this discord? this will only be used in this discord.",
                           view=YesOrNoButtons(), ephemeral=True)
        else:
            await ctx.user.add_roles(ctx.guild.get_role(1201928108769554442))
            log(f"verified user {ctx.user} ({ctx.user.id})")
            await ctx.send("you have been verified!", ephemeral=True)
    else:
        await ctx.send("you are already verified!", ephemeral=True)

class Cog(commands.Cog):
    @commands.Cog.listener()
    async def on_message(self, ctx):
        if ctx.channel.id == 1201928657703292959 and ctx.author.id not in [785037540155195424, bot.user.id]:
            await ctx.delete()
bot.add_cog(Cog())

@bot.slash_command(name="link", guild_ids=[1200812715527114824])
async def link(ctx):
    pass

@link.subcommand(name="gtr", description="Link your GTR to this server!")
async def linkgtr(ctx):
    log(f"reached by {ctx.user} ({ctx.user.id})")
    gtrcheck = fwogutils.getgtruser(discid=ctx.user.id)
    if gtrcheck[0]:
        log(f"gtrcheck index 0 returned true")

        class YesOrNoButtons(nextcord.ui.View):
            @nextcord.ui.button(label="Yes", style=nextcord.ButtonStyle.green)
            async def yes(self, button: nextcord.Button, ctx: nextcord.Interaction):
                try:
                    self.stop()
                    fwogutils.addgtruser(str(ctx.user.id), gtrcheck[1])
                    await ctx.send("You have been linked!", ephemeral=True)
                except Exception as ewwor:
                    await ctx.send(fwogutils.errormessage(ewwor), ephemeral=True)

            @nextcord.ui.button(label="Cancel", style=nextcord.ButtonStyle.red)
            async def no(self, button: nextcord.Button, ctx: nextcord.Interaction):
                self.stop()
                await ctx.send("cancelled!", ephemeral=True)

        await ctx.send(f"i have detected a GTR account by the name of **{gtrcheck[1]['steamName']}**, do you wish to link it?",
                       view=YesOrNoButtons(), ephemeral=True)
    else:
        await ctx.send("I did not find any discord linkage, Please link your discord to your GTR by reproducing the following steps in-game:\n`Settings -> Mods -> Scroll to GTR -> In the 'discord' section, Press 'Link'`",
                       ephemeral=True)

async def rankingsfunc(gtrrankings):
    global leaderboards
    leaderboard = await bot.get_channel(1203645881279184948).fetch_message(leaderboards['rankings'])
    stringedrankings = ""
    for x in gtrrankings["rankings"][:20]:
        stringedrankings += f"{x['position']}. `{x['user']['steamName']}` with **{x['score']}** points and **{x['amountOfWorldRecords']}** World Records\n"
    embed = discord.Embed(title="GTR Rankings", description=stringedrankings, color=nextcord.Color.blue(),
                          timestamp=datetime.datetime.now())
    embed.set_footer(text="last updated")
    await leaderboard.edit(embed=embed, view=fwogutils.views.LButtons(gtrrankings))
    ruusies = fwogutils.getRUusers()
    linkeds = fwogutils.get_linked_users()
    for x in ruusies:
        checkrank = fwogutils.getlinkeduserdata(x)["position"]
        userrank = fwogutils.jsonapi_get_playerrank(linkeds[x]["id"])
        if checkrank > userrank:
            log(f"{x} ranked up!! sending notif!")
            channel = await bot.fetch_channel(1207401802769633310)
            embed = discord.Embed(title="Ranked up!", description=f"You have ranked up to position **{userrank}** in the GTR rankings!!", color=nextcord.Color.blue())
            embed.set_thumbnail(url="https://cdn.discordapp.com/attachments/1066387605253525595/1202663511252013066/Projet_20240201061441.png?ex=65ce46ad&is=65bbd1ad&hm=42cf06915022254aee2647a53d62d3814c8397d034e8232381c4d6b7e95d299e&")
            await channel.send(f"<@{int(x)}>", embed=embed)
            fwogutils.setlinkedranking(user=x, pos=userrank)
    rdusies = fwogutils.getRDusers()
    for x in rdusies:
        checkrank = fwogutils.getlinkeduserdata(x)["position"]
        userrank = fwogutils.jsonapi_get_playerrank(linkeds[x]["id"])
        if checkrank < userrank:
            log(f"{x} ranked down :/ sending notif!")
            channel = await bot.fetch_channel(1207401802769633310)
            embed = discord.Embed(title="Ranked down :/", description=f"You have ranked down to position **{userrank}** in the GTR rankings :/", color=nextcord.Color.blue())
            embed.set_thumbnail(url="https://cdn.discordapp.com/attachments/1066387605253525595/1202663511252013066/Projet_20240201061441.png?ex=65ce46ad&is=65bbd1ad&hm=42cf06915022254aee2647a53d62d3814c8397d034e8232381c4d6b7e95d299e&")
            await channel.send(f"<@{int(x)}>", embed=embed)
            fwogutils.setlinkedranking(user=x, pos=userrank)


@tasks.loop(time=fwogutils.all_24hours(), reconnect=True)
async def rankings():
    gtrrankings = fwogutils.getgtruserrankings(limit=100, offset=0)
    await rankingsfunc(gtrrankings=gtrrankings)

rankings.start()

@bot.slash_command(name="notif", guild_ids=[1200812715527114824])
async def notif(ctx):
    pass

@notif.subcommand(name="add", description="will notify you for what you select!")
async def notifme(ctx, to: str=nextcord.SlashOption(name="for", description="will notify you for what you select!", choices={"GTR Rank up": "RU", "GTR Rank down": "RD", "World Record stolen": "WRST"})):
    log(f"reached by {ctx.user} ({ctx.user.id})")
    try:
        if fwogutils.userislinked(ctx.user.id):
            log("user is linked")
            usersettings = fwogutils.getlinkedusersettings(ctx.user.id)
            if usersettings["notifs"][to] is True:
                await ctx.send("You already enabled this notification!")
                log("setting already enabled, returning")
                return
            log(f"setting {to} to True")
            fwogutils.setlinkedusersetting(setting=to, value=True, user=ctx.user.id)
            if to == "WRST":
                log("setting user wrs for WRST notif")
                user = fwogutils.get_linked_users()[str(ctx.user.id)]
                allwrs = fwogutils.gtr_getalluserwrs(user['id'])
                fwogutils.loc_setuserwrs(user['id'], allwrs)
            await ctx.send(f"You will now be notified for what you selected!")
        else:
            await ctx.send("You are not linked! use the `/link gtr` command to link your GTR to this server!")
    except Exception as ewwor:
        await ctx.send(fwogutils.errormessage(ewwor))
        log(str(ewwor))

@notif.subcommand(name="remove", description="will stop notifying you for what you select!")
async def notifme(ctx, to: str=nextcord.SlashOption(name="for", description="will stop notifying you for what you select!", choices={"GTR Rank up": "RU", "GTR Rank down": "RD", "World Record stolen": "WRST"})):
    log(f"reached by {ctx.user} ({ctx.user.id})")
    try:
        if fwogutils.userislinked(ctx.user.id):
            log("user is linked")
            usersettings = fwogutils.getlinkedusersettings(ctx.user.id)
            if usersettings["notifs"][to] is False:
                await ctx.send("This was already disabled!")
                log("setting already disabled, returning")
                return
            log(f"setting {to} to False")
            fwogutils.setlinkedusersetting(setting=to, value=False, user=ctx.user.id)
            user = fwogutils.get_linked_users()[str(ctx.user.id)]
            fwogutils.loc_setuserwrs(user['id'], ["user opt-out"])
            await ctx.send(f"We will stop to notify you for what you selected!")
        else:
            await ctx.send("You are not linked! use the `/link gtr` command to link your GTR to this server!")
    except Exception as ewwor:
        await ctx.send(fwogutils.errormessage(ewwor))
        log(str(ewwor))

async def listen_forever():
    try:
        async with websockets.connect("wss://stream.zeepkist-gtr.com/ws") as websocket:
            websocket.recv = await wrcallback(websocket, None)
            await listen_forever()
    except Exception as ewwor:
        log(str(ewwor))
        await listen_forever()

async def wrcallback(websocket, message=None):
    content = json.loads(await websocket.recv())
    if str(content['Data']['PreviousUserId']) in fwogutils.getWRSTusers() and content['Data']['PreviousUserId'] != content['Data']['NewUserId'] and content['Type'] == "wr":
        log("WR is stolen!!")
        wrstuserinfo = fwogutils.getWRSTusers()[str(content['Data']['PreviousUserId'])]
        userlink = fwogutils.get_linked_users()[str(wrstuserinfo['discid'])]
        level = fwogutils.zworp_getlevel(content['Data']['LevelHash'])
        if level is not False:
            log("level was not false")
            prevrec = fwogutils.jsonapi_getrecord(content['Data']['PreviousRecordId'])
            recordcreated = datetime.datetime.strptime(prevrec["dateCreated"], '%Y-%m-%dT%H:%M:%S.%fZ')
            timenow = datetime.datetime.now()
            if timenow.date() == recordcreated.date() and int(recordcreated.timestamp())+600 > int(timenow.timestamp()):
                return
            newrec = fwogutils.getgtrrecord(content['Data']['NewRecordId'])
            newuser = fwogutils.getgtruser(content['Data']['NewUserId'])
            wrstembed = discord.Embed(title="One of your World Records has been taken!", description=f"Your World Record on **{level[0]['name']}** by **{level[0]['fileAuthor']}** was taken!",
                                      color=nextcord.Color.blue(), url=f"https://steamcommunity.com/sharedfiles/filedetails/?id={level[0]['workshopId']}")
            wrstembed.set_thumbnail(url="https://cdn.discordapp.com/attachments/1066387605253525595/1202663511252013066/Projet_20240201061441.png?ex=65ce46ad&is=65bbd1ad&hm=42cf06915022254aee2647a53d62d3814c8397d034e8232381c4d6b7e95d299e&")
            wrstembed.add_field(name="Info", value=f"Previous time: **{fwogutils.format_time(prevrec['time'])}** by **{userlink['steamName']}** set <t:{int(recordcreated.timestamp())}:R>\n"
                                                   f"New time: **{fwogutils.format_time(newrec['time'])}** by **{newuser[1]['steamName']}**\n"
                                                   f"Level: [{level[0]['name']} by {level[0]['fileAuthor']}](https://steamcommunity.com/sharedfiles/filedetails/?id={level[0]['workshopId']})")
            notifchannel = await bot.fetch_channel(1207401802769633310)
            await notifchannel.send(f"<@{wrstuserinfo['discid']}>", embed=wrstembed)

@get.subcommand(name="hot")
async def gethot(ctx):
    pass

@gethot.subcommand(name="levels", description="Get a playlist of the levels that have been played the most in the past 24 hours!")
async def gethotlvls(ctx, playlistname: str=nextcord.SlashOption(description="The name for the playlist", required=True)):
    ctx = await ctx.send("processing!")
    hot = GTR.Levels.Hot()
    if hot.status_code != 200:
        await ctx.send(f"Error occured.\n`{hot.status_code}`")
    else:
        hotlvls = hot.levels
        hashlist = []
        for x in hotlvls:
            hashlist.append(x['level'])
        sepplevels = fwogutils.converturlsepperations(hashlist)
        levelhashes = fwogutils.zworp_getlevelsbyhashlist(sepplevels)
        levels = []
        for x in hashlist:
            try:
                levels.append(levelhashes[x])
            except KeyError as notfound:
                log(f"did not find level: {notfound}")
        fwogutils.dumppl({
                "name": playlistname,
                "amountOfLevels": len(levels),
                "roundLength": 480.0,
                "shufflePlaylist": False,
                "UID": [],
                "levels": levels
            })
        fwogutils.renamepl(playlistname)
        await ctx.edit(f"Your playlist has been generated!",
                       file=nextcord.File(f"{playlistname}.zeeplist"))
        fwogutils.undorename(playlistname)



bot.run(privaat.token)