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
import urllib
from urllib.parse import quote
import fwogutils
from fwogutils import bot as bot
from fwogutils import log as log
from fwogutils import format_time as format_time
from fwogutils import views
import random
import websockets
from fwogutils import GTR as GTR

bot.load_extension("onami")

"""@bot.event
async def on_application_command_error(ctx, error):
    log(error)
    print(error)
    try:
        await ctx.send(f"{fwogutils.errormessage(error)}", ephemeral=True)
    except nextcord.errors.InteractionResponded:
        pass"""


@bot.event
async def on_command_error(ctx, error):
    log(error)

leaderboards = {}

@bot.event
async def on_ready():
    global submissionschannels, leaderboards
    log(f"Loaded up! with bot ID: {bot.user.id}")
    log("initializing startup guilds")
    #await bot.change_presence(activity=discord.Activity(type=discord.ActivityType.watching, name="For level submissions"))
    for guild in bot.guilds:
        print(f"Connected to guild: {guild.name} ({guild.id}) with {guild.member_count} members.")
        log(f"Connected to guild: {guild.name} ({guild.id}) with {guild.member_count} members.")
    log("initializing startup cache for live leaderboards.")
    with open("data.json", "r") as f:
        data = json.load(f)
        leaderboards = data["leaderboards"]
        log(f"leaderboards cache succeeded.")
        if bot.user.id == 1126430942924386315:
            log("updating the live leaderboards cause of start.")
            await rankingsfunc(fwogutils.getgtruserrankings(limit=100, offset=0))
            log("Process done to the GTR rankings leaderboard.")
        await rankingsfunc(fwogutils.getgtruserrankings(limit=100, offset=0))
    #await wrcallback()

@bot.is_owner
@bot.command(name="log")
async def ownlog(ctx, type: str, *, text: str = None):
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

