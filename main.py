import requests
import json
import os
import nextcord
import re
import discord
from discord.ext import commands
from nextcord.errors import HTTPException

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
    global ids, lvlsamount, gitgud
    gitgud = False
    ids = []
    patterna = r'https://steamcommunity\.com/sharedfiles/filedetails/\?id=\d+'
    channel = bot.get_channel(channelid)
    await status(f"Fetching messages.")
    async for x in channel.history(limit=amount, oldest_first=False):
        if gitgud is True:
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
    await status(f"\nFetched {lvlsamount} levels.\n")
    if oldest_first is True:
        ids.reverse()

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
    await ctx.send(f"An error occured. if this persists please report it in the zeepkist modding server: [here](https://discord.gg/a4FxG9RpV3) in this thread: https://discord.com/channels/972933002516647986/1126438917420359691 \n \n Error: `{error}`")

@bot.event
async def on_command_error(ctx, error):
    await ctx.send(f"An error occured. if this persists please report it in the zeepkist modding server: [here](https://discord.gg/a4FxG9RpV3) in this thread: https://discord.com/channels/972933002516647986/1126438917420359691 \n \n Error: `{error}`")

@bot.event
async def on_ready():
    await bot.change_presence(activity=discord.Activity(type=discord.ActivityType.watching, name="For level submissions"))
    for guild in bot.guilds:
        print(f"Connected to guild: {guild.name} ({guild.id}) with {guild.member_count} members.")

cmdmsg = int
@bot.message_command(name="create-playlist")
async def msgcmd(ctx, msg):
    global cmdmsg
    modal = Crtpl()
    cmdmsg = msg.id
    await ctx.response.send_modal(modal)

class Crtpl(nextcord.ui.Modal):
    def __init__(self):
        super().__init__("playlist creation")  # Modal title

        # Create a text input and add it to the modal
        self.name = nextcord.ui.TextInput(
            label="Playlist name",
            min_length=2,
            max_length=50,
        )
        self.add_item(self.name)

    async def callback(self, ctx: nextcord.Interaction) -> None:
        global ids, lvlsamount, cont, lvlnames, statuslog, unfound
        statuslog = "Executing command:\n\n"
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

bot.run("MTEyNjQzMDk0MjkyNDM4NjMxNQ.GQECw9.fsmJwixgP5vXPXp0mhy6Unr-Wbv4LSW_qolBXE")