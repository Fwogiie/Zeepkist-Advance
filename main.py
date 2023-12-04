import datetime
import time
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
import fwogutils
from fwogutils import bot as bot
from fwogutils import log as log

bot.load_extension("onami")

ids = []
lvlsamount = 0
gitgud = bool
async def fetch(channelid: int, amount: int, oldest_first: bool, fetched_react: int, messageid: int=0):
    global ids, lvlsamount, gitgud
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

@bot.event
async def on_ready():
    await bot.change_presence(activity=discord.Activity(type=discord.ActivityType.watching, name="For level submissions"))
    for guild in bot.guilds:
        print(f"Connected to guild: {guild.name} ({guild.id}) with {guild.member_count} members.")

@bot.is_owner
@bot.command(name="log")
async def ownlog(ctx, type: str, *, text: str=None):
    if type == "send" and text is None:
        await ctx.reply("yes ma'am", file=nextcord.File("log.txt"))
    elif type == "send" and text == "true":
        with open("log.txt", 'r') as fr:
            await ctx.send(f"```{fr.read()}```")
    elif type == "add":
        log(text)
        await ctx.reply(f"Added `{text}` to log.txt")
    elif type == "clear":
        log("bruh", "clear")
        await ctx.reply("cleared log.txt")
    else:
        await ctx.reply("Yo fucking stupid bruv?")

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
    log(f"msgcmd called by {ctx.user} for msg {msg.content}")
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

def format_time(time: float):
    minutes = int(time // 60)
    seconds = int(time % 60)
    milliseconds = int((time % 1) * 1000)
    formatted_time = f"{minutes:02d}:{seconds:02d}:{milliseconds:03d}"
    return formatted_time

submissionschannels = []
@bot.event
async def on_ready():
    global submissionschannels
    log(f"Loaded up! with bot ID: {bot.user.id}")
    with open("data.json", "r") as f:
        data = json.load(f)
        submissionschannels = data["submission-channels"]
    await submission_checker.start()

def updatesubchannels():
    global submissionschannels
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
                log(ewwor)

@bot.slash_command(name="create")
async def create(ctx):
    pass

@create.subcommand(name="submission")
async def subm(ctx):
    pass

@subm.subcommand(name="channel")
async def subchannel(ctx, submissionschannel: nextcord.TextChannel, logchannel: nextcord.TextChannel):
    global submissionschannels
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
    if ctx.user.id in [bot.owner_id, ctx.guild.owner_id]:
        for x in submissionschannels:
            if x['channelid'] == channel.id:
                create_filepl(playlistname)
                if add_levels(x['levels']) is not False:
                    os.rename("playlist.zeeplist", f"{playlistname}.zeeplist")
                    await ctx.send("The playlist has been generated."
                                   " To import the playlist into the host controls simply drag the file below into this specific directory: `%userprofile%\AppData\Roaming\Zeepkist\Playlists`."
                                   " to easily access this directory: (for windows only) press Win+R and paste the directory in the text box.", file=nextcord.File(f'{playlistname}.zeeplist'))
                    os.rename(f"{playlistname}.zeeplist", "playlist.zeeplist")
                    clearlevels(channel.id)
                    updatesubchannels()
                    return
                else:
                    await ctx.send("The playlist you requested is either empty or only has 1 level. so i did not make it.")
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
        log(ewwor)

emb = nextcord.InteractionResponse
page = {"page": 1, "limit": 10, "offset": 0}
@bot.slash_command(name="rankings")
async def rankings(ctx):
    global emb, page
    page = {"page": 1, "limit": 10, "offset": 0}
    class Lbpage(nextcord.ui.View):
        def __init__(self):
            super().__init__(timeout=30)
            self.page = page
        @nextcord.ui.button(label="🡨", style=nextcord.ButtonStyle.blurple)
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
        @nextcord.ui.button(label="🡪", style=nextcord.ButtonStyle.blurple)
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



bot.run(privaat.token)
