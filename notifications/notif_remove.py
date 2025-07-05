import fwogutils
from fwogutils import log
from notifications.base_command import notif
import nextcord

@notif.subcommand(name="remove", description="will stop notifying you for what you select!")
async def notifme(ctx,
                  to: str = nextcord.SlashOption(name="for", description="will stop notifying you for what you select!",
                                                 choices={"GTR Rank up": "RU", "GTR Rank down": "RD",
                                                          "World Record stolen": "WRST"})):
    log(f"reached by {ctx.user} ({ctx.user.id})")
    try:
        if fwogutils.userislinked(ctx.user.id):
            log("user is linked")
            usersettings = fwogutils.getlinkedusersettings(ctx.user.id)
            if usersettings["notifs"][to] is False:
                await ctx.send("This was already disabled!")
                log("setting already disabled, returning")
                return
            log(f"setting {to} to False")
            fwogutils.setlinkedusersetting(setting=to, value=False, user=ctx.user.id)
            user = fwogutils.get_linked_users()[str(ctx.user.id)]
            await ctx.send(f"We will stop to notify you for what you selected!")
        else:
            await ctx.send("You are not linked! use the `/link gtr` command to link your GTR to this server!")
    except Exception as ewwor:
        await ctx.send(fwogutils.errormessage(ewwor))
        log(str(ewwor))

print(f"| {__name__} loaded in")