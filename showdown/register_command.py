from fwogutils import bot
import fwogutils
import nextcord
import json

@bot.slash_command(name="register", description="Register to play in the Showdown competition!", guild_ids=[1127321762686836798])
async def sd_register(ctx):
    linkeds = fwogutils.get_linked_users()
    user = str(ctx.user.id)
    with open("../storage/showdownusers.json", 'r') as read:
        sdusers = json.loads(read.read())
    if int(user) in sdusers['registered_users']:
        await ctx.send("You are already registered!", ephemeral=True)
        return
    if user in linkeds:
        linkeduser = linkeds[user]
        async def btn_yes(ctx: nextcord.Interaction):
            newuser = {"id": linkeduser['id'], "steamId": linkeduser['steamId'], "steamName": linkeduser['steamName'], "discordId": linkeduser['discordId'], "registered": True}
            sdusers["s5"].append(newuser)
            sdusers["registered_users"].append(int(user))
            with open("../storage/showdownusers.json", 'w') as write:
                json.dump(sdusers, write, indent=2)
            await ctx.edit(content="Thank you for participating!", view=None)
            await ctx.channel.send(f"{ctx.user.mention} has joined the competition!")
        async def btn_no(ctx: nextcord.Interaction):
            await ctx.edit(content="Alrighty!", view=None)
            return
        agreebtns = nextcord.ui.View(timeout=60)
        btnyes = nextcord.ui.Button(label="Yes", style=nextcord.ButtonStyle.green)
        btnyes.callback = btn_yes
        btnno = nextcord.ui.Button(label="No", style=nextcord.ButtonStyle.red)
        btnno.callback = btn_no
        agreebtns.add_item(btnyes)
        agreebtns.add_item(btnno)
        await ctx.send(f"I have found a steam account by the name of **{linkeduser['steamName']}**\nDo you wish to register?\n\n"
                       f"**By registering you accept that we need to gather your steam ID, your steam Name and your GTR user ID for organizational and technical reasons**", ephemeral=True, view=agreebtns)
    else:
        user = fwogutils.getgtruserv2(discordid=ctx.user.id)
        if user:
            async def btn_yes(ctx: nextcord.Interaction):
                newuser = {"id": user['id'], "steamId": user['steamId'], "steamName": user['steamName'], "discordId": user['discordId'], "registered": True}
                sdusers["s5"].append(newuser)
                sdusers["registered_users"].append(int(ctx.user.id))
                with open("../storage/showdownusers.json", 'w') as write:
                    json.dump(sdusers, write, indent=2)
                await ctx.edit(content="Thank you for participating!", view=None)
                await ctx.channel.send(f"{ctx.user.mention} has joined the competition!")
            async def btn_no(ctx: nextcord.Interaction):
                await ctx.edit(content="Alrighty!", view=None)
                return
            agreebtns = nextcord.ui.View(timeout=60)
            btnyes = nextcord.ui.Button(label="Yes", style=nextcord.ButtonStyle.green)
            btnyes.callback = btn_yes
            btnno = nextcord.ui.Button(label="No", style=nextcord.ButtonStyle.red)
            btnno.callback = btn_no
            agreebtns.add_item(btnyes)
            agreebtns.add_item(btnno)
            await ctx.send(f"I have found a steam account by the name of **{user['steamName']}**\nDo you wish to register?\n\n"
                           f"**By registering you accept that we need to gather your steam ID, your steam Name and your GTR user ID for organizational and technical reasons**", ephemeral=True, view=agreebtns)
        else:
            await ctx.send("You do not have your discord linked to GTR! to proceed please go to your mods settings in the game settings, scrolling to the GTR section, in the Discord section press 'link'", ephemeral=True)

print(f"| {__name__} loaded in")