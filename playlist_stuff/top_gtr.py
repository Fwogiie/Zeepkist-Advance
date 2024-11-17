import json
from fwogutils import objects, views
import discord
import nextcord.ui
import requests
import fwogutils
from fwogutils import bot, log
from fwogutils.queries import post_url, top_gtr

getter_messages = ["1305497165128536095,1305497713579917392", "1306295442828689478,1306295591705514077"]
getter_test = "1200814236499189842,1305507941750673459"
embed = discord.Embed(title="Top GTR", description="Get a playlist of the levels worth the most points in GTR!", color=nextcord.Color.blue())

async def bot_startup_handler():
    if fwogutils.is_test_build():
        log("Test build detected, updating test getter")
        channel, message = int(getter_test.split(",")[0]), int(getter_test.split(",")[1])
        await bot.get_channel(channel).get_partial_message(message).edit(embed=embed, view=DownloadButton())
    else:
        log("doing base top getter")
        for x in getter_messages:
            channel, message = int(x.split(",")[0]), int(x.split(",")[1])
            await bot.get_channel(channel).get_partial_message(message).edit(embed=embed, view=DownloadButton())

textinput = nextcord.TextInput
class DownloadButton(nextcord.ui.View):
    def __init__(self):
        super().__init__(timeout=None, auto_defer=True)

    def modal(self):
        global textinput
        modal = nextcord.ui.Modal(title="Top GTR")
        textinput = nextcord.ui.TextInput(label="Amount of levels (max 500)", max_length=3)
        modal.add_item(textinput)
        modal.callback = self.modal_callback
        return modal

    @nextcord.ui.button(label="Get Playlist", style=nextcord.ButtonStyle.green)
    async def button_callback(self, button, ctx):
        await ctx.response.send_modal(self.modal())

    async def modal_callback(self, ctx):
        amount = int(textinput.value)
        if amount > 500:
            await ctx.send("Level amount too high! Please try again!", ephemeral=True)
            return
        else:
            ctx = await ctx.send("Processing! This shouldn't take more than 20 seconds!", ephemeral=True)
            req = requests.post(post_url, json={"query": top_gtr, "variables": {"first": amount}})
            if req.status_code != 200:
                log("something other than 200 was returned")
                await ctx.send(f"Error Occurred!\nError: `query 'top_gtr' returned unexpected status code: {req.status_code}. {req.text}`")
            else:
                log(f"200 OK, continuing")
                playlist = fwogutils.objects.Playlist(name=f"top {amount} GTR")
                levels = json.loads(req.text)["data"]["allLevelPoints"]["nodes"]
                for x in levels:
                    try:
                        x = x["levelByIdLevel"]["levelItemsByIdLevel"]["nodes"][0]
                    except IndexError:
                        log("a level failed.")
                    playlist.add_level(x["fileUid"],x["workshopId"],x["name"],x["fileAuthor"])
                embed = discord.Embed(title="Playlist", description="Your Playlist is ready!", color=nextcord.Color.blue())
                embed.add_field(name="Playlist:", value=f"Name: {playlist.name}\n"
                                                        f"Round Length: {fwogutils.format_time(playlist.roundlength)[:5]}\n"
                                                        f"Shuffle: {playlist.shuffle}\nAmount of Levels: {playlist.level_count}")
                view = fwogutils.views.DownloadPlaylist(await playlist.get_download_url())
                await view.hai()
                await ctx.edit(content="", view=view, embed=embed)




print(f"| {__name__} loaded in")