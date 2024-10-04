import fwogutils
from fwogutils import bot, log
import discord
import nextcord
import json
import requests

@bot.slash_command("upload")
async def upload(ctx):
    pass

code, author, desc, password = "The code used to import this playlist into zeepkist", "The person who made this playlist", "The description of this playlist", "This password is needed to manage this playlist later on"
@upload.subcommand(name="playlist", description="Upload a playlist to fwogiiedev to be importable via code!")
async def upload_pl(ctx, playlist: nextcord.Attachment):
    if fwogutils.checkzeeplist(playlist.filename):
        def embed():
            embed = discord.Embed(title="Playlist Upload", description="This is where you can edit your playlist before uploading it!", color=nextcord.Color.blue())
            embed.set_thumbnail(url="https://cdn.discordapp.com/attachments/1066387605253525595/1202663511252013066/Projet_20240201061441.png?ex=65ce46ad&is=65bbd1ad&hm=42cf06915022254aee2647a53d62d3814c8397d034e8232381c4d6b7e95d299e&")
            embed.add_field(name="Code (required)", value=code, inline=False)
            embed.add_field(name="Author (required)", value=author, inline=False)
            embed.add_field(name="Description (optional)", value=desc, inline=False)
            embed.add_field(name="Password (required)", value=password, inline=False)
            return embed

        async def set_code(ctx):
            async def modalcallback(ctx):
                global code
                code = txtinput.value
                await ctxe.edit(embed=embed(), view=editbtns)
            modal = nextcord.ui.Modal(title="Set Code", auto_defer=True)
            txtinput = nextcord.ui.TextInput(label="Code", max_length=15, placeholder=code)
            modal.add_item(txtinput)
            modal.callback = modalcallback
            await ctx.response.send_modal(modal)

        async def set_author(ctx):
            async def modalcallback(ctx):
                global author
                author = txtinput.value
                await ctxe.edit(embed=embed(), view=editbtns)

            modal = nextcord.ui.Modal(title="Set Author", auto_defer=True)
            txtinput = nextcord.ui.TextInput(label="Author", max_length=30, placeholder=author)
            modal.add_item(txtinput)
            modal.callback = modalcallback
            await ctx.response.send_modal(modal)
        async def set_desc(ctx):
            async def modalcallback(ctx):
                global desc
                desc = txtinput.value
                await ctxe.edit(embed=embed(), view=editbtns)

            modal = nextcord.ui.Modal(title="Set Description", auto_defer=True)
            txtinput = nextcord.ui.TextInput(label="Description", max_length=256, placeholder=desc)
            modal.add_item(txtinput)
            modal.callback = modalcallback
            await ctx.response.send_modal(modal)
        async def set_psw(ctx):
            async def modalcallback(ctx):
                global password
                password = txtinput.value
                await ctxe.edit(embed=embed(), view=editbtns)

            modal = nextcord.ui.Modal(title="Set Password", auto_defer=True)
            txtinput = nextcord.ui.TextInput(label="Password", max_length=30, placeholder=password)
            modal.add_item(txtinput)
            modal.callback = modalcallback
            await ctx.response.send_modal(modal)
        async def upload(ctx):
            global code, author, password, desc
            await ctx.response.defer()
            if code and author and password:
                pl = json.loads(await playlist.read())
                pl["amountOfLevels"] = len(pl["levels"])
                req = requests.post(f"https://fwogiiedev.com/api/playlists?customcode={code}&author={author}&description={desc}&password={password}", json=pl)
                if req.status_code == 409:
                    await ctx.followup.send("This code already exists, please pick another one!", ephemeral=True)
                    return
                if req.status_code != 200:
                    await ctx.followup.send(f"unexpected error, code: {req.status_code}")
                with open("storage/fwogiiedev.json", 'r') as read:
                    data = json.loads(read.read())
                data[str(ctx.user.id)] = {"code": code, "password": password, "author": author}
                data[author] = {"code": code, "password": password, "author": author}
                with open("storage/fwogiiedev.json", 'w') as write:
                    json.dump(data, write, indent=2)
                await ctx.followup.send(f"All set! You can now share this code: {code}", ephemeral=True)
                code, author, desc, password = "The code used to import this playlist into zeepkist", "The person who made this playlist", "The description of this playlist", "This password is needed to manage this playlist later on"
            else:
                await ctx.followup.send("Missing required Information!", ephemeral=True)

        editbtns = nextcord.ui.View(timeout=120, auto_defer=True)
        setcodebtn = nextcord.ui.Button(label="Set Code", style=nextcord.ButtonStyle.grey)
        setcodebtn.callback = set_code
        editbtns.add_item(setcodebtn)
        setauthorbtn = nextcord.ui.Button(label="Set Author", style=nextcord.ButtonStyle.grey)
        setauthorbtn.callback = set_author
        editbtns.add_item(setauthorbtn)
        setdescbtn = nextcord.ui.Button(label="Set Description", style=nextcord.ButtonStyle.grey)
        setdescbtn.callback = set_desc
        editbtns.add_item(setdescbtn)
        setpswbtn = nextcord.ui.Button(label="Set Password", style=nextcord.ButtonStyle.grey)
        setpswbtn.callback = set_psw
        editbtns.add_item(setpswbtn)
        uploadbtn = nextcord.ui.Button(label="Upload", style=nextcord.ButtonStyle.green)
        uploadbtn.callback = upload
        editbtns.add_item(uploadbtn)
        ctxe = await ctx.send(embed=embed(), view=editbtns, ephemeral=True)
    else:
        await ctx.send("Please attach a valid .zeeplist file", ephemeral=True)

print(f"| {__name__} loaded in")