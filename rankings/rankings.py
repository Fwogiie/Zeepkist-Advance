from datetime import datetime
import discord
import nextcord
import fwogutils
from fwogutils import bot, log
from nextcord.ext import tasks
from rankings import rankings_view


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
    lb = await bot.get_channel(1203645881279184948).fetch_message(1203656747294654555)
    await lb.edit(embed=embed, view=rankings_view.LbView())


print(f"| {__name__} loaded in")