@bot.message_command(name="create-playlist")
async def create_pl(ctx, msg: nextcord.Message):
    chan, msgs = await bot.fetch_channel(ctx.channel.id), []
    async for x in chan.history(limit=500):
        msgs.append(x.content)
        if x.id == msg.id:
            msgs.reverse()
            break
    if len(msgs) < 2:
        await ctx.send("You need at least 2 levels to create a playlist!", ephemeral=True)
        return
    async def modal_sub(ctx):
        wsids, levels, sorting, levelfails, antipack, duplicheck, packlvls, dupliwarn, dupliwarnlvls = [], [], {}, "", [], [], "", [], ""
        for x in msgs:
            workshop_urls = re.findall('https://steamcommunity\.com/sharedfiles/filedetails/\?id=\d+', x)
            if workshop_urls:
                for url in workshop_urls:
                    wsids.append(url.split('=')[1])
        if not wsids:
            log("Playlist would be empty, warning and returning")
            await ctx.send("Your playlist would be empty, so i dint create any!", ephemeral=True)
            return
        else:
            ctxe = await ctx.send("processing", ephemeral=True)
            reqlevels = json.loads(requests.post(f"https://graphql.zeepkist-gtr.com", json={"query": "query GetLevels($workshopIds: [BigFloat!]) { allLevelItems(filter: { workshopId: { in: $workshopIds } }) { nodes { name fileAuthor fileUid workshopId } } }", "variables": {"workshopIds": wsids}}).text)
            for x in reqlevels["data"]["allLevelItems"]["nodes"]:
                id = x['workshopId']
                if id not in antipack:
                    log(f"{id} wasnt in antipack, adding and appending to antipack")
                    sorting[id] = {"UID": x['fileUid'], "WorkshopID": x['workshopId'], "Name": x['name'], "Author": x['fileAuthor']}
                    antipack.append(id)
                elif id in antipack and id not in duplicheck:
                    log(f"{id} is pack, adding to pack list for warn")
                    packlvls += f"- [{x['name']} - {id}](<https://steamcommunity.com/sharedfiles/filedetails/?id={id}>)\n"
                    duplicheck.append(id)
            for x in wsids:
                try:
                    log(f"Trying for {x} in for wsids")
                    levels.append(sorting[x])
                    log("Level Appended.")
                except KeyError:
                    log(f"{x} is assumed to have failed the try, KeyError was raised")
                    levelfails += f"- [Workshop ID: {x}](<https://steamcommunity.com/sharedfiles/filedetails/?id={x}>)\n"
            for x in levels:
                if x not in dupliwarn:
                    dupliwarn.append(x)
                else:
                    dupliwarnlvls += f"- [{x['Name']} - {x['WorkshopID']}](<https://steamcommunity.com/sharedfiles/filedetails/?id={x['WorkshopID']}>)\n"
            plname = textinput.value
            async def btn_add_level(ctx):
                view = fwogutils.views.LevelSelect()
                await ctx.send(view=view, ephemeral=True)
                await bot.wait_for("interaction", check=lambda interaction: interaction.data['custom_id'] == "thisisalevelsub", timeout=120)
                level = fwogutils.get_returnlist()[0]
                pl["levels"].append(level)
                fwogutils.dumppl(pl)
                fwogutils.renamepl(plname)
                await ctxe.edit(file=nextcord.File(f"{plname}.zeeplist"))
                fwogutils.undorename(plname)
                await ctx.send(f"added **{level['Name']}** to the playlist", ephemeral=True)
            async def btn_remove_duplicates(ctx):
                duplicheck, updlvls, duplicount = [], [], 0
                outdatedlvls = pl["levels"]
                for x in outdatedlvls:
                    if x not in duplicheck:
                        updlvls.append(x)
                        duplicheck.append(x)
                    else:
                        duplicount += 1
                pl["levels"] = updlvls
                pl["amountOfLevels"] = len(updlvls)
                fwogutils.dumppl(pl)
                fwogutils.renamepl(plname)
                await ctxe.edit(file=nextcord.File(f"{plname}.zeeplist"))
                fwogutils.undorename(plname)
                await ctx.send(f"{duplicount} Duplicates removed.", ephemeral=True)
            async def btn_shuffle_pl(ctx):
                random.shuffle(pl["levels"])
                fwogutils.dumppl(pl)
                fwogutils.renamepl(plname)
                await ctxe.edit(file=nextcord.File(f"{plname}.zeeplist"))
                fwogutils.undorename(plname)
                await ctx.send("Playlist has been shuffled.", ephemeral=True)
            async def btn_make_koc(ctx):
                newlvls = []
                async def btn_continue(ctx):
                    for x in pl['levels']:
                        newlvls.append(x)
                        newlvls.append({"UID": "09052023-112732077-[CTR]OwlPlague-249589054336-368", "WorkshopID": "2973690373",
                                        "Name": "KICK OR CLUTCH VOTING LEVEL", "Author": "[CTR]OwlPlague"})
                    pl['levels'] = newlvls
                    pl["amountOfLevels"] = len(newlvls)
                    fwogutils.dumppl(pl)
                    fwogutils.renamepl(plname)
                    await ctxe.edit(file=nextcord.File(f"{plname}.zeeplist"))
                    fwogutils.undorename(plname)
                    await ctx.send("Done!", ephemeral=True)
                async def btn_edit_level(ctx):
                    view = fwogutils.views.LevelSelect()
                    await ctx.send(view=view, ephemeral=True)
                    await bot.wait_for("interaction", check=lambda interaction: interaction.data['custom_id'] == "thisisalevelsub", timeout=120)
                    level = fwogutils.get_returnlist()[0]
                    for x in pl['levels']:
                        newlvls.append(x)
                        newlvls.append(level)
                    pl['levels'] = newlvls
                    pl["amountOfLevels"] = len(newlvls)
                    fwogutils.dumppl(pl)
                    fwogutils.renamepl(plname)
                    await ctxe.edit(file=nextcord.File(f"{plname}.zeeplist"))
                    fwogutils.undorename(plname)
                    await ctx.send("Done!", ephemeral=True)
                kocview = nextcord.ui.View(timeout=60)
                btncontinue = nextcord.ui.Button(label="Continue", style=nextcord.ButtonStyle.green)
                btncontinue.callback = btn_continue
                btneditlvl = nextcord.ui.Button(label="Edit Level", style=nextcord.ButtonStyle.grey)
                btneditlvl.callback = btn_edit_level
                kocview.add_item(btncontinue)
                kocview.add_item(btneditlvl)
                await ctx.send("Make this playlist Koc-Like?\n*Continuing Would use the default voting level*", view=kocview, ephemeral=True)
            editbtns = nextcord.ui.View(timeout=60)
            btnaddlvl = nextcord.ui.Button(label="Add Level", style=nextcord.ButtonStyle.green)
            btnaddlvl.callback = btn_add_level
            btnremdupelvls = nextcord.ui.Button(label="Remove Duplicate Levels", style=nextcord.ButtonStyle.red)
            btnremdupelvls.callback = btn_remove_duplicates
            btnshufflvls = nextcord.ui.Button(label="Shuffle Levels", style=nextcord.ButtonStyle.grey)
            btnshufflvls.callback = btn_shuffle_pl
            btnmakekoc = nextcord.ui.Button(label="Make Koc", style=nextcord.ButtonStyle.grey)
            btnmakekoc.callback = btn_make_koc
            editbtns.add_item(btnaddlvl)
            editbtns.add_item(btnremdupelvls)
            editbtns.add_item(btnshufflvls)
            editbtns.add_item(btnmakekoc)
            pl = {"name": plname, "amountOfLevels": len(levels), "roundLength": 480.0, "shufflePlaylist": False, "UID": [], "levels": levels}
            fwogutils.dumppl(pl)
            fwogutils.renamepl(plname)
            await ctxe.edit(f"# Your playlist has been generated!\n### Failed levels (These levels failed and would need to be added manually):\n{levelfails[:500]}\n"
                            f"### Level packs (Might need manual adjustments):\n{packlvls[:500]}\n### Duplicate Levels (Press the remove duplicates button to remove them):\n{dupliwarnlvls[:500]}",
                            file=nextcord.File(f"{plname}.zeeplist"), view=editbtns)
            fwogutils.undorename(plname)
    modal = nextcord.ui.Modal(title="Playlist creation")
    textinput = nextcord.ui.TextInput(label="Playlist name", min_length=1, max_length=50)
    modal.add_item(textinput)
    modal.callback = modal_sub
    await ctx.response.send_modal(modal)

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
                lb = json.loads(requests.get( f"https://api.zeepkist-gtr.com/users/rankings?Limit={self.page['limit']}&Offset={self.page['offset']}").text)
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
                embed.add_field(name=f"{x['position']}. {x['user']['steamName']}", inline=False, value=f"World Records: {x['amountOfWorldRecords']}\nScore: {x['score']}")
            await emb.edit(embed=embed, view=Lbpage())

    lbb = json.loads(requests.get("https://api.zeepkist-gtr.com/users/rankings?Limit=10&Offset=0").text)
    embedd = discord.Embed(title="GTR Rankings", color=nextcord.Color.purple(), timestamp=datetime.datetime.now())
    embedd = discord.Embed.set_footer(self=embedd, text=f"page: {page['page']}, Total amount: {lbb['totalAmount']}")
    for x in lbb["rankings"]:
        embedd.add_field(name=f"{x['position']}. {x['user']['steamName']}", inline=False, value=f"World Records: {x['amountOfWorldRecords']}\nScore: {x['score']}")
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
            await ctx.send('The playlist has been generated.'
                           r' To import the playlist into the host controls simply drag the file below into this specific directory: `%userprofile%\AppData\Roaming\Zeepkist\Playlists`.'
                           ' to easily access this directory: (for windows only) press Win+R and paste the directory in the text box.',
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
async def updpl(ctx, playlist: nextcord.Attachment = nextcord.SlashOption(description="Update this playlist to newer levels!", required=True),
                removeduplicates: bool = nextcord.SlashOption(description="Removes duplicates if there are any.", required=True)):
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
        data = {'updlvls': 0, 'updlvlsnames': "", 'dellvls': 0, 'dellvlsnames': "", 'nflvls': 0, 'nflvlsnames': "", 'duplilvls': 0, 'duplilvlsnames': "", 'duplicheck': []}
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
                                pllvlsupd["levels"].append(
                                    {"UID": f"{reqtxt[0]['fileUid']}", "WorkshopID": int(reqtxt[0]['workshopId']),
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
            await ctx.edit(f"## {data['updlvls']} level(s) were updated.\n> ### Updated level(s):\n{data['updlvlsnames'][:15]}\n"
                           f"## {data['dellvls']} level(s) were deleted from the workshop. (These can manually be added!)\n> ### Deleted level(s):\n{data['dellvlsnames'][:15]}\n"
                           f"## {data['nflvls']} level(s) were not found. (These can manually be added!)\n> ### Not Found level(s):\n{data['nflvlsnames'][:15]}\n"
                           f"## {data['duplilvls']} level(s) were duplicated.\n> ### Duplicated level(s):\n{data['duplilvlsnames']}", file=nextcord.File(f"{name}.zeeplist"))
            os.rename(f"{name}.zeeplist", "playlist.zeeplist")
        except HTTPException as ewwor:
            await ctx.edit(fwogutils.errormessage(ewwor))
            log(ewwor)
    else:
        await ctx.send("Please attach a valid .zeeplist file.")


@bot.slash_command(name="reverse")
async def rev(ctx):
    pass


@rev.subcommand(name="playlist", description="Reverse a playlist!")
async def revpl(ctx, playlist: nextcord.Attachment = nextcord.SlashOption(description="The playlist to reverse.",
                                                                          required=True)):
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
async def shufpl(ctx, playlist: nextcord.Attachment = nextcord.SlashOption(description="The playlist to Shuffle.", required=True)):
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

@bot.slash_command(name="get")
async def get(ctx):
    pass

@get.subcommand(name="top")
async def gettop(ctx):
    pass


@gettop.subcommand(name="levels", description="Get a playlist from levels worth the most points in GTR!")
async def gettoplvls(ctx, amount: int = nextcord.SlashOption(
    description="Amount of levels to have in the playlist! (Maximum 999)"),
                     playlistname: str = nextcord.SlashOption(description="The name of the playlist!")):
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
            "levels": levels})
        fwogutils.renamepl(playlistname)
        await ctx.edit(f"Your playlist has been generated! {len(levels)}/{amount} levels were found!", file=nextcord.File(f"{playlistname}.zeeplist"))
        fwogutils.undorename(playlistname)
    else:
        await ctx.edit("Error! Limit is 999!")


@bot.slash_command(name='crtteam', guild_ids=[1127321762686836798])
async def crtteam(ctx, teamname: str, teamtag: str, pa: str, pb: str, color: str):
    color = fwogutils.hex_to_rgb(color)
    embed = discord.Embed(title=f"[{teamtag}] {teamname}", description=f"{pa}\n{pb}", color=nextcord.Color.from_rgb(color[0], color[1], color[2]))
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

            await ctx.send(
                f"Hello there! i have detected that you have a GTR account by the name of **{gtrcheck[1]['steamName']}**,"
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
        await ctx.send("I did not find any discord linkage, Please link your discord to your GTR by reproducing the following steps in-game:\n"
                       "`Settings -> Mods -> Scroll to GTR -> In the 'discord' section, Press 'Link'`", ephemeral=True)


async def rankingsfunc(gtrrankings):
    global leaderboards
    leaderboard = await bot.get_channel(1203645881279184948).fetch_message(leaderboards['rankings'])
    stringedrankings = ""
    for x in gtrrankings[:20]:
        stringedrankings += f"{x['node']['rank']}. `{x['node']['userByIdUser']['steamName']}` with **{x['node']['points']}** points and **{x['node']['worldRecords']}** World Records\n"
    embed = discord.Embed(title="GTR Rankings", description=stringedrankings, color=nextcord.Color.blue(), timestamp=datetime.datetime.now())
    embed.set_footer(text="last updated")
    await leaderboard.edit(embed=embed, view=fwogutils.views.LButtons(gtrrankings))
    ruusies = fwogutils.getRUusers()
    linkeds = fwogutils.get_linked_users()
    for x in ruusies:
        checkrank = fwogutils.getlinkeduserdata(x)['position']
        userrank = fwogutils.getgtruserrank(linkeds[x]["id"])['rank']
        if checkrank > userrank:
            log(f"{x} ranked up!! sending notif!")
            channel = await bot.fetch_channel(1207401802769633310)
            embed = discord.Embed(title="Ranked up!", description=f"You have ranked up to position **{userrank}** in the GTR rankings!!", color=nextcord.Color.blue())
            embed.set_thumbnail(url="https://cdn.discordapp.com/attachments/1066387605253525595/1202663511252013066/Projet_20240201061441.png?ex=65ce46ad&is=65bbd1ad&hm=42cf06915022254aee2647a53d62d3814c8397d034e8232381c4d6b7e95d299e&")
            await channel.send(f"<@{int(x)}>", embed=embed)
            fwogutils.setlinkedranking(user=x, pos=userrank)
    rdusies = fwogutils.getRDusers()
    for x in rdusies:
        checkrank = fwogutils.getlinkeduserdata(x)['position']
        userrank = fwogutils.getgtruserrank(linkeds[x]["id"])['rank']
        if checkrank < userrank:
            log(f"{x} ranked down :/ sending notif!")
            channel = await bot.fetch_channel(1207401802769633310)
            embed = discord.Embed(title="Ranked down :/",
                                  description=f"You have ranked down to position **{userrank}** in the GTR rankings :/",
                                  color=nextcord.Color.blue())
            embed.set_thumbnail(url="https://cdn.discordapp.com/attachments/1066387605253525595/1202663511252013066/Projet_20240201061441.png?ex=65ce46ad&is=65bbd1ad&hm=42cf06915022254aee2647a53d62d3814c8397d034e8232381c4d6b7e95d299e&")
            await channel.send(f"<@{int(x)}>", embed=embed)
            fwogutils.setlinkedranking(user=x, pos=userrank)


@tasks.loop(time=fwogutils.gtrlb_shedule(), reconnect=True)
async def rankings():
    gtrrankings = fwogutils.getgtruserrankings(limit=100, offset=0)
    await rankingsfunc(gtrrankings=gtrrankings)

rankings.start()

@bot.slash_command(name="notif", guild_ids=[1200812715527114824])
async def notif(ctx):
    pass


@notif.subcommand(name="add", description="will notify you for what you select!")
async def notifme(ctx, to: str = nextcord.SlashOption(name="for", description="will notify you for what you select!",
                                                      choices={"GTR Rank up": "RU", "GTR Rank down": "RD",
                                                               "World Record stolen": "WRST"})):
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
            await ctx.send(f"You will now be notified for what you selected!")
        else:
            await ctx.send("You are not linked! use the `/link gtr` command to link your GTR to this server!")
    except Exception as ewwor:
        await ctx.send(fwogutils.errormessage(ewwor))
        log(str(ewwor))


@notif.subcommand(name="remove", description="will stop notifying you for what you select!")
async def notifme(ctx,
                  to: str = nextcord.SlashOption(name="for", description="will stop notifying you for what you select!",
                                                 choices={"GTR Rank up": "RU", "GTR Rank down": "RD",
                                                          "World Record stolen": "WRST"})):
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


async def wrcallback(message=None):
    while True:
        try:
            log('connecting to gtr wss')
            async with websockets.connect("wss://stream.zeepkist-gtr.com/ws") as ws:
                while True:
                    content = json.loads(await ws.recv())
                    wrstusers = fwogutils.getWRSTusers()
                    if str(content['Data']['PreviousUserId']) in wrstusers and content['Data']['PreviousUserId'] != content['Data']['NewUserId'] and content['Type'] == "wr":
                        log("WR is stolen!!")
                        wrstuserinfo = wrstusers[str(content['Data']['PreviousUserId'])]
                        userlink = fwogutils.get_linked_users()[str(wrstuserinfo['discid'])]
                        level = fwogutils.zworp_getlevel(content['Data']['LevelHash'])
                        if level is not False:
                            log("level was not false")
                            prevrec = fwogutils.jsonapi_getrecord(content['Data']['PreviousRecordId'])
                            recordcreated = datetime.datetime.strptime(prevrec["dateCreated"], '%Y-%m-%dT%H:%M:%S.%fZ')
                            timenow = datetime.datetime.now()
                            if timenow.date() == recordcreated.date() and int(recordcreated.timestamp()) + 600 > int(
                                    timenow.timestamp()):
                                log('wr beat before 10 mins, breaking')
                                break
                            prevrec, prevuser = fwogutils.jsonapi_getrecord(content['Data']['PreviousRecordId']), fwogutils.getgtruser(content['Data']["PreviousUserId"])
                            recordcreated = datetime.datetime.strptime(prevrec["dateCreated"], '%Y-%m-%dT%H:%M:%S.%fZ')
                            newrecordcreated = datetime.datetime.strptime(newrec["dateCreated"], '%Y-%m-%dT%H:%M:%S.%fZ')
                            newrec, newuser = fwogutils.jsonapi_getrecord(content['Data']['NewRecordId']), fwogutils.getgtruser(content['Data']['NewUserId'])
                            wrstembed = discord.Embed(title="New World Record!",
                                                      description=f"New World Record on **{level[0]['name']}** by **{level[0]['fileAuthor']}**",
                                                      color=nextcord.Color.blue(),
                                                      url=f"https://steamcommunity.com/sharedfiles/filedetails/?id={level[0]['workshopId']}")
                            wrstembed.set_thumbnail(url="https://cdn.discordapp.com/attachments/1066387605253525595/1202663511252013066/Projet_20240201061441.png?ex=65ce46ad&is=65bbd1ad&hm=42cf06915022254aee2647a53d62d3814c8397d034e8232381c4d6b7e95d299e&")
                            wrstembed.add_field(name="Info",
                                                value=f"Previous time: **{fwogutils.format_time(prevrec['time'])}** by **{prevuser[1]['steamName']}** set <t:{int(recordcreated.timestamp())}:R>\n"
                                                      f"New time: **{fwogutils.format_time(newrec['time'])}** by **{newuser[1]['steamName']}** set <t:{int(newrecordcreated.timestamp())}:R>\n"
                                                      f"Level: [{level[0]['name']} by {level[0]['fileAuthor']}](https://steamcommunity.com/sharedfiles/filedetails/?id={level[0]['workshopId']})")
                            notifchannel = await bot.fetch_channel(1207401802769633310)
                            await notifchannel.send(f"<@{wrstuserinfo['discid']}>", embed=wrstembed)
                            feedchannel = await bot.fetch_channel(1231992230529601647)
                            await feedchannel.send("", embed=wrstembed)
                    else:
                        log("WR getting sent into feed channel")
                        level = fwogutils.zworp_getlevel(content['Data']['LevelHash'])
                        if level is not False:
                            log("level was not false")
                            prevrec, prevuser = fwogutils.jsonapi_getrecord(content['Data']['PreviousRecordId']), fwogutils.getgtruser(content['Data']["PreviousUserId"])
                            newrec, newuser = fwogutils.jsonapi_getrecord(content['Data']['NewRecordId']), fwogutils.getgtruser(content['Data']['NewUserId'])
                            recordcreated = datetime.datetime.strptime(prevrec["dateCreated"], '%Y-%m-%dT%H:%M:%S.%fZ')
                            newrecordcreated = datetime.datetime.strptime(newrec["dateCreated"], '%Y-%m-%dT%H:%M:%S.%fZ')
                            wrstembed = discord.Embed(title="New World Record!",
                                                      description=f"New World Record on **{level[0]['name']}** by **{level[0]['fileAuthor']}**",
                                                      color=nextcord.Color.blue(),
                                                      url=f"https://steamcommunity.com/sharedfiles/filedetails/?id={level[0]['workshopId']}")
                            wrstembed.set_thumbnail(url="https://cdn.discordapp.com/attachments/1066387605253525595/1202663511252013066/Projet_20240201061441.png?ex=65ce46ad&is=65bbd1ad&hm=42cf06915022254aee2647a53d62d3814c8397d034e8232381c4d6b7e95d299e&")
                            wrstembed.add_field(name="Info",
                                                value=f"Previous time: **{fwogutils.format_time(prevrec['time'])}** by **{prevuser[1]['steamName']}** set <t:{int(recordcreated.timestamp())}:R>\n"
                                                      f"New time: **{fwogutils.format_time(newrec['time'])}** by **{newuser[1]['steamName']}** set <t:{int(newrecordcreated.timestamp())}:R>\n"
                                                      f"Level: [{level[0]['name']} by {level[0]['fileAuthor']}](https://steamcommunity.com/sharedfiles/filedetails/?id={level[0]['workshopId']})")
                            feedchannel = await bot.fetch_channel(1231992230529601647)
                            await feedchannel.send("", embed=wrstembed)
        except Exception as ex:
            print(ex)
            log(str(ex))

@get.subcommand(name="hot")
async def gethot(ctx):
    pass


@gethot.subcommand(name="levels", description="Get a playlist of the levels that have been played the most in the past 24 hours!")
async def gethotlvls(ctx, playlistname: str = nextcord.SlashOption(description="The name for the playlist", required=True)):
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
            "levels": levels})
        fwogutils.renamepl(playlistname)
        await ctx.edit(f"Your playlist has been generated!", file=nextcord.File(f"{playlistname}.zeeplist"))
        fwogutils.undorename(playlistname)

