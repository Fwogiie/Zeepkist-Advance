from fwogutils import bot, log
import json
import nextcord
import os

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
        with open("../storage/playlist.zeeplist", 'w') as f:
            json.dump(pl, f, indent=2)
        os.rename("../storage/playlist.zeeplist", f"{name}.zeeplist")
        await ctx.edit("Your playlist has been reversed!", file=nextcord.File(f"{name}.zeeplist"))
        os.rename(f"{name}.zeeplist", "../storage/playlist.zeeplist")
    else:
        await ctx.send("Please attach a valid .zeeplist file!")

print(f"| {__name__} loaded in")