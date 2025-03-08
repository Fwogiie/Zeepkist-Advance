from datetime import datetime
import discord
import nextcord
import fwogutils
from fwogutils import bot, log
from nextcord.ext import tasks
from rankings import rankings_view

main_leaderboards = ["1203645881279184948-1203656747294654555"]
test_leaderboard = "1347885622559375460-1347886582140768319"

async def startup_handler():
    await rankings()
    rankings_updater.start()

@tasks.loop(time=fwogutils.gtrlb_shedule(), reconnect=True)
async def rankings_updater():
    await rankings()

async def rankings():
    log("reach")
    baseranks = ""
    for x in fwogutils.getrankings():
        baseranks += f"{x['rank']}. `{x['steamName']}` with {x['points']} points and {x['worldRecords']} World Records\n"
    embed = discord.Embed(title="GTR Rankings", description=baseranks, timestamp=datetime.now(), color=nextcord.Color.blue())
    embed.set_footer(text="last updated")
    if fwogutils.is_test_build():
        lb = await bot.get_channel(int(test_leaderboard.split("-")[0])).fetch_message(int(test_leaderboard.split("-")[1]))
        await lb.edit(embed=embed, view=rankings_view.LbView())
        return
    for x in main_leaderboards:
        lb = await bot.get_channel(int(x.split("-")[0])).fetch_message(int(x.split("-")[1]))
        await lb.edit(embed=embed, view=rankings_view.LbView())


print(f"| {__name__} loaded in")