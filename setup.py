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

# Other
log("loading others")
import errors
import link_gtr
import log_command
import verify

# Commands
log("loading commands")
import commands.get

bot.load_extension("onami")

@bot.event
async def on_ready():
    global submissionschannels, leaderboards
    log(f"Loaded up! with bot ID: {bot.user.id}")
    log("initializing startup guilds")
    for guild in bot.guilds:
        log(f"Connected to guild: {guild.name} ({guild.id}) with {guild.member_count} members.")
    log("initializing startup cache for live leaderboards.")
    with open("storage/data.json", "r") as f:
        data = json.load(f)
        rankings.rankings_handler.leaderboards = data["leaderboards"]
        log(f"leaderboards cache succeeded.")
        if bot.user.id == 1126430942924386315:
            log("updating the live leaderboards cause of start.")
            await rankings.rankings_handler.rankingsfunc(fwogutils.getgtruserrankings(limit=100, offset=0))
            log("Process done to the GTR rankings leaderboard.")
    if fwogutils.is_test_build():
        await playlist_stuff.top_gtr.bot_startup_handler()