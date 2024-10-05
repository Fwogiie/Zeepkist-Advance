import discord
from nextcord.ext import tasks
from fwogutils import bot
import fwogutils
import json
import requests
import nextcord

@tasks.loop(minutes=5)
async def qualifier_lb():
    level, users, records, strlb, embeds, count = {"id": 39381}, [], "", "", [], 1
    with open("storage/showdownusers.json", 'r') as read:
        contents = json.loads(read.read())
        for x in contents['s5']:
            users.append(x['id'])
        levelpbs = json.loads(requests.post(url= "https://graphql.zeepkist-gtr.com", json={"query": "query MyQuery($ids: [Int!], $level: Int) { allPersonalBestGlobals ( filter: { idLevel: { equalTo: $level }, idUser: { in: $ids } } ) { edges { node { id recordByIdRecord { time userByIdUser { steamName } } } } } }", "variables": {"ids": users, "level": level["id"]} }).text)
        print(levelpbs)
        for x in levelpbs["data"]["allPersonalBestGlobals"]["edges"]:
            x = x["node"]["recordByIdRecord"]
            records += f'{fwogutils.format_time(x["time"])}={x["userByIdUser"]["steamName"]}\n'
        sort = records.split("\n")
        sort.sort()
        print(sort)
        for x in sort[1:9]:
            mwah = x.split("=")
            strlb += f"{count}. `{mwah[0]}` by **{mwah[1]}**\n"
            count += 1
        poolone = discord.Embed(title="Pool 1", description=strlb, color=nextcord.Colour.red())
        embeds.append(poolone)
        records, strlb = "", ""
        for x in sort[9:17]:
            mwah = x.split("=")
            strlb += f"{count}. `{mwah[0]}` by **{mwah[1]}**\n"
            count += 1
        pool = discord.Embed(title="Pool 2", description=strlb, color=nextcord.Colour.blue())
        embeds.append(pool)
        records, strlb = "", ""
        for x in sort[17:]:
            mwah = x.split("=")
            strlb += f"{count}. `{mwah[0]}` by **{mwah[1]}**\n"
            count += 1
        subs = discord.Embed(title="Substitutes", description=strlb, color=nextcord.Colour.light_gray())
        embeds.append(subs)
        records, strlb = "", ""
    embed = await bot.get_channel(1198606669123424357).fetch_message(1284247928113729630)
    await embed.edit("# Showdown Qualifier Season 4", embeds=embeds)

print(f"| {__name__} loaded in")