from fwogutils import bot, log
import nextcord
import re
import json
import fwogutils
import requests
import random
import fwogutils.views

@bot.message_command(name="create-playlist")
async def create_pl(ctx, msg: nextcord.Message):
    chan, msgs = await bot.fetch_channel(ctx.channel.id), []
    async for x in chan.history(limit=500):
        msgs.append(x.content)
        if x.id == msg.id:
            msgs.reverse()
            break
    if len(msgs) < 2:
        await ctx.send("You need at least 2 levels to create a playlist!", ephemeral=True)
        return
    async def modal_sub(ctx):
        wsids, levels, sorting, levelfails, antipack, duplicheck, packlvls, dupliwarn, dupliwarnlvls = [], [], {}, "", [], [], "", [], ""
        for x in msgs:
            workshop_urls = re.findall("https://steamcommunity\.com/sharedfiles/filedetails/\?id=\d+", x)
            if workshop_urls:
                for url in workshop_urls:
                    wsids.append(url.split('=')[1])
        if not wsids:
            log("Playlist would be empty, warning and returning")
            await ctx.send("Your playlist would be empty, so i dint create any!", ephemeral=True)
            return
        else:
            ctxe = await ctx.send("processing", ephemeral=True)
            reqlevels = json.loads(requests.post(f"https://graphql.zeepkist-gtr.com", json={"query": "query GetLevels($workshopIds: [BigFloat!]) { allLevelItems(filter: { workshopId: { in: $workshopIds } }) { nodes { name fileAuthor fileUid workshopId } } }", "variables": {"workshopIds": wsids}}).text)
            for x in reqlevels["data"]["allLevelItems"]["nodes"]:
                id = x['workshopId']
                if id not in antipack:
                    log(f"{id} wasnt in antipack, adding and appending to antipack")
                    sorting[id] = {"UID": x['fileUid'], "WorkshopID": x['workshopId'], "Name": x['name'], "Author": x['fileAuthor']}
                    antipack.append(id)
                elif id in antipack and id not in duplicheck:
                    log(f"{id} is pack, adding to pack list for warn")
                    packlvls += f"- [{x['name']} - {id}](<https://steamcommunity.com/sharedfiles/filedetails/?id={id}>)\n"
                    duplicheck.append(id)
            for x in wsids:
                try:
                    log(f"Trying for {x} in for wsids")
                    levels.append(sorting[x])
                    log("Level Appended.")
                except KeyError:
                    log(f"{x} is assumed to have failed the try, KeyError was raised")
                    levelfails += f"- [Workshop ID: {x}](<https://steamcommunity.com/sharedfiles/filedetails/?id={x}>)\n"
            for x in levels:
                if x not in dupliwarn:
                    dupliwarn.append(x)
                else:
                    dupliwarnlvls += f"- [{x['Name']} - {x['WorkshopID']}](<https://steamcommunity.com/sharedfiles/filedetails/?id={x['WorkshopID']}>)\n"
            plname = textinput.value
            async def btn_add_level(ctx):
                view = fwogutils.views.LevelSelect()
                await ctx.send(view=view, ephemeral=True)
                await bot.wait_for("interaction", check=lambda interaction: interaction.data['custom_id'] == "thisisalevelsub", timeout=120)
                level = fwogutils.get_returnlist()[0]
                pl["levels"].append(level)
                fwogutils.dumppl(pl)
                fwogutils.renamepl(plname)
                await ctxe.edit(file=nextcord.File(f"storage/{plname}.zeeplist"))
                fwogutils.undorename(plname)
                await ctx.send(f"added **{level['Name']}** to the playlist", ephemeral=True)
            async def btn_remove_duplicates(ctx):
                duplicheck, updlvls, duplicount = [], [], 0
                outdatedlvls = pl["levels"]
                for x in outdatedlvls:
                    if x not in duplicheck:
                        updlvls.append(x)
                        duplicheck.append(x)
                    else:
                        duplicount += 1
                pl["levels"] = updlvls
                pl["amountOfLevels"] = len(updlvls)
                fwogutils.dumppl(pl)
                fwogutils.renamepl(plname)
                await ctxe.edit(file=nextcord.File(f"storage/{plname}.zeeplist"))
                fwogutils.undorename(plname)
                await ctx.send(f"{duplicount} Duplicates removed.", ephemeral=True)
            async def btn_shuffle_pl(ctx):
                random.shuffle(pl["levels"])
                fwogutils.dumppl(pl)
                fwogutils.renamepl(plname)
                await ctxe.edit(file=nextcord.File(f"{plname}.zeeplist"))
                fwogutils.undorename(plname)
                await ctx.send("Playlist has been shuffled.", ephemeral=True)
            async def btn_make_koc(ctx):
                newlvls = []
                async def btn_continue(ctx):
                    for x in pl['levels']:
                        newlvls.append(x)
                        newlvls.append({"UID": "09052023-112732077-[CTR]OwlPlague-249589054336-368", "WorkshopID": "2973690373",
                                        "Name": "KICK OR CLUTCH VOTING LEVEL", "Author": "[CTR]OwlPlague"})
                    pl['levels'] = newlvls
                    pl["amountOfLevels"] = len(newlvls)
                    fwogutils.dumppl(pl)
                    fwogutils.renamepl(plname)
                    await ctxe.edit(file=nextcord.File(f"storage/{plname}.zeeplist"))
                    fwogutils.undorename(plname)
                    await ctx.send("Done!", ephemeral=True)
                async def btn_edit_level(ctx):
                    view = fwogutils.views.LevelSelect()
                    await ctx.send(view=view, ephemeral=True)
                    await bot.wait_for("interaction", check=lambda interaction: interaction.data['custom_id'] == "thisisalevelsub", timeout=120)
                    level = fwogutils.get_returnlist()[0]
                    for x in pl['levels']:
                        newlvls.append(x)
                        newlvls.append(level)
                    pl['levels'] = newlvls
                    pl["amountOfLevels"] = len(newlvls)
                    fwogutils.dumppl(pl)
                    fwogutils.renamepl(plname)
                    await ctxe.edit(file=nextcord.File(f"storage/{plname}.zeeplist"))
                    fwogutils.undorename(plname)
                    await ctx.send("Done!", ephemeral=True)
                kocview = nextcord.ui.View(timeout=60)
                btncontinue = nextcord.ui.Button(label="Continue", style=nextcord.ButtonStyle.green)
                btncontinue.callback = btn_continue
                btneditlvl = nextcord.ui.Button(label="Edit Level", style=nextcord.ButtonStyle.grey)
                btneditlvl.callback = btn_edit_level
                kocview.add_item(btncontinue)
                kocview.add_item(btneditlvl)
                await ctx.send("Make this playlist Koc-Like?\n*Continuing Would use the default voting level*", view=kocview, ephemeral=True)
            editbtns = nextcord.ui.View(timeout=60)
            btnaddlvl = nextcord.ui.Button(label="Add Level", style=nextcord.ButtonStyle.green)
            btnaddlvl.callback = btn_add_level
            btnremdupelvls = nextcord.ui.Button(label="Remove Duplicate Levels", style=nextcord.ButtonStyle.red)
            btnremdupelvls.callback = btn_remove_duplicates
            btnshufflvls = nextcord.ui.Button(label="Shuffle Levels", style=nextcord.ButtonStyle.grey)
            btnshufflvls.callback = btn_shuffle_pl
            btnmakekoc = nextcord.ui.Button(label="Make Koc", style=nextcord.ButtonStyle.grey)
            btnmakekoc.callback = btn_make_koc
            editbtns.add_item(btnaddlvl)
            editbtns.add_item(btnremdupelvls)
            editbtns.add_item(btnshufflvls)
            editbtns.add_item(btnmakekoc)
            pl = {"name": plname, "amountOfLevels": len(levels), "roundLength": 480.0, "shufflePlaylist": False, "UID": [], "levels": levels}
            fwogutils.dumppl(pl)
            fwogutils.renamepl(plname)
            await ctxe.edit(f"# Your playlist has been generated!\n### Failed levels (These levels failed and would need to be added manually):\n{levelfails[:500]}\n"
                            f"### Level packs (Might need manual adjustments):\n{packlvls[:500]}\n### Duplicate Levels (Press the remove duplicates button to remove them):\n{dupliwarnlvls[:500]}",
                            file=nextcord.File(f"storage/{plname}.zeeplist"), view=editbtns)
            fwogutils.undorename(plname)
    modal = nextcord.ui.Modal(title="Playlist creation")
    textinput = nextcord.ui.TextInput(label="Playlist name", min_length=1, max_length=50)
    modal.add_item(textinput)
    modal.callback = modal_sub
    await ctx.response.send_modal(modal)

print(f"| {__name__} loaded in")