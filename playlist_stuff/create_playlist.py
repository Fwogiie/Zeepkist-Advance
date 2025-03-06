from fwogutils import bot, log, post_url
import nextcord
import re
import json
import fwogutils
import requests
import random
import fwogutils.views
from fwogutils.queries import levels_from_ids


@bot.message_command(name="create-playlist")
async def create_pl(ctx, msg: nextcord.Message):
    workshopids = []
    async for x in msg.channel.history(limit=500):
        urls = re.findall("https://steamcommunity\.com/sharedfiles/filedetails/\?id=\d+", x.content)
        if not urls:
            # Stop the loop once the iteration iterates the message the command was called on, Because that's how the command is supposed to work :3
            if x.id == msg.id:
                break
            # Continue to the next iteration, cause the message that was just parsed did not contain a submission, saves us going through a loop when it's not needed
            continue
        for url in urls:
            workshopids.append(str(url).split("?id=")[1])
        # Stop the loop once the iteration iterates the message the command was called on, Because that's how the command is supposed to work :3
        if x.id == msg.id:
            break
    # Check if Playlist would be empty, to save Processing resources
    if not workshopids:
        await ctx.send("Your Playlist would be Empty, So i will not be making it!", ephemeral=True)
        return
    # Reverse the IDs because submissions are always from oldest to newest, and reversing the list makes that happen
    workshopids.reverse()
    request = requests.post(post_url, json=levels_from_ids)
    # Check if the request returned unexpected status code, because process feedback is always nice :3
    if request.status_code != 200:
        log(f"Unexpected status code: {request.status_code}: {request.text}")
        await ctx.send(f"Unexpected Status code during Query 'levels_from_ids': {request.status_code}\nIf this happens again, please report this in the Zeepkist Modding discord!")
        return
    returnedlevels = json.loads(request.text)
    # Check for level packs
    for level in returnedlevels["data"]["allLevelItems"]["edges"]:
        level = level["node"]
        if level["deleted"] is True:
            continue



print(f"| {__name__} loaded in")