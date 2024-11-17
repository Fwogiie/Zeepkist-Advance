from fwogutils import bot, log, objects, views
import json
import nextcord
import os

@bot.slash_command(name="reverse")
async def rev(ctx):
    pass


@rev.subcommand(name="playlist", description="Reverse a playlist!")
async def revpl(ctx, playlist: nextcord.Attachment = nextcord.SlashOption(description="The playlist to reverse.", required=True)):
    log(f"reached by {ctx.user} ({ctx.user.id}) with playlist name: {playlist.filename}")
    if playlist.filename.split(".")[1:][0] == "zeeplist":
        ctx, given_pl = await ctx.send("processing", ephemeral=True), objects.Playlist(json=json.loads(await playlist.read()))
        new_pl = objects.Playlist(name=given_pl.name, roundlength=given_pl.roundlength, shuffle=given_pl.shuffle)
        new_pl.levels = given_pl.levels.reverse()
        await ctx.edit(f"Your playlist named **{new_pl.name}** with **{new_pl.level_count}** levels has been reversed!",
                       view=views.DownloadPlaylist(download_url=new_pl.get_download_url()))
    else:
        await ctx.send("Please attach a valid .zeeplist file!", ephemeral=True)

print(f"| {__name__} loaded in")