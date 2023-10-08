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
import fwogutils
from fwogutils import bot as bot
from fwogutils import log as log

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
    print(error)
    await ctx.send(f"An error occured. if this persists please report it in the zeepkist modding server: [here](https://discord.gg/a4FxG9RpV3) in this thread: https://discord.com/channels/972933002516647986/1126438917420359691 \n \n Error: `{error}`", ephemeral=True)

@bot.event
async def on_ready():
    await bot.change_presence(activity=discord.Activity(type=discord.ActivityType.watching, name="For level submissions"))
    for guild in bot.guilds:
        print(f"Connected to guild: {guild.name} ({guild.id}) with {guild.member_count} members.")

@bot.is_owner
@bot.command(name="log")
async def ownlog(ctx, type: str, *, text: str=None):
    if type == "send":
        await ctx.reply("yes ma'am", file=nextcord.File("log.txt"))
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


# Zeepkist Advance
async def add_user(discid: int, gtrid: int=0, check: bool=False):
    with open("auth.json", "r") as file:
        authlist = json.load(file)

    if check is True:
        for x in authlist["users"]:
            if discid == x["discordId"]:
                return True

    if check is False:
        new_user = (
            {
                "gtrId": gtrid,
                "discordId": discid,
                "unlockedAC": [],
                "lockedAC": []
            }
        )
        print(new_user)
        authlist["users"].append(new_user)
        with open("auth.json", "w") as file:
            json.dump(authlist, file, indent=2)
        return new_user

class Yes(nextcord.ui.View):
    def __init__(self):
        super().__init__()
        self.value = None
        self.userid = int

    @nextcord.ui.button(label = "Yes", style = nextcord.ButtonStyle.green)
    async def helpb(self, button: nextcord.ui.Button, interaction: nextcord.Interaction):
        if self.userid == interaction.user.id:
            print(gtrids)
            e = await add_user(gtrid=gtrids, discid=interaction.user.id)
            await interaction.response.send_message(f"You have been Added to the system! (debug json: {e})")
            self.stop()
        else:
            await interaction.response.send_message("This button is not for you.", ephemeral=True)

gtrids = int
@bot.slash_command(name="login", description="THIS IS A BETA AND WILL MOST LIKELY FAIL!!!")
async def login(ctx):
    global gtrids
    check = await add_user(discid=ctx.user.id, check=True)
    if check is True:
        await ctx.send("You are already in the system.")
        return
    a = requests.get(f"https://api.zeepkist-gtr.com/users/discord/{ctx.user.id}")
    if a.status_code == 200:
        c = json.loads(a.content)
        gtrids = c["id"]
        view = Yes()
        view.userid = ctx.user.id
        await ctx.send(f"Is [this](https://steamcommunity.com/profiles/{c['steamId']}) your account? if so, please press 'Yes' Below.", view=view)
        await view.wait()
    if a.status_code == 404:
        await ctx.send("I could not find anything linked to your discord, Please make sure you have Zeepkist GTR installed!")

def get_users():
    with open("auth.json", "r") as file:
        return json.load(file)["users"]


