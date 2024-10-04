from fwogutils import log
import fwogutils
import nextcord
from notifications.base_command import notif

@notif.subcommand(name="add", description="will notify you for what you select!")
async def notifme(ctx, to: str = nextcord.SlashOption(name="for", description="will notify you for what you select!",
                                                      choices={"GTR Rank up": "RU", "GTR Rank down": "RD",
                                                               "World Record stolen": "WRST"})):
    log(f"reached by {ctx.user} ({ctx.user.id})")
    try:
        if fwogutils.userislinked(ctx.user.id):
            log("user is linked")
            usersettings = fwogutils.getlinkedusersettings(ctx.user.id)
            if usersettings["notifs"][to] is True:
                await ctx.send("You already enabled this notification!")
                log("setting already enabled, returning")
                return
            log(f"setting {to} to True")
            fwogutils.setlinkedusersetting(setting=to, value=True, user=ctx.user.id)
            await ctx.send(f"You will now be notified for what you selected!")
        else:
            await ctx.send("You are not linked! use the `/link gtr` command to link your GTR to this server!")
    except Exception as ewwor:
        await ctx.send(fwogutils.errormessage(ewwor))
        log(str(ewwor))

print(f"| {__name__} loaded in")