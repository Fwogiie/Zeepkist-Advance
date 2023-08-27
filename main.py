import requests
import json
import os
import nextcord
import re
import discord
from discord.ext import commands, tasks
from nextcord.ui import View, Select
from nextcord.errors import HTTPException, InteractionResponded
import urllib
from urllib import parse
import privaat
import asyncio

intents = nextcord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix='!',
                   intents=intents,
                   help_command=None,
                   owner_id=785037540155195424)

ids = []
lvlsamount = 0
gitgud = bool
async def fetch(channelid: int, amount: int, oldest_first: bool, fetched_react: int, messageid: int=0):
    print(oldest_first)
    global ids, lvlsamount, gitgud
    gitgud = False
    ids = []
    patterna = r'https://steamcommunity\.com/sharedfiles/filedetails/\?id=\d+'
    channel = bot.get_channel(channelid)
    await status(f"Fetching messages.")
    async for x in channel.history(limit=amount, oldest_first=False):
        if gitgud is True:
            if oldest_first is True:
                print("pear")
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
    if ctx.guild.id == 1083812526917177514:
        print(error)
        return
    await ctx.send(f"An error occured. if this persists please report it in the zeepkist modding server: [here](https://discord.gg/a4FxG9RpV3) in this thread: https://discord.com/channels/972933002516647986/1126438917420359691 \n \n Error: `{error}`", ephemeral=True)

@bot.event
async def on_command_error(ctx, error):
    print(error)
    await ctx.send(f"An error occured. if this persists please report it in the zeepkist modding server: [here](https://discord.gg/a4FxG9RpV3) in this thread: https://discord.com/channels/972933002516647986/1126438917420359691 \n \n Error: `{error}`")

@bot.event
async def on_ready():
    await bot.change_presence(activity=discord.Activity(type=discord.ActivityType.watching, name="For level submissions"))
    MyCog()
    for guild in bot.guilds:
        print(f"Connected to guild: {guild.name} ({guild.id}) with {guild.member_count} members.")

cmdmsg = int
@bot.message_command(name="create-playlist")
async def msgcmd(ctx, msg):
    global cmdmsg, makekoc
    makekoc = False
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
        print(self.values[0])
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
            print("going bruv")
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


# ZeeplistBuilder
async def add_user(discid: int, gtrid: int=0, check: bool=False):
    with open("auth.json", "r") as file:
        authlist = json.load(file)

    if check is True:
        for x in authlist["users"]:
            if discid == x["discordId"]:
                return True

    if check is False:
        # Create a new level tuple
        new_user = (
            {
                "gtrId": gtrid,
                "discordId": discid,
                "unlockedAC": [],
                "lockedAC": []
            }
        )
        print(new_user)

        # Add the new level tuple to the "levels" list
        authlist["users"].append(new_user)

        # Save the updated playlist back to the file
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
        b = a.text
        c = json.loads(b)
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

thinsthing = None
sent = False
bl = ["76561198050792757", "76561198091849339", "76561199027567424",
     "76561198359568548", "76561199089299899", "76561198047403251",
      "76561198855034411"]

@bot.slash_command(name="blacklist", description="Reserved for yolo and grimmlon only!")
async def blackl(ctx, usersteamid: str):
    global bl
    if ctx.user.id in [257321046611329026, 506854236206792704, 785037540155195424]:
        bl.append(usersteamid)
        await ctx.send(f"Blacklisted {usersteamid}", ephemeral=True)
        print(bl)
    else:
        await ctx.send("You are not allowed to use this command.", ephemeral=True)

class MyCog(commands.Cog):
    def __init__(self):
        self.loop.start()
    @tasks.loop(seconds=60)
    async def loop(self):
        global thisthing, sent, bl
        a = requests.get("https://api.zeepkist-gtr.com/records?LevelId=19066&BestOnly=true&ValidOnly=true&After=%221692990000%22&Before=%221692914400%22&Limit=25&Offset=0")
        b = a.text
        c = json.loads(b)["records"]
        channel = await bot.fetch_channel(1144730662000136315)
        embedd = discord.Embed(title="Zeepkist Showdown Qualifier times", description=None, color=nextcord.Color.dark_orange())
        count = 1
        blcount = 0
        for e in c:
            if e["user"]["steamId"] in bl:
                blcount += 1
        a = requests.get(f"https://api.zeepkist-gtr.com/records?LevelId=19066&BestOnly=true&ValidOnly=true&After=%221692990000%22&Before=%221692914400%22&Limit={25 + blcount}&Offset=0")
        b = a.text
        c = json.loads(b)["records"]
        for x in c:
            if x["user"]["steamId"] in bl:
                print("Blacklisted: " + x["user"]["steamId"])
            else:
                discord.Embed.add_field(self=embedd, name=f"{count}. {format_time(x['time'])}", value=f"by {x['user']['steamName']}")
                count += 1
        if sent is False:
            thisthing = await channel.send(embed=embedd)
            sent = True
        else:
            await thisthing.edit(embed=embedd)
        #gwan = get_users()
        #for user in gwan:
            #print(user)
            #a = requests.get(f"https://api.zeepkist-gtr.com/stats?UserId={user['gtrId']}")
            #b = a.text
            #c = json.loads(b)
            #discuser = await bot.fetch_user(user["discordId"])
            #await discuser.send(c)

bot.run(privaat.token)