@bot.slash_command(name="register", description="Register to play in the Showdown competition!", guild_ids=[1127321762686836798])
async def sd_register(ctx):
    linkeds = fwogutils.get_linked_users()
    user = str(ctx.user.id)
    with open("showdownusers.json", 'r') as read:
        sdusers = json.loads(read.read())
    if int(user) in sdusers['registered_users']:
        await ctx.send("You are already registered!", ephemeral=True)
        return
    if user in linkeds:
        linkeduser = linkeds[user]
        async def btn_yes(ctx: nextcord.Interaction):
            newuser = {"id": linkeduser['id'], "steamId": linkeduser['steamId'], "steamName": linkeduser['steamName'], "discordId": linkeduser['discordId'], "registered": True}
            sdusers["s5"].append(newuser)
            sdusers["registered_users"].append(int(user))
            with open("showdownusers.json", 'w') as write:
                json.dump(sdusers, write, indent=2)
            await ctx.edit(content="Thank you for participating!", view=None)
            await ctx.channel.send(f"{ctx.user.mention} has joined the competition!")
        async def btn_no(ctx: nextcord.Interaction):
            await ctx.edit(content="Alrighty!", view=None)
            return
        agreebtns = nextcord.ui.View(timeout=60)
        btnyes = nextcord.ui.Button(label="Yes", style=nextcord.ButtonStyle.green)
        btnyes.callback = btn_yes
        btnno = nextcord.ui.Button(label="No", style=nextcord.ButtonStyle.red)
        btnno.callback = btn_no
        agreebtns.add_item(btnyes)
        agreebtns.add_item(btnno)
        await ctx.send(f"I have found a steam account by the name of **{linkeduser['steamName']}**\nDo you wish to register?\n\n"
                       f"**By registering you accept that we need to gather your steam ID, your steam Name and your GTR user ID for organizational and technical reasons**", ephemeral=True, view=agreebtns)
    else:
        user = fwogutils.getgtruserv2(discordid=ctx.user.id)
        if user:
            async def btn_yes(ctx: nextcord.Interaction):
                newuser = {"id": user['id'], "steamId": user['steamId'], "steamName": user['steamName'], "discordId": user['discordId'], "registered": True}
                sdusers["s5"].append(newuser)
                sdusers["registered_users"].append(int(ctx.user.id))
                with open("showdownusers.json", 'w') as write:
                    json.dump(sdusers, write, indent=2)
                await ctx.edit(content="Thank you for participating!", view=None)
                await ctx.channel.send(f"{ctx.user.mention} has joined the competition!")
            async def btn_no(ctx: nextcord.Interaction):
                await ctx.edit(content="Alrighty!", view=None)
                return
            agreebtns = nextcord.ui.View(timeout=60)
            btnyes = nextcord.ui.Button(label="Yes", style=nextcord.ButtonStyle.green)
            btnyes.callback = btn_yes
            btnno = nextcord.ui.Button(label="No", style=nextcord.ButtonStyle.red)
            btnno.callback = btn_no
            agreebtns.add_item(btnyes)
            agreebtns.add_item(btnno)
            await ctx.send(f"I have found a steam account by the name of **{user['steamName']}**\nDo you wish to register?\n\n"
                           f"**By registering you accept that we need to gather your steam ID, your steam Name and your GTR user ID for organizational and technical reasons**", ephemeral=True, view=agreebtns)
        else:
            await ctx.send("You do not have your discord linked to GTR! to proceed please go to your mods settings in the game settings, scrolling to the GTR section, in the Discord section press 'link'", ephemeral=True)


