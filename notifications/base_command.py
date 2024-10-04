from fwogutils import bot

@bot.slash_command(name="notif", guild_ids=[1200812715527114824])
async def notif(ctx):
    pass

print(f"| {__name__} loaded in")