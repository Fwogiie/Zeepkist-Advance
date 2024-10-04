from fwogutils import bot, log
import nextcord
import fwogutils
import os
import json

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
            with open("../storage/playlist.zeeplist", 'w') as f:
                json.dump(plbr, f, indent=2)
            os.rename("../storage/playlist.zeeplist", f"{name}.zeeplist")
            await ctx.send('The playlist has been generated.'
                           r' To import the playlist into the host controls simply drag the file below into this specific directory: `%userprofile%\AppData\Roaming\Zeepkist\Playlists`.'
                           ' to easily access this directory: (for windows only) press Win+R and paste the directory in the text box.',
                           file=nextcord.File(f'{name}.zeeplist'))
            os.rename(f"{name}.zeeplist", "../storage/playlist.zeeplist")
        else:
            await ctx.send(f"please attach a valid .zeeplist file")
    except Exception as ewwor:
        log(str(ewwor))
        await ctx.user(fwogutils.errormessage(ewwor))

print(f"| {__name__} loaded in")