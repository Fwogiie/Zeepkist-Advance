from fwogutils import bot, log
import fwogutils.objects
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
        filejson = json.loads(await playlist.read())
        playlist = fwogutils.objects.Playlist()
        playlist.levels = filejson["levels"]
        playlist.name = filejson["name"]
        playlist.shuffle = filejson["shufflePlaylist"]
        playlist.roundlength = filejson["roundLength"]
        await playlist.shuffle_playlist()
        url = await playlist.get_download_url()
        await ctx.send(f"Your playlist is ready! {url}")
    else:
        await ctx.send("Please attach a valid .zeeplist file!")

print(f"| {__name__} loaded in")