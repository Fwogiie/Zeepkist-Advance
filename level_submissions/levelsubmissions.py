from fwogutils import bot, log
import re
import requests
import json
from nextcord.ext import commands


class LevelSubmissionsHandler(commands.Cog):

    def  __init__(self):
        self.bot = bot

    @commands.Cog.listener()
    async def on_message(self, message):
        workshop_urls = re.findall("https://steamcommunity\.com/sharedfiles/filedetails/\?id=\d+", message.content)
        if not workshop_urls:
            return
        else:
            await self.submissionhandler(workshop_urls, message.channel.id)

    async def submissionhandler(self, workshop_urls: list, channel: int):
        gamelevels = []
        for x in workshop_urls:
            levelrequest = requests.post("https://graphql.zeepkist-gtr.com",
            json={"query": "query MyQuery($level: BigFloat) {allLevelItems(filter: {workshopId: {equalTo: $level}}) {edges{node { id name fileUid fileAuthor deleted workshopId}}}}",
                  "variables": {"level": int(x.split('?id=')[1])}})
            if levelrequest.status_code != 200:
                log(f"Something went wrong in submissionhandler (POST request related :3) code: {levelrequest.status_code}: {levelrequest.text}")
                return
            else:
                level = json.loads(levelrequest.text)
                level = level["data"]["allLevelItems"]["edges"][0]["node"]
                if level["deleted"] is True:
                    return
                gamelevels.append({"UID": level['fileUid'], "WorkshopID": level['workshopId'], "Name": level['name'], "Author": level['fileAuthor']})
        requests.post("https://fwogiiedev.com/api/levelsubmissions", json={"levels": gamelevels, "channel": str(channel)})

@bot.message_command(name="resubmit-level")
async def resub_level(ctx, message):
    workshop_urls = re.findall("https://steamcommunity\.com/sharedfiles/filedetails/\?id=\d+", message.content)
    if not workshop_urls:
        return
    else:
        await ctx.response.defer(ephemeral=True)
        await LevelSubmissionsHandler.submissionhandler(LevelSubmissionsHandler(), workshop_urls=workshop_urls, channel=message.channel.id)
        await ctx.followup.send("Successfully Submitted the Level(s)")

bot.add_cog(LevelSubmissionsHandler())
print(f"| {__name__} loaded in")