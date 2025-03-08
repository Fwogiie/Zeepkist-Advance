import nextcord
import fwogutils
from fwogutils import bot
from nextcord.ext import tasks

notif_channel = 1207401802769633310
notif_test_channel = 1347885622559375460

async def startup_logic():
    await rankings_checker()
    rankings_notifier.start()

@tasks.loop(time=fwogutils.gtrlb_shedule())
async def rankings_notifier():
    await rankings_checker()

async def rankings_checker():
    notifusers = fwogutils.getnotifusers()
    for user in notifusers["RDusers"]:
        userupdatedpos = fwogutils.getusergtrposition(user)
        userunupdatedpos = fwogutils.getstoreduser(user)["userdata"]["position"]
        if userunupdatedpos < userupdatedpos:
            await rankdown_handler(userupdatedpos, userunupdatedpos, user)
            fwogutils.updateuserposition(user, userupdatedpos)
    for user in notifusers["RUusers"]:
        userupdatedpos = fwogutils.getusergtrposition(user)
        userunupdatedpos = fwogutils.getstoreduser(user)["userdata"]["position"]
        if userunupdatedpos > userupdatedpos:
            await rankup_handler(userupdatedpos, userunupdatedpos, user)
            fwogutils.updateuserposition(user, userupdatedpos)


async def rankdown_handler(updatedpos: int, unupdatedpos: int, user: str):
    embed = nextcord.Embed(title="Ranked down :/",
                           description=f"You have ranked down from Position {unupdatedpos} to {updatedpos} in the GTR rankings!",
                           color=nextcord.Color.blue())
    embed.set_thumbnail("https://cdn.discordapp.com/attachments/1066387605253525595/1202663511252013066/Projet_20240201061441.png")
    if fwogutils.is_test_build():
        await bot.get_channel(notif_test_channel).send(f"<@{user}>", embed=embed)
    else:
        await bot.get_channel(notif_channel).send(f"<@{user}>", embed=embed)

async def rankup_handler(updatedpos: int, unupdatedpos: int, user: str):
    embed = nextcord.Embed(title="Ranked up!",
                           description=f"You have ranked up from Position {unupdatedpos} to {updatedpos} in the GTR rankings!",
                           color=nextcord.Color.blue())
    embed.set_thumbnail("https://cdn.discordapp.com/attachments/1066387605253525595/1202663511252013066/Projet_20240201061441.png")
    if fwogutils.is_test_build():
        await bot.get_channel(notif_test_channel).send(f"<@{user}>", embed=embed)
    else:
        await bot.get_channel(notif_channel).send(f"<@{user}>", embed=embed)