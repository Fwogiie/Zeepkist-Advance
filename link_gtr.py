from fwogutils import bot, log
import fwogutils
import nextcord

@bot.slash_command(name="link", guild_ids=[1200812715527114824])
async def link(ctx):
    pass


@link.subcommand(name="gtr", description="Link your GTR to this server!")
async def linkgtr(ctx):
    log(f"reached by {ctx.user} ({ctx.user.id})")
    gtrcheck = fwogutils.getgtruser(discid=ctx.user.id)
    if gtrcheck[0]:
        log(f"gtrcheck index 0 returned true")

        class YesOrNoButtons(nextcord.ui.View):
            @nextcord.ui.button(label="Yes", style=nextcord.ButtonStyle.green)
            async def yes(self, button: nextcord.Button, ctx: nextcord.Interaction):
                try:
                    self.stop()
                    fwogutils.addgtruser(str(ctx.user.id), gtrcheck[1])
                    await ctx.send("You have been linked!", ephemeral=True)
                except Exception as ewwor:
                    await ctx.send(fwogutils.errormessage(ewwor), ephemeral=True)

            @nextcord.ui.button(label="Cancel", style=nextcord.ButtonStyle.red)
            async def no(self, button: nextcord.Button, ctx: nextcord.Interaction):
                self.stop()
                await ctx.send("cancelled!", ephemeral=True)

        await ctx.send(f"i have detected a GTR account by the name of **{gtrcheck[1]['steamName']}**, do you wish to link it?",
            view=YesOrNoButtons(), ephemeral=True)
    else:
        await ctx.send("I did not find any discord linkage, Please link your discord to your GTR by reproducing the following steps in-game:\n"
                       "`Settings -> Mods -> Scroll to GTR -> In the 'discord' section, Press 'Link'`", ephemeral=True)

print(f"| {__name__} loaded in")