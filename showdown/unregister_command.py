from fwogutils import bot
from fwogutils import log
import json

@bot.slash_command(name="unregister", description="Unregister from the Showdown Competition", guild_ids=[1127321762686836798])
async def sd_unregister(ctx):
    await ctx.response.defer(ephemeral=True)
    with open("../storage/showdownusers.json", 'r') as read:
        sdusers = json.loads(read.read())
    index = 0
    for x in sdusers["registered_users"]:
        if x == ctx.user.id:
            user = sdusers["s5"][index]
            user["registered"] = False
            log(f"popping {ctx.user.id}")
            log(sdusers["s5"].pop(index))
            log(sdusers["registered_users"].pop(index))
            with open("../storage/showdownusers.json", 'w') as write:
                json.dump(sdusers, write, indent=2)
            await ctx.followup.send("You have been successfully unregistered!")
            await ctx.channel.send(f"{ctx.user.mention} Has left the competition :/")
            return
        index += 1
    await ctx.followup.send("You arent registered!")

print(f"| {__name__} loaded in")