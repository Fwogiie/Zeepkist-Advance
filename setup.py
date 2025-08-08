from fwogutils import bot, log
import fwogutils
import json

# Level Submissions
import level_submissions

# Notifications
import notifications

# Playlist Importer
#import playlist_importer #Obsolete

# Playlist Stuff
import playlist_stuff

# Rankings
import rankings
from rankings.rankings_notifs import rankings_notifier, startup_logic

# Showdown

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
    # Load Playlist generator
    try:
        await playlist_stuff.top_gtr.bot_startup_handler()
    except:
        print("Error occurred loading top GTR playlist generator")
    finally:
        print("Loaded top GTR playlist generator")
    # Load Rankings system
    try:
        await rankings.rankings.startup_handler()
        await startup_logic()
    except:
        print("Error occurred loading the Rankings system")
    finally:
        print("Loaded Rankings system!")