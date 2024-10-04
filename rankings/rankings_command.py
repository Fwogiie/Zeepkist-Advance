from fwogutils import bot, log
import nextcord
import requests
import discord
import json
import datetime

emb = nextcord.InteractionResponse
page = {"page": 1, "limit": 10, "offset": 0}

@bot.slash_command(name="rankings")
async def rankings(ctx):
    global emb, page
    log(f"called by: {ctx.user}")
    page = {"page": 1, "limit": 10, "offset": 0}

    class Lbpage(nextcord.ui.View):
        def __init__(self):
            super().__init__(timeout=30)
            self.page = page

        @nextcord.ui.button(label="<", style=nextcord.ButtonStyle.blurple)
        async def left(self, ctx: nextcord.Interaction, button: nextcord.Button):
            if self.page['page'] > 1:
                self.page['limit'] -= 10
                self.page['offset'] -= 10
                self.page['page'] -= 1
                lb = json.loads(requests.get( f"https://api.zeepkist-gtr.com/users/rankings?Limit={self.page['limit']}&Offset={self.page['offset']}").text)
                embed = discord.Embed(title="GTR Rankings", color=nextcord.Color.purple(), timestamp=datetime.datetime.now())
                embed = discord.Embed.set_footer(self=embed, text=f"page: {page['page']}, Total amount: {lb['totalAmount']}")
                for x in lb["rankings"]:
                    embed.add_field(name=f"{x['position']}. {x['user']['steamName']}", inline=False,
                                    value=f"World Records: {x['amountOfWorldRecords']}\nScore: {x['score']}")
                await emb.edit(embed=embed, view=Lbpage())

        @nextcord.ui.button(label=">", style=nextcord.ButtonStyle.blurple)
        async def right(self, ctx: nextcord.Interaction, button: nextcord.Button):
            self.page['limit'] += 10
            self.page['offset'] += 10
            self.page['page'] += 1
            lb = json.loads(requests.get(f"https://api.zeepkist-gtr.com/users/rankings?Limit={self.page['limit']}&Offset={self.page['offset']}").text)
            embed = discord.Embed(title="GTR Rankings", color=nextcord.Color.purple(), timestamp=datetime.datetime.now())
            embed = discord.Embed.set_footer(self=embed, text=f"page: {page['page']}, Total amount: {lb['totalAmount']}")
            for x in lb["rankings"]:
                embed.add_field(name=f"{x['position']}. {x['user']['steamName']}", inline=False, value=f"World Records: {x['amountOfWorldRecords']}\nScore: {x['score']}")
            await emb.edit(embed=embed, view=Lbpage())

    lbb = json.loads(requests.get("https://api.zeepkist-gtr.com/users/rankings?Limit=10&Offset=0").text)
    embedd = discord.Embed(title="GTR Rankings", color=nextcord.Color.purple(), timestamp=datetime.datetime.now())
    embedd = discord.Embed.set_footer(self=embedd, text=f"page: {page['page']}, Total amount: {lbb['totalAmount']}")
    for x in lbb["rankings"]:
        embedd.add_field(name=f"{x['position']}. {x['user']['steamName']}", inline=False, value=f"World Records: {x['amountOfWorldRecords']}\nScore: {x['score']}")
    emb = await ctx.send(embed=embedd, view=Lbpage())

print(f"| {__name__} loaded in")