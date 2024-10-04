from nextcord.ext import tasks
import json
import fwogutils
import discord
from fwogutils import bot
import requests

@tasks.loop(minutes=5)
async def showdown_lbs():
    levels, users, records, strlb, embeds = [{"id": 992, "name": "Quasarion"}, {"id": 982, "name": "Stellar Slip"}, {"id": 708, "name": "Signalum"}, {"id": 972, "name": "Derelict Rally"}, {"id": 962, "name": "Broken Dreams"}, {"id": 5119, "name": "Magical Forest"}, {"id": 1242, "name": "Shurima Desert"}], [], "", "", []
    with open("../storage/showdownusers.json", 'r') as read:
        contents = json.loads(read.read())
        for x in contents['s5']:
            users.append(x['id'])
    for level in levels:
        levelpbs = json.loads(requests.post(url="https://graphql.zeepkist-gtr.com", json={
            "query": "query MyQuery($ids: [Int!], $level: Int) { allPersonalBestGlobals ( filter: { idLevel: { equalTo: $level }, idUser: { in: $ids } } ) { edges { node { id recordByIdRecord { time userByIdUser { steamName } } } } } }",
            "variables": {"ids": users, "level": level["id"]}}).text)
        print(levelpbs)
        for x in levelpbs["data"]["allPersonalBestGlobals"]["edges"]:
            x = x["node"]["recordByIdRecord"]
            records += f'{fwogutils.format_time(x["time"])}={x["userByIdUser"]["steamName"]}\n'
        sort = records.split("\n")
        sort.sort()
        print(sort)
        for x in sort[1:]:
            mwah = x.split("=")
            strlb += f"1. `{mwah[0]}` by **{mwah[1]}**\n"
        embeds.append(discord.Embed(title=level["name"], description=strlb, color=nextcord.Colour.purple()))
        records, sort, strlb = "", [], ""
    embed = await bot.get_channel(1198606669123424357).fetch_message(1284251355573129256)
    await embed.edit(embeds=embeds)

print(f"| {__name__} loaded in")