from fwogutils import bot, log
import fwogutils.views
import fwogutils
import discord
import datetime
import nextcord

async def rankingsfunc(gtrrankings):
    global leaderboards
    leaderboard = await bot.get_channel(1203645881279184948).fetch_message(leaderboards['rankings'])
    stringedrankings = ""
    for x in gtrrankings[:20]:
        stringedrankings += f"{x['node']['rank']}. `{x['node']['userByIdUser']['steamName']}` with **{x['node']['points']}** points and **{x['node']['worldRecords']}** World Records\n"
    embed = discord.Embed(title="GTR Rankings", description=stringedrankings, color=nextcord.Color.blue(), timestamp=datetime.datetime.now())
    embed.set_footer(text="last updated")
    await leaderboard.edit(embed=embed, view=fwogutils.views.LButtons(gtrrankings))
    ruusies = fwogutils.getRUusers()
    linkeds = fwogutils.get_linked_users()
    for x in ruusies:
        checkrank = fwogutils.getlinkeduserdata(x)['position']
        userrank = fwogutils.getgtruserrank(linkeds[x]["id"])['rank']
        if checkrank > userrank:
            log(f"{x} ranked up!! sending notif!")
            channel = await bot.fetch_channel(1207401802769633310)
            embed = discord.Embed(title="Ranked up!", description=f"You have ranked up to position **{userrank}** in the GTR rankings!!", color=nextcord.Color.blue())
            embed.set_thumbnail(url="https://cdn.discordapp.com/attachments/1066387605253525595/1202663511252013066/Projet_20240201061441.png?ex=65ce46ad&is=65bbd1ad&hm=42cf06915022254aee2647a53d62d3814c8397d034e8232381c4d6b7e95d299e&")
            await channel.send(f"<@{int(x)}>", embed=embed)
            fwogutils.setlinkedranking(user=x, pos=userrank)
    rdusies = fwogutils.getRDusers()
    for x in rdusies:
        checkrank = fwogutils.getlinkeduserdata(x)['position']
        userrank = fwogutils.getgtruserrank(linkeds[x]["id"])['rank']
        if checkrank < userrank:
            log(f"{x} ranked down :/ sending notif!")
            channel = await bot.fetch_channel(1207401802769633310)
            embed = discord.Embed(title="Ranked down :/",
                                  description=f"You have ranked down to position **{userrank}** in the GTR rankings :/",
                                  color=nextcord.Color.blue())
            embed.set_thumbnail(url="https://cdn.discordapp.com/attachments/1066387605253525595/1202663511252013066/Projet_20240201061441.png?ex=65ce46ad&is=65bbd1ad&hm=42cf06915022254aee2647a53d62d3814c8397d034e8232381c4d6b7e95d299e&")
            await channel.send(f"<@{int(x)}>", embed=embed)
            fwogutils.setlinkedranking(user=x, pos=userrank)

print(f"| {__name__} loaded in")