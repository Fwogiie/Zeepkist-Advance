from nextcord.ext import tasks
from rankings.rankings_handler import rankingsfunc
import fwogutils


@tasks.loop(time=fwogutils.gtrlb_shedule(), reconnect=True)
async def rankings():
    gtrrankings = fwogutils.getgtruserrankings(limit=100, offset=0)
    await rankingsfunc(gtrrankings=gtrrankings)

rankings.start()

print(f"| {__name__} loaded in")