@bot.slash_command(name="unregister", description="Unregister from the Showdown Competition", guild_ids=[1127321762686836798])
async def sd_unregister(ctx):
    await ctx.response.defer(ephemeral=True)
    with open("showdownusers.json", 'r') as read:
        sdusers = json.loads(read.read())
    index = 0
    for x in sdusers["registered_users"]:
        if x == ctx.user.id:
            user = sdusers["s5"][index]
            user["registered"] = False
            log(f"popping {ctx.user.id}")
            log(sdusers["s5"].pop(index))
            log(sdusers["registered_users"].pop(index))
            with open("showdownusers.json", 'w') as write:
                json.dump(sdusers, write, indent=2)
            await ctx.followup.send("You have been successfully unregistered!")
            await ctx.channel.send(f"{ctx.user.mention} Has left the competition :/")
            return
        index += 1
    await ctx.followup.send("You arent registered!")


sent = False
conx = nextcord.Interaction


@tasks.loop(seconds=3, minutes=1, reconnect=True)
async def emb():
    global sent, conx
    this = []
    sort = []
    iden = {}
    with open("showdownusers.json", 'r') as read:
        users = json.loads(read.read())["s4"]
        for x in users:
            userpb = json.loads(requests.get(
                f"https://jsonapi.zeepkist-gtr.com/personalbests?filter=and(equals(userId,%27{x['id']}%27),equals(level,%27C1911F2EB2B9787C5592DC48BFEEDE23F70ED169%27))&include=record").text)["included"][0]["attributes"]
            iden[str(userpb['time'])] = x['steamName']
            sort.append(userpb['time'])
        sort.sort()
        for x in sort:
            this.append({"time": str(fwogutils.format_time(x)), "name": iden[str(x)]})
    chan = await bot.fetch_channel(1144730662000136315)
    try:
        # this = json.loads(requests.get("https://zeepkist-showdown-4215308f4ce4.herokuapp.com/api/qualifier").text)['qualifier']
        wr = json.loads(requests.get(
            "https://api.zeepkist-gtr.com/records?Level=C1911F2EB2B9787C5592DC48BFEEDE23F70ED169&ValidOnly=true&Limit=1&Offset=0").text)[
            'records'][0]
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
        for x in this[8:16]:
            embeda.add_field(name=f"{count}. {x['time']}", value=f"by {x['name']}")
            count += 1
        embeda.add_field(name=f"", value=f"")
        for x in this[16:41]:
            embedb.add_field(name=f"{count}. {x['time']}", value=f"by {x['name']}")
            count += 1
        wrembed.add_field(name=f"{format_time(wr['time'])}", value=f"by {wruser['steamName']}")
        if sent:
            await conx.edit(f"# Showdown Qualifier Season 3", embeds=[embed, embeda, embedb, wrembed])
        else:
            conx = await chan.send(f"# Showdown Qualifier Season 3", embeds=[embed, embeda, embedb, wrembed])
            sent = True
    except Exception as ewwor:
        await chan.send(f"an error occurred.\n\n```{ewwor}```")


