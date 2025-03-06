import nextcord.ui

import fwogutils


class LbView(nextcord.ui.View):
    @nextcord.ui.button(label="View more", style=nextcord.ButtonStyle.grey)
    async def _view_more(self, button, ctx):
        # Variables
        self.count_offset = 0
        self.count_limit = 30
        def do_calc():
            ranks = ""
            for x in fwogutils.getrankings(offset=self.count_offset, limit=self.count_limit):
                ranks += f"{x["rank"]}. `{x['steamName']}` with {x['points']} and {x['worldRecords']} World Records\n"
            return ranks
        async def button_next_callback(ctx):
            self.count_offset += 30
            await self.more_view.edit(embed=nextcord.Embed(title=None, description=do_calc(), color=nextcord.Color.blue()))
        async def button_prev_callback(ctx):
            self.count_offset -= 30
            await self.more_view.edit(embed=nextcord.Embed(title=None, description=do_calc(), color=nextcord.Color.blue()))
        # Page buttons
        view = nextcord.ui.View()
        buttonprev = nextcord.ui.Button(label="<")
        buttonnext = nextcord.ui.Button(label=">")
        buttonprev.callback = button_prev_callback
        buttonnext.callback = button_next_callback
        view.add_item(buttonprev)
        view.add_item(buttonnext)
        self.more_view = await ctx.send(embed=nextcord.Embed(title=None, description=do_calc(), color=nextcord.Color.blue()), ephemeral=True, view=view)


print(f"| {__name__} loaded in")