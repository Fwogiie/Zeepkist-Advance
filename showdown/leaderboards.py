import json
from datetime import datetime
import nextcord
import requests
from nextcord.ext import tasks
import fwogutils
from fwogutils import bot, log, queries
import time

async def startup_logic():
    log("Showdown Leaderboards statup logic has been called.")
    quali_leaderboard.start()

# quai leaderboards updating
@tasks.loop(minutes=5, reconnect=True)
async def quali_leaderboard():
    with open("showdown/storage.json", 'r') as read:
        stored = json.loads(read.read())
    if stored["update?"]:
        await update_qualifier()
    return

async def update_qualifier():
    log("Qualifier leaderboard updating...")
    with open("showdown/storage.json", "r") as read:
        storage = json.loads(read.read())
    req = requests.post(queries.post_url,
                        json={"query": queries.get_user_pb_by_id, "variables": {"in": storage["regUsersById"], "idLevel": storage["quali"]["id"]}})
    resp = json.loads(req.text)
    print(resp)
    count, records, poolonerecords, pooltworecords, substitutesrecords = 1, [], "", "", ""
    for record in resp["data"]["allUsers"]["nodes"]:
        if record["recordsByIdUser"]["edges"]:
            record, user = record["recordsByIdUser"]["edges"][0]["node"], record["recordsByIdUser"]["edges"][0]["node"]["userByIdUser"]["steamName"]
            records.append(f"{record['time']}:{user}")
    records.sort()
    print(records)
    for x in records:
        recordtime, user = x.split(":")[0], x.split(":")[1]
        if count < 9:
            log("reach 1st check")
            poolonerecords += f"{count}. `{fwogutils.format_time(float(recordtime))}` by **{user}**\n"
            count += 1
        elif 8 < count < 17:
            log("reach 2nd check")
            pooltworecords += f"{count}. `{fwogutils.format_time(float(recordtime))}` by **{user}**\n"
            count += 1
        elif count > 16:
            log("reach 3rd check")
            substitutesrecords += f"{count}. `{fwogutils.format_time(float(recordtime))}` by **{user}**\n"
            count += 1
    pooloneembed = nextcord.Embed(title="Pool 1", description=poolonerecords, color=nextcord.Color.red())
    pooltwoembed = nextcord.Embed(title="Pool 2", description=pooltworecords, color=nextcord.Color.blue())
    substitutesembed = nextcord.Embed(title="Substitutes", description=substitutesrecords, color=nextcord.Color.light_gray())
    channel = bot.get_channel(storage["qualiLb"]["channel"])
    message = await channel.fetch_message(storage["qualiLb"]["message"])
    await message.edit(embeds=[pooloneembed, pooltwoembed, substitutesembed])
