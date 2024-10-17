from fwogutils import bot, log
import fwogutils
import nextcord
from nextcord.ext import commands

@bot.slash_command(name="verify", description="Verify that you are not a bot!", guild_ids=[1200812715527114824])
async def verify(ctx):
    log(f"called by user: {ctx.user} ({ctx.user.id})")
    if ctx.guild.get_role(1201928108769554442) not in ctx.user.roles:
        gtrcheck = fwogutils.getgtruser(discid=ctx.user.id)
        if gtrcheck[0]:
            log(f"gtrcheck index 0 returned true")

            class YesOrNoButtons(nextcord.ui.View):
                @nextcord.ui.button(label="Yes", style=nextcord.ButtonStyle.green)
                async def yes(self, button: nextcord.Button, ctx: nextcord.Interaction):
                    try:
                        self.stop()
                        fwogutils.addgtruser(str(ctx.user.id), gtrcheck[1])
                        await ctx.user.add_roles(ctx.guild.get_role(1201928108769554442))
                        log(f"verified user {ctx.user} ({ctx.user.id}), also accepted to link their GTR :3")
                        await ctx.send("You have been verified!", ephemeral=True)
                    except Exception as ewwor:
                        await ctx.send(fwogutils.errormessage(ewwor), ephemeral=True)

                @nextcord.ui.button(label="No", style=nextcord.ButtonStyle.red)
                async def no(self, button: nextcord.Button, ctx: nextcord.Interaction):
                    self.stop()
                    await ctx.user.add_roles(ctx.guild.get_role(1201928108769554442))
                    log(f"verified user {ctx.user} ({ctx.user.id}) without linkage to GTR")
                    await ctx.send("You have been verified!", ephemeral=True)

            await ctx.send(
                f"Hello there! i have detected that you have a GTR account by the name of **{gtrcheck[1]['steamName']}**,"
                f" do you wish to link it to this discord? this will only be used in this discord.",
                view=YesOrNoButtons(), ephemeral=True)
        else:
            await ctx.user.add_roles(ctx.guild.get_role(1201928108769554442))
            log(f"verified user {ctx.user} ({ctx.user.id})")
            await ctx.send("you have been verified!", ephemeral=True)
    else:
        await ctx.send("you are already verified!", ephemeral=True)


class Cog(commands.Cog):
    @commands.Cog.listener()
    async def on_message(self, ctx):
        if ctx.channel.id == 1201928657703292959 and ctx.author.id not in [785037540155195424, bot.user.id]:
            await ctx.delete()
        if ctx.channel.id == 1296544182051274852:
            await ctx.add_reaction("✅")

bot.add_cog(Cog())

print(f"| {__name__} loaded in")