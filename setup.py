from fwogutils import bot, log
import fwogutils
import json

# Level Submissions
import level_submissions

# Notifications
import notifications

# Playlist Importer
import playlist_importer

# Playlist Stuff
import playlist_stuff

# Rankings
import rankings

# Showdown
import showdown
from rankings.rankings_notifs import rankings_notifier, startup_logic

# Other
log("loading others")
import errors
import link_gtr
import log_command
import verify

# Commands
log("loading commands")

bot.load_extension("onami")

@bot.event
async def on_ready():
    log(f"Loaded up! with bot ID: {bot.user.id}")
    log("initializing startup guilds")
    for guild in bot.guilds:
        log(f"Connected to guild: {guild.name} ({guild.id}) with {guild.member_count} members.")
    log("initializing startup cache for live leaderboards.")
    #await playlist_stuff.top_gtr.bot_startup_handler()
    await rankings.rankings.startup_handler()
    log("assumed to have begun rankings leaderboard!")
    await startup_logic()
