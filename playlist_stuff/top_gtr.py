import json
from fwogutils import objects, views
import nextcord.ui
import requests
import fwogutils
from fwogutils import bot, log
from fwogutils.queries import post_url, top_gtr

getter_messages = ["1305497165128536095,1305497713579917392", "1307802539789647962,1307802618055229451"]
getter_test = "1347885622559375460,1391043187920867339"
embed = nextcord.Embed(title="Top GTR", description="Get a playlist of the levels worth the most points in GTR!", color=nextcord.Color.blue())

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

class DownloadButton(nextcord.ui.View):
    def __init__(self):
        super().__init__(timeout=None, auto_defer=True)
        modal = nextcord.ui.Modal(title="Top GTR")
        self.textinput = nextcord.ui.TextInput(label="Amount of levels (max 1000)", max_length=4)
        modal.add_item(self.textinput)
        modal.callback = self.modal_callback
        self.modal = modal

    @nextcord.ui.button(label="Get Playlist", style=nextcord.ButtonStyle.green)
    async def button_callback(self, button, ctx):
        await ctx.response.send_modal(self.modal)

    async def modal_callback(self, ctx):
        amount = int(self.textinput.value)
        if amount > 1000:
            await ctx.send("Level amount too high! Please try again!", ephemeral=True)
            return
        ctx = await ctx.send("Processing! This shouldn't take more than 1 minute!", ephemeral=True)
        reqs = []
        if amount <= 100:
            reqs.append(requests.post(post_url, json={"query": top_gtr, "variables": {"first": amount}}))
        else:
            numdiv100 = range(int(amount / 100))
            for x in numdiv100:
                reqs.append(requests.post(post_url, json={"query": top_gtr, "variables": {"first": 100, "offset": x*100}}))
            reqs.append(requests.post(post_url, json={"query": top_gtr, "variables": {"first": amount-len(numdiv100)*100, "offset": len(numdiv100)*100}}))
        playlist = fwogutils.objects.Playlist(name=f"top {amount} GTR")
        for req in reqs:
            if req.status_code != 200:
                log("something other than 200 was returned")
                await ctx.edit(f"Error Occurred!\nError: `query 'top_gtr' returned unexpected status code: {req.status_code}. {req.text}`")
            else:
                log(f"200 OK, continuing")
                levels = json.loads(req.text)["data"]["levelPoints"]["nodes"]
                print(levels)
                for x in levels:
                    try:
                        x = x["level"]["levelItems"]["nodes"][0]
                    except IndexError:
                        log("a level failed.")
                        continue
                    playlist.add_level(x["fileUid"],x["workshopId"],x["name"],x["fileAuthor"])
        await ctx.edit(content="", view=fwogutils.views.DownloadPlaylist(await playlist.get_download_url(), playlist), embed=playlist.embed)




print(f"| {__name__} loaded in")