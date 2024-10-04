from fwogutils import bot
from showdown.qualifier_lb import qualifier_lb
from showdown.levels_lbs import showdown_lbs


@bot.command()
async def start(ctx, lb: str):
    if ctx.author.id in [257321046611329026, 785037540155195424, 106800154664792064, 483611064974704653, 403942829656899587]:
        if lb == "quali":
            qualifier_lb.start()
            await ctx.send("started :3")
        if lb == "lbs":
            showdown_lbs.start()
            await ctx.send("started :3")
    else:
        await ctx.send("You do not have the permissions to use this command :3")

@bot.command()
async def stop(ctx, lb: str):
    if ctx.author.id in [257321046611329026, 785037540155195424, 106800154664792064, 483611064974704653, 403942829656899587]:
        if lb == "quali":
            qualifier_lb.stop()
            await ctx.send("stopped :3")
        if lb == "lbs":
            showdown_lbs.stop()
            await ctx.send("stopped :3")
    else:
        await ctx.send("You do not have the permissions to use this command :3")

print(f"| {__name__} loaded in")