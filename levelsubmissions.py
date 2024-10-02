from fwogutils import bot
from fwogutils import log
import re
import requests
import json
import nextcord
from nextcord.ext import commands
from nextcord import slash_command

class LevelSubmissionsHandler(commands.Cog):

    def __init__(self):
        self.bot = bot
        self.workshop_urls = []
        self.channel = int

    @commands.Cog.listener()
    async def on_message(self, message):
        workshop_urls = re.findall("https://steamcommunity\.com/sharedfiles/filedetails/\?id=\d+", message.content)
        if not workshop_urls:
            return
        else:
            self.workshop_urls = workshop_urls
            self.channel = message.channel.id
            await self.submissionhandler()

    async def submissionhandler(self):
        for x in self.workshop_urls:
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
                else:
                    pass
                gamelevel = {"UID": level['fileUid'], "WorkshopID": level['workshopId'], "Name": level['name'], "Author": level['fileAuthor']}
                requests.post("https://fwogiiedev.com/api/levelsubmissions", json={"level": gamelevel, "channel": str(self.channel)})


def setup(bot):
    bot.add_cog(LevelSubmissionsHandler())
    print("Level submissions Cog successfully loaded in :3")