@bot.command(name="startemb")
async def startemb(ctx):
    if ctx.author.id in [785037540155195424, 257321046611329026]:
        emb.start()


@bot.command(name="stopemb")
async def stopemb(ctx):
    global sent
    if ctx.author.id in [785037540155195424, 257321046611329026]:
        emb.stop()
        sent = False

sentlb = False
conxlb = nextcord.Interaction


@tasks.loop(minutes=5, reconnect=True)
async def lb():
    global sentlb, conxlb, cache
    sdlvls = [{'hash': "10E58AD6D56644967ABC385701D245B1C9D63153", 'name': "Malfunction"},
              {'hash': "E802E67815634AE7CE072B92A48BB34A1DE0E604", 'name': "Breakup"},
              {'hash': "583D91B9454460B062A7D2A9195F812325EAEB87", 'name': "Impact"},
              {'hash': "741A69742F3F6787682B3E79AD4136CD4780BD91", 'name': "Crimson Course"},
              {'hash': "E48EF5181176449F9DBE9F45926CCBFDBD67B0D4", 'name': "Island Serenity"},
              {'hash': "F81CD65D7823A686C476DFFAC3289CF8FD27459E", 'name': "Orange Strands"},
              {'hash': "5BAA18F8423AA864F7CB15E94AF11150E66F7A04", 'name': "Jungle Run"}]
    chan = await bot.fetch_channel(1198606669123424357)
    embed = discord.Embed(title="Showdown Season 3 Levels", description=" ", color=nextcord.Color.purple())
    embeda = discord.Embed(color=nextcord.Color.purple(), description=" ")
    embedb = discord.Embed(color=nextcord.Color.purple(), description=" ")
    embedc = discord.Embed(color=nextcord.Color.purple(), description=" ", timestamp=datetime.datetime.now())
    embedc.set_footer(text="last updated")
    try:
        for x in sdlvls:
            records = json.loads(requests.get(
                f"https://api.zeepkist-gtr.com/records?Level={x['hash']}&ValidOnly=true&Limit=75&Offset=0").text)
            data = {"levelrecs": "", "rcount": 0, "users": []}
            for a in records['records']:
                user = fwogutils.getgtruser(id=a['user'])[1]['steamName']
                if user not in data['users']:
                    data['levelrecs'] += f"1. `{format_time(a['time'])}` by **{user}**\n"
                    data['users'].append(user)
                    data['rcount'] += 1
                    if data["rcount"] == 5:
                        break
            if x['name'] in ['Malfunction', 'Breakup']:
                embed.add_field(name=x['name'], value=data['levelrecs'], inline=True)
            elif x['name'] in ['Impact', 'Crimson Course']:
                embeda.add_field(name=x['name'], value=data['levelrecs'], inline=True)
            elif x['name'] in ['Island Serenity', 'Orange Strands']:
                embedb.add_field(name=x['name'], value=data['levelrecs'], inline=True)
            elif x['name'] in ['Jungle Run']:
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
async def startlb(ctx):
    if ctx.author.id in [785037540155195424, 257321046611329026]:
        lb.start()
    else:
        print("invalid user")


