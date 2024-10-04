from fwogutils import bot, log
import nextcord
import fwogutils

@bot.event
async def on_application_command_error(ctx, error):
    log(error)


@bot.event
async def on_command_error(ctx, error):
    log(error)

print(f"| {__name__} loaded in")