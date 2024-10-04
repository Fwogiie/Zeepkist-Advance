from fwogutils import bot, log
import fwogutils
import nextcord
import random
import json

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

print(f"| {__name__} loaded in")