@bot.command(name="stoplb")
async def stoplb(ctx):
    global sentlb
    if ctx.author.id in [785037540155195424, 257321046611329026]:
        lb.stop()
        sentlb = False
    else:
        print("invalid user")

@bot.slash_command("upload")
async def upload(ctx):
    pass

code, author, desc, password = "The code used to import this playlist into zeepkist", "The person who made this playlist", "The description of this playlist", "This password is needed to manage this playlist later on"
@upload.subcommand(name="playlist", description="Upload a playlist to fwogiiedev to be importable via code!")
async def upload_pl(ctx, playlist: nextcord.Attachment):
    if fwogutils.checkzeeplist(playlist.filename):
        def embed():
            embed = discord.Embed(title="Playlist Upload", description="This is where you can edit your playlist before uploading it!", color=nextcord.Color.blue())
            embed.set_thumbnail(url="https://cdn.discordapp.com/attachments/1066387605253525595/1202663511252013066/Projet_20240201061441.png?ex=65ce46ad&is=65bbd1ad&hm=42cf06915022254aee2647a53d62d3814c8397d034e8232381c4d6b7e95d299e&")
            embed.add_field(name="Code (required)", value=code, inline=False)
            embed.add_field(name="Author (required)", value=author, inline=False)
            embed.add_field(name="Description (optional)", value=desc, inline=False)
            embed.add_field(name="Password (required)", value=password, inline=False)
            return embed

        async def set_code(ctx):
            async def modalcallback(ctx):
                global code
                code = txtinput.value
                await ctxe.edit(embed=embed(), view=editbtns)
            modal = nextcord.ui.Modal(title="Set Code", auto_defer=True)
            txtinput = nextcord.ui.TextInput(label="Code", max_length=15, placeholder=code)
            modal.add_item(txtinput)
            modal.callback = modalcallback
            await ctx.response.send_modal(modal)

        async def set_author(ctx):
            async def modalcallback(ctx):
                global author
                author = txtinput.value
                await ctxe.edit(embed=embed(), view=editbtns)

            modal = nextcord.ui.Modal(title="Set Author", auto_defer=True)
            txtinput = nextcord.ui.TextInput(label="Author", max_length=30, placeholder=author)
            modal.add_item(txtinput)
            modal.callback = modalcallback
            await ctx.response.send_modal(modal)
        async def set_desc(ctx):
            async def modalcallback(ctx):
                global desc
                desc = txtinput.value
                await ctxe.edit(embed=embed(), view=editbtns)

            modal = nextcord.ui.Modal(title="Set Description", auto_defer=True)
            txtinput = nextcord.ui.TextInput(label="Description", max_length=256, placeholder=desc)
            modal.add_item(txtinput)
            modal.callback = modalcallback
            await ctx.response.send_modal(modal)
        async def set_psw(ctx):
            async def modalcallback(ctx):
                global password
                password = txtinput.value
                await ctxe.edit(embed=embed(), view=editbtns)

            modal = nextcord.ui.Modal(title="Set Password", auto_defer=True)
            txtinput = nextcord.ui.TextInput(label="Password", max_length=30, placeholder=password)
            modal.add_item(txtinput)
            modal.callback = modalcallback
            await ctx.response.send_modal(modal)
        async def upload(ctx):
            global code, author, password, desc
            await ctx.response.defer()
            if code and author and password:
                pl = json.loads(await playlist.read())
                pl["amountOfLevels"] = len(pl["levels"])
                req = requests.post(f"https://fwogiiedev.com/api/playlists?customcode={code}&author={author}&description={desc}&password={password}", json=pl)
                if req.status_code == 409:
                    await ctx.followup.send("This code already exists, please pick another one!", ephemeral=True)
                    return
                if req.status_code != 200:
                    await ctx.followup.send(f"unexpected error, code: {req.status_code}")
                with open("fwogiiedev.json", 'r') as read:
                    data = json.loads(read.read())
                data[str(ctx.user.id)] = {"code": code, "password": password, "author": author}
                data[author] = {"code": code, "password": password, "author": author}
                with open("fwogiiedev.json", 'w') as write:
                    json.dump(data, write, indent=2)
                await ctx.followup.send(f"All set! You can now share this code: {code}", ephemeral=True)
                code, author, desc, password = "The code used to import this playlist into zeepkist", "The person who made this playlist", "The description of this playlist", "This password is needed to manage this playlist later on"
            else:
                await ctx.followup.send("Missing required Information!", ephemeral=True)

        editbtns = nextcord.ui.View(timeout=120, auto_defer=True)
        setcodebtn = nextcord.ui.Button(label="Set Code", style=nextcord.ButtonStyle.grey)
        setcodebtn.callback = set_code
        editbtns.add_item(setcodebtn)
        setauthorbtn = nextcord.ui.Button(label="Set Author", style=nextcord.ButtonStyle.grey)
        setauthorbtn.callback = set_author
        editbtns.add_item(setauthorbtn)
        setdescbtn = nextcord.ui.Button(label="Set Description", style=nextcord.ButtonStyle.grey)
        setdescbtn.callback = set_desc
        editbtns.add_item(setdescbtn)
        setpswbtn = nextcord.ui.Button(label="Set Password", style=nextcord.ButtonStyle.grey)
        setpswbtn.callback = set_psw
        editbtns.add_item(setpswbtn)
        uploadbtn = nextcord.ui.Button(label="Upload", style=nextcord.ButtonStyle.green)
        uploadbtn.callback = upload
        editbtns.add_item(uploadbtn)
        ctxe = await ctx.send(embed=embed(), view=editbtns, ephemeral=True)
    else:
        await ctx.send("Please attach a valid .zeeplist file", ephemeral=True)

@bot.command()
async def delpl(ctx, plcode: str):
    if ctx.author.id == 785037540155195424:
        req = requests.post(f"https://fwogiiedev.com/api/playlists?customcode={plcode}&delete=True", json={})
        await ctx.send(f"`{req.status_code}` {req.text}")

bot.run(privaat.token)
