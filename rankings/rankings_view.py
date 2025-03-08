import nextcord.ui

import fwogutils


class LbView(nextcord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @nextcord.ui.button(label="View more", style=nextcord.ButtonStyle.grey)
    async def _view_more(self, button, ctx):
        # Variables
        self.count_offset = 0
        self.count_limit = 30
        def do_calc():
            ranks = ""
            for x in fwogutils.getrankings(offset=self.count_offset, limit=self.count_limit):
                ranks += f"{x['rank']}. `{x['steamName']}` with {x['points']} points and {x['worldRecords']} World Records\n"
            return ranks
        async def button_next_callback(ctx):
            self.count_offset += 30
            await self.more_view.edit(embed=nextcord.Embed(title=None, description=do_calc(), color=nextcord.Color.blue()))
        async def button_prev_callback(ctx):
            self.count_offset -= 30
            await self.more_view.edit(embed=nextcord.Embed(title=None, description=do_calc(), color=nextcord.Color.blue()))
        # Page buttons
        view = nextcord.ui.View(timeout=None)
        buttonprev = nextcord.ui.Button(label="<")
        buttonnext = nextcord.ui.Button(label=">")
        buttonprev.callback = button_prev_callback
        buttonnext.callback = button_next_callback
        view.add_item(buttonprev)
        view.add_item(buttonnext)
        self.more_view = await ctx.send(embed=nextcord.Embed(title=None, description=do_calc(), color=nextcord.Color.blue()), ephemeral=True, view=view)

    @nextcord.ui.button(label="My rank", style=nextcord.ButtonStyle.green)
    async def _my_rank(self, button, ctx):
        user = fwogutils.getstoreduser(str(ctx.user.id))
        if user:
            ranks = ""
            for x in fwogutils.getrankings(user["userdata"]["position"]-6, 11):
                if x["rank"] == user["userdata"]["position"]:
                    ranks += f"> {x['rank']}. `{x['steamName']}` with {x['points']} points and {x['worldRecords']} World Records\n"
                else:
                    ranks += f"{x['rank']}. `{x['steamName']}` with {x['points']} points and {x['worldRecords']} World Records\n"
            embed = nextcord.Embed(title=None, description=ranks, color=nextcord.Color.blue())
            await ctx.send(embed=embed, ephemeral=True)
        else:
            await ctx.send("You do not have GTR linked! use `/link gtr` to link!", ephemeral=True)


print(f"| {__name__} loaded in")