def format_time(time: float):
    minutes = int(time // 60)
    seconds = int(time % 60)
    milliseconds = int((time % 1) * 1000)
    formatted_time = f"{minutes:02d}:{seconds:02d}:{milliseconds:03d}"
    return formatted_time

class Lbsend(nextcord.ui.ChannelSelect):
    def __init__(self):
        super().__init__(channel_types=[nextcord.TextChannel])

class lbedit(nextcord.ui.View):
    def __init__(self):
        super().__init__()
        self.add_item(Lbsend())

    @nextcord.ui.button(label="Edit", style=nextcord.ButtonStyle.gray)
    async def helpb(self, button: nextcord.ui.Button, interaction: nextcord.Interaction):
        await interaction.response.send_modal(Crtlb(type=lbtypea))

    @nextcord.ui.button(label="Send", style=nextcord.ButtonStyle.green)
    async def sendlb(self, button: nextcord.ui.Button, interaction: nextcord.Interaction):
        await interaction.response.send_message("Wich channel do you wish this leaderboard to get sent to?")



defvalues = ""
@bot.slash_command(name="create_leaderboard")
async def createlb(ctx, lbtype: str=nextcord.SlashOption(name="leaderboard_type", description="Type of leaderboard you wish to have", choices={"Singular Track": "single", "Multiple Tracks": "multi"}, required=True)):
    #await ctx.send("This command is currently in progress, thus only developers are allowed to access it.")
    global lbtypea, defvalues, sent
    defvalues = {'title': None, 'desc': None, 'slvl': None, 'sstyle': None, 'stop': None, 'mlvls': None, 'mtop': None}
    view = Crtlb(type=lbtype)
    lbtypea = lbtype
    sent = False
    await ctx.response.send_modal(view)

inline = bool
lb = ""
trknm = ""
lbtypea = ""
lbmsg = None
conte = nextcord.Interaction
sent = bool
class Crtlb(nextcord.ui.Modal):
    def __init__(self, type: str):
        super().__init__("Leaderboard Creation")  # Modal title
        global defvalues

        # Create a text input and add it to the modal
        self.lbtitle = nextcord.ui.TextInput(
            label="Leaderboard Title",
            min_length=2,
            max_length=50,
            default_value=defvalues["title"]
        )
        self.lbdesc = nextcord.ui.TextInput(
            label="Leaderboard Description (optional)",
            min_length=2,
            max_length=50,
            style=nextcord.TextInputStyle.paragraph,
            required=False,
            default_value=defvalues["desc"]
        )
        self.singlelvl = nextcord.ui.TextInput(
            label="Leaderboard Level (workshop ID)",
            min_length=0,
            max_length=30,
            placeholder="Level workshop ID",
            default_value=defvalues["slvl"]
        )
        self.singlestyle = nextcord.ui.TextInput(
            label="Leaderboard style (1-3)",
            min_length=0,
            max_length=30,
            placeholder="Look at the preview if needed.",
            default_value=defvalues["sstyle"]
        )
        self.singletop= nextcord.ui.TextInput(
            label="Top amount (max 25)",
            min_length=0,
            max_length=30,
            placeholder="Example: 5",
            default_value=defvalues["stop"]
        )
        self.multilvls = nextcord.ui.TextInput(
            label="Level IDS separated with - (max 25)",
            min_length=0,
            max_length=2,
            placeholder="Example: 3027682870-3027301734-3026954856",
            default_value=defvalues["mlvls"]
        )
        self.multitop = nextcord.ui.TextInput(
            label="Top amount (max 15)",
            min_length=0,
            max_length=2,
            placeholder="Example: 10",
            default_value=defvalues["mtop"]
        )

        if type == "single":
            self.add_item(self.lbtitle)
            self.add_item(self.lbdesc)
            self.add_item(self.singlelvl)
            self.add_item(self.singletop)
            self.add_item(self.singlestyle)
        elif type == "multi":
            self.add_item(self.lbtitle)
            self.add_item(self.lbdesc)
            self.add_item(self.multilvls)
            self.add_item(self.multitop)
        self.type = type

    async def callback(self, ctx: nextcord.Interaction) -> None:
        global inline, lb, trknm, defvalues, lbmsg, sent, conte
        defvalues = {'title': self.lbtitle.value, 'desc': self.lbdesc.value, 'slvl': self.singlelvl.value,
                     'sstyle': self.singlestyle.value, 'stop': self.singletop.value, 'mlvls': self.multilvls.value,
                     'mtop': self.multitop.value}
        lb = ""
        lbprev = discord.Embed(title=self.lbtitle.value, description=self.lbdesc.value)
        if self.type == "single":
            recs = json.loads(requests.get(f"https://api.zeepkist-gtr.com/records?LevelWorkshopId={self.singlelvl.value}&BestOnly=true&ValidOnly=true&InvalidOnly=false&WorldRecordOnly=false&Limit=25&Offset=0").text)['records']
            count = 1
            if self.singlestyle.value == "3":
                inline = True
            elif self.singlestyle.value == "1":
                inline = False
            for x in recs:
                if self.singlestyle.value == "2":
                    lb += f"{count}. {format_time(x['time'])} **by {x['user']['steamName']}**\n"
                    count += 1
                    trknm = x["level"]["name"]
                else:
                    discord.Embed.add_field(self=lbprev, name=f"{count}. {format_time(x['time'])}", value=f"by {x['user']['steamName']}", inline=inline)
                    count += 1
            if self.singlestyle.value == "2":
                discord.Embed.add_field(self=lbprev, name=trknm, value=lb)
            if sent is False:
                conte = await ctx.send("This is what your current leaderboard looks like! Would you want to edit it?", embed=lbprev, view=lbedit(), ephemeral=True)
                sent = True
            else:
                await conte.edit("This is what your current leaderboard looks like! Would you want to edit it?", embed=lbprev, view=lbedit())

def add_lb(type: str):
    print("it got fooking called mate, you believe this shit?")

def add_req(msgid, lvlid, user):
    with open("data.json", "r") as file:
        reqlist = json.load(file)
        new_req = {"msgid": str(msgid), "lvlid": str(lvlid), "user": str(user), "accepted": False}
        log(new_req)
        reqlist["requests"].append(new_req)
        with open("data.json", "w") as file:
            json.dump(reqlist, file, indent=2)

def check_reqs(lvlid: str=None, discid: str=None):
    with open("data.json", "r") as checking:
        reqlist = json.load(checking)
        if lvlid is not None:
            for x in reqlist["requests"]:
                if x["lvlid"] == lvlid:
                    return True
            return False
        elif discid is not None:
            for x in reqlist["requests"]:
                if x["msgid"] == discid:
                    return x
            return None

def aareq(msgid: str):
    with open("data.json", "r") as file:
        reqlist = json.load(file)
        for x in reqlist["requests"]:
            if x['msgid'] == msgid:
                x["accepted"] = True
        with open("data.json", "w") as file:
            json.dump(reqlist, file, indent=2)

def getacclvl():
    with open("data.json", "r") as file:
        reqlist = json.load(file)
        for x in reqlist["requests"]:
            log("looped in for x")
            if x["accepted"] is True:
                log(f"passed 1st if statement: {x}")
                return x
        log("for x ended")
        return "ewwor"

def mtplvls():
    try:
        log("called")
        with open("data.json", "r") as file:
            reqlist = json.load(file)
            for x in reqlist["requests"]:
                if x["accepted"] is True:
                    log("passed 1st if statement")
                    reqlist["requests"].remove(x)
                    reqlist["played"].append(x)
                    with open("data.json", "w") as file:
                        json.dump(reqlist, file, indent=2)
                        return x
    except Exception as ewwor:
        log(ewwor)


@bot.slash_command(name="request_level")
async def lvlreq(ctx, workshopid: int):
    req = json.loads(requests.get(f"https://api.zeepkist-gtr.com/levels?WorkshopId={workshopid}&ValidOnly=false&InvalidOnly=false&Limit=1&Offset=0").text)
    if req["totalAmount"] > 0:
        lvl = req["levels"][0]
        check = check_reqs(lvlid=str(workshopid))
        if check is True:
            await ctx.send("This level has already been requested!")
        else:
            reqchannel = await bot.fetch_channel(966694897799286787)
            class Buttons(nextcord.ui.View):
                def __init__(self):
                    super().__init__()
                @nextcord.ui.button(label="Yes", style=nextcord.ButtonStyle.green)
                async def valid(self, button: nextcord.Button, ctx: nextcord.Interaction):
                    try:
                        ureq = await reqchannel.send(f"**{ctx.user}** has requested a Level!\nhttps://steamcommunity.com/sharedfiles/filedetails/?id={workshopid}")
                        add_req(msgid=ureq.id, lvlid=workshopid, user=ctx.user.id)
                        await ctx.send("Successfully sent a request, keep an eye in <#968060466637185044> to see if your request got accepted!")
                        self.stop()
                    except Exception as error:
                        await ctx.send(f"An error occurred: {error}")

                @nextcord.ui.button(label="No", style=nextcord.ButtonStyle.red)
                async def novalid(self, button: nextcord.Button, ctx: nextcord.Interaction):
                    await ctx.send("Request cancelled.")
                    self.stop()

            await ctx.send(f"is the level you want to submit called **{lvl['name']}** made by {lvl['author']} ?", view=Buttons())
    else:
        await ctx.send("Could not find the level! Make sure the level is registered on GTR!")

@bot.message_command(name="accept-request")
async def accreq(ctx, msg):
    log(f"accreq called by {ctx.user}")
    if ctx.user.id == 785037540155195424:
        aclvl = check_reqs(discid=str(msg.id))
        if aclvl is not None:
            log("aclvl is not None")
            try:
                log("Trying to accept a lvl request")
                aareq(str(msg.id))
                log("accepting a lvl request went trough.")
                await ctx.send("level added!")
            except Exception as ewwor:
                log(ewwor)
                ctx.send("Something wrong happened!", ephemeral=True)
        else:
            log("aclvl is None (failed to find level)")
            await ctx.send("failed to find level.", ephemeral=True)
    else:
        await ctx.send("You are not allowed to use this.", ephemeral=True)

timestamp = 0
async def totd():
    global timestamp
    timestamp = calendar.timegm(datetime.datetime.utcnow().timetuple())
    log(f"Timestamp is: {timestamp}")
    totdchan = await bot.fetch_channel(1154510654196166706) # bot.fetch_channel(899725913586032701)
    log("DAILY TRACK WOOOOOOOOOOOOOOOOOOOOOOOOOO")
    dailytrek = getacclvl()
    if dailytrek == "ewwor":
        await totdchan.send("An error occurred!")
        log("NOOOOOO WE DONT GET TOTD CAUSE NO TREK DAMMIT :<")
    else:
        dailytrekgtr = json.loads(requests.get(f"https://api.zeepkist-gtr.com/levels?WorkshopId={dailytrek['lvlid']}&ValidOnly=true&Limit=1&Offset=0").text)['levels'][0]
        log(f"dailytrekgtr went though: {dailytrekgtr}")
        log(f"TRACK FUCKING FOUND WOOOOOOOOO ALSO HERES THE TRACK JSON: {dailytrek}")
        embed = discord.Embed(title="Track of the day!", description=None, color=nextcord.Color.purple(), timestamp=datetime.datetime.now())
        embed = discord.Embed.add_field(self=embed, name="Level:", value=f"**Link:** [steam link](https://steamcommunity.com/sharedfiles/filedetails/?id={dailytrek['lvlid']})\n"
                                                                         f"**Name:** {dailytrekgtr['name']}\n"
                                                                         f"**Creator:** {dailytrekgtr['author']}\n"
                                                                         f"**Author time:** {format_time(dailytrekgtr['timeAuthor'])}", inline=False)
        embed = discord.Embed.add_field(self=embed, name="Requested by:", value=f"<@{dailytrek['user']}>", inline=False)
        embed = discord.Embed.set_thumbnail(self=embed, url="https://cdn.discordapp.com/attachments/966694897799286787/1155109884799504424/image.png")
        embed = discord.Embed.set_image(self=embed, url=f"https://storage.googleapis.com/zeepkist-gtr/thumbnails/{urllib.parse.quote(dailytrekgtr['uniqueId'])}.jpeg")
        embed = discord.Embed.set_footer(self=embed, icon_url="https://cdn.discordapp.com/attachments/966694897799286787/1155111574160298014/image.png")
        await totdchan.send("*ping*", embed=embed)
        embedtwo = discord.Embed(title="Leaderboard:", description="No records yet.", colour=nextcord.Color.purple())
        totdlb = await totdchan.send(embed=embedtwo)
        await totdlbt.start(chan=totdlb, lvlid=dailytrekgtr["id"], ts=timestamp)

async def totdend():
    global timestamp
    try:
        totdlbt.cancel()
        dailytrek = getacclvl()
        dailytrekgtr = json.loads(requests.get(f"https://api.zeepkist-gtr.com/levels?WorkshopId={dailytrek['lvlid']}&ValidOnly=true&Limit=1&Offset=0").text)['levels'][0]
        recs = json.loads(requests.get(f"https://api.zeepkist-gtr.com/records/best?Level={dailytrekgtr['id']}&ValidOnly=true&InvalidOnly=false&After={timestamp}&Limit=50").text)["records"]
        recsamount = 0
        for c in recs:
            recsamount += 1
        points = []
        for p in recs:
            points.append({"user": p['user']['steamName'], "points": recsamount})
            recsamount -= 1
        log(points)
        pointslb = ""
        places = 1
        for pl in points:
            pointslb += f"{places}. {pl['user']} with {pl['points']} points\n"
            places += 1
        totdchan = await bot.fetch_channel(1154510654196166706)
        embed = discord.Embed(title="Track of the day!", description="Track of the day is over! These are the results!", color=nextcord.Color.purple(), timestamp=datetime.datetime.now())
        embed = discord.Embed.set_thumbnail(self=embed, url="https://cdn.discordapp.com/attachments/966694897799286787/1155109884799504424/image.png")
        embed = discord.Embed.add_field(self=embed, name="Today's Result:", value=pointslb)
        embed = discord.Embed.add_field(self=embed, name="All-time Results:", value="Coming soon!", inline=False)
        await totdchan.send(embed=embed)
        mtplvls()
    except Exception as ewwor:
        log(ewwor)


scheduler = AsyncIOScheduler()
cronny = CronTrigger(day_of_week="mon-sun", hour="19", minute="00", timezone="CET")
cronnyend = CronTrigger(day_of_week="mon-sun", hour="19", minute="15", timezone="CET")
scheduler.add_job(totd, trigger=cronny)
scheduler.add_job(totdend, trigger=cronnyend)
scheduler.start()

@tasks.loop(seconds=5)
async def totdlbt(chan=None, lvlid: str=None, ts=None):
    totdlb = ""
    recs = json.loads(requests.get(f"https://api.zeepkist-gtr.com/records/best?Level={lvlid}&ValidOnly=true&InvalidOnly=false&After={ts}&Limit=50").text)["records"]
    log(recs)
    for x in recs:
        totdlb += f"{format_time(x['time'])} **by {x['user']['steamName']}**\n"
    embed = discord.Embed(title="Leaderboard:", description=totdlb, colour=nextcord.Color.purple())
    lead = await chan.edit(embed=embed)
    log(f"edited the embed desc with: {totdlb}")

submissionschannels = []
@bot.event
async def on_ready():
    global submissionschannels
    log(f"Loaded up!")
    print("going bruv")
    with open("data.json", "r") as f:
        data = json.load(f)
        submissionschannels = data["submission-channels"]
    await submission_checker.start()

def m_addlvl(lvl: dict):
    log(f"reached with: {lvl}")
    with open("data.json", 'r') as f:
        data = json.load(f)
    with open("data.json", 'w') as ft:
        data["submission-channels"][0]['levels'].append({"wsid": lvl['wsid'], "lvlname": lvl['lvlname'], "lvluid": lvl['lvluid'], "lvlatn": lvl['lvlatn']})
        json.dump(data, ft, indent=2)

def m_checkduplicate(id: int):
    with open("data.json", 'r') as f:
        data = json.load(f)
    for x in data["submission-channels"][0]['levels']:
        if x['wsid'] == id:
            return True
    return False

@tasks.loop(seconds=5)
async def submission_checker():
    global submissionschannels
    pattern = r'id=(\d+)'
    for info in submissionschannels:
        try:
            channel = await bot.fetch_channel(info['channelid'])
            logchannel = await bot.fetch_channel(info['logchannel'])
            checkage = await fetchmessages({"fetchtype":1, "channel":info["channelid"], "customfeature": 1, "fetchobject": 6969})
            if checkage["code"] == 404 and checkage["objectcode"] == 0:
                return
            else:
                for x in checkage['message']['usermessages']:
                    if x["code"] == 404:
                        await channel.send(f"<@{x['userid']}>, '{x['message']}' is not a valid submission! Please provide a valid steam workshop link!")
                        await x['rawmessage'].delete()
                    elif x['code'] == 200:
                        id = re.findall(pattern, x['message'])
                        req = requests.get(f"https://api.zworpshop.com/levels/workshop/{id[0]}?IncludeReplaced=true")
                        if req.status_code == 404:
                            await x["rawmessage"].add_reaction("❌")
                            await x['rawmessage'].reply(f":warning: I could not find the level. The playlist creator will have to manually add this level! :warning:")
                            await logchannel.send(f"*rony ping*\ni could not find a submission where this was linked: {x['message']}\nThis is either an invalid level or a level i could not find!")
                        elif req.status_code == 200:
                            lvl = json.loads(req.text)
                            crtm = lvl[0]["createdAt"].split("-")
                            lvlmonth = int(crtm[1])
                            if lvlmonth == datetime.datetime.utcnow().month:
                                if len(lvl) > 1:
                                    await x["rawmessage"].add_reaction("❌")
                                    await x['rawmessage'].reply(f":warning: This submission has several levels in it! Please stop using level packs and upload all levels separately! :warning:")
                                else:
                                    if not m_checkduplicate(lvl[0]['workshopId']):
                                        m_addlvl({"wsid": lvl[0]['workshopId'], "lvlname": lvl[0]['name'], "lvluid": lvl[0]['fileUid'], "lvlatn": lvl[0]['fileAuthor']})
                                        await x["rawmessage"].add_reaction("✅")
                                        await x['rawmessage'].reply(f"Level '{lvl[0]['name']}' added!")
                                    else:
                                        await x["rawmessage"].add_reaction("❌")
                                        await x['rawmessage'].reply(":warning: this level is already submitted! :warning:")
                            else:
                                await x["rawmessage"].add_reaction("❌")
                                await x['rawmessage'].reply(f":warning: this level is too old! the level needs to be made in {calendar.month_name[datetime.datetime.utcnow().month]} :warning:")
                        else:
                            await x['rawmessage'].reply(f":warning: Something really wrong happened! :warning:")
        except Exception as ewwor:
            if isinstance(ewwor, TypeError):
                return
            else:
                await logchannel.send(f"*rony ping*\n{fwogutils.errormessage(ewwor)}")
                log(ewwor)

@bot.slash_command(name="set")
async def set(ctx):
    pass

@set.subcommand(name="submission")
async def subm(ctx):
    pass

@bot.slash_command(name="get")
async def get(ctx):
    pass

@subm.subcommand(name="channel")
async def subchannel(ctx, chan: nextcord.TextChannel):
    global submissionschannels
    if ctx.user.id in [785037540155195424, 181519107311534080]:
        with open("data.json", 'r') as f:
            data = json.load(f)
        with open("data.json", 'w') as ft:
            data["submission-channels"][0]['channelid'] = chan.id
            json.dump(data, ft, indent=2)
            submissionschannels[0]['channelid'] = chan.id
            await ctx.send(f"Submissions channel set to: <#{chan.id}>")
    else:
        await ctx.send("You do not have the permission to use this.", ephemeral=True)

@subm.subcommand(name="log")
async def sublog(ctx, chan: nextcord.TextChannel):
    global submissionschannels
    if ctx.user.id in [785037540155195424, 181519107311534080]:
        with open("data.json", 'r') as f:
            data = json.load(f)
        with open("data.json", 'w') as ft:
            data["submission-channels"][0]['logchannel'] = chan.id
            json.dump(data, ft, indent=2)
            submissionschannels[0]['logchannel'] = chan.id
            await ctx.send(f"Submissions log channel set to: <#{chan.id}>")
    else:
        await ctx.send("You do not have the permission to use this.", ephemeral=True)

@get.subcommand(name="playlist")
async def getpl(ctx, playlistname: str):
    if ctx.user.id in [785037540155195424, 181519107311534080]:
        with open("data.json", 'r') as f:
            data = json.load(f)
        with open("playlist.zeeplist", 'r') as pl:
            zpl = json.load(pl)
        with open("playlist.zeeplist", 'w') as pld:
            zpl["levels"] = []
            zpl["name"] = playlistname
            for x in data['submission-channels'][0]['levels']:
                zpl["levels"].append({
                    "UID": f"{x['lvluid']}",
                    "WorkshopID": f"{x['wsid']}",
                    "Name": f"{x['lvlname']}",
                    "Author": f"{x['lvlatn']}"
                })
            json.dump(zpl, pld, indent=2)
        os.rename("playlist.zeeplist", f"{playlistname}.zeeplist")
        await ctx.send("The playlist has been generated."
                        " To import the playlist into the host controls simply drag the file below into this specific directory: `%userprofile%\AppData\Roaming\Zeepkist\Playlists`."
                        " to easily access this directory: (for windows only) press Win+R and paste the directory in the text box.",
                        file=nextcord.File(f'{playlistname}.zeeplist'))
        os.rename(f"{playlistname}.zeeplist", "playlist.zeeplist")
    else:
        await ctx.send("You do not have permissions to use this!", ephemeral=True)


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
                if message.author.id in [1143521016031744025, 181519107311534080]:
                    if len(messages) == 0:
                        return {"code": 404, "objectcode": 0}
                    else:
                        messages.reverse()
                        return {"code": 200, "message": {'usermessages': messages}, "objectcode": 1}
                if re.findall(patterna, message.content):
                    urls = re.findall(patterna, message.content)
                    if len(urls) > 1:
                        for l in urls:
                            messages.append({'code': 200, 'userid': message.author.id, "message": l, 'rawmessage': message})
                    else:
                        messages.append({'code': 200, 'userid': message.author.id, "message": urls[0], 'rawmessage': message})
                else:
                    messages.append({'code': 404, 'userid': message.author.id, "message": message.content, 'rawmessage': message})
    except Exception as ewwor:
        await channel.send(fwogutils.errormessage(ewwor))
        log(ewwor)

bot.run(privaat.token)