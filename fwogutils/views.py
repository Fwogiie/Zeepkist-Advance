from cProfile import label

import requests
import json
import nextcord
import fwogutils
from fwogutils import log as log
from fwogutils.objects import Playlist
from playlist_stuff.top_gtr import embed


class LButtons(nextcord.ui.View):
    def __init__(self, gtrrankings):
        super().__init__(timeout=None, auto_defer=True)
        self.gtrrankings = gtrrankings

    @nextcord.ui.button(label="Show more", style=nextcord.ButtonStyle.grey)
    async def show_more(self, button: nextcord.Button, ctx: nextcord.Interaction):
        gtrrankings = self.gtrrankings
        log(f"reached by {ctx.user} ({ctx.user.id})")
        stringedrankings = ""
        stringranks = ""
        strranks = ""
        for x in gtrrankings[:30]:
            x = x['node']
            stringedrankings += f"{x['rank']}. `{x['userByIdUser']['steamName']}` with **{x['points']}** points and **{x['worldRecords']}** World Records\n"
        for x in gtrrankings[30:60]:
            x = x['node']
            stringranks += f"{x['rank']}. `{x['userByIdUser']['steamName']}` with **{x['points']}** points and **{x['worldRecords']}** World Records\n"
        for x in gtrrankings[60:90]:
            x = x['node']
            strranks += f"{x['rank']}. `{x['userByIdUser']['steamName']}` with **{x['points']}** points and **{x['worldRecords']}** World Records\n"
        embed = nextcord.Embed(title="GTR Rankings", description=stringedrankings, color=nextcord.Color.blue())
        embeda = nextcord.Embed(title=" ", description=stringranks, color=nextcord.Color.blue())
        embedb = nextcord.Embed(title=" ", description=strranks, color=nextcord.Color.blue())
        await ctx.send(embeds=[embed, embeda, embedb], ephemeral=True)

    @nextcord.ui.button(label="My ranking")
    async def my_rank(self, button: nextcord.Button, ctx: nextcord.Interaction):
        log(f"reached by {ctx.user} ({ctx.user.id})")
        userid = ctx.user.id
        ctx = await ctx.send("processing", ephemeral=True)
        linked = fwogutils.get_linked_users()
        if str(userid) in linked:
            linked = linked[str(userid)]
            log(f"user had gtr linked, showing rank!")
            if linked["userdata"]["position"] != 6969:
                userrank = linked["userdata"]["position"]
            else:
                print("e")
                print(fwogutils.getgtruserrank(linked["id"]))
                userrank = fwogutils.getgtruserrank(linked["id"])["rank"]
            closeranks = fwogutils.getgtrpositions(userrank-5, 11)
            ranks = ""
            for x in closeranks:
                x = x['node']
                if x['rank'] != userrank:
                    ranks += f"{x['rank']}. `{x['userByIdUser']['steamName']}` with **{x['points']}** points and **{x['worldRecords']}** World Records\n"
                else:
                    ranks += f"> {x['rank']}. `{x['userByIdUser']['steamName']}` with **{x['points']}** points and **{x['worldRecords']}** World Records\n"
            embed = nextcord.Embed(title="Your Rank", description=ranks, color=nextcord.Color.blue())
            await ctx.edit("", embed=embed)
        else:
            log(f"user did not have gtr linked!")
            await ctx.edit("You did not link your GTR! use `/link gtr` to do so!")

# Level Select
returnlist = []
class LevelSelect(nextcord.ui.View):
    def __init__(self, max: int=1, min: int=1):
        super().__init__(timeout=120, auto_defer=True)
        self.returnlist = []
        #StringSelect
        self.max = max
        self.min = min
        self.strselect = nextcord.ui.StringSelect(placeholder="No Levels", max_values=max, min_values=min, options=[nextcord.SelectOption(label='hey :3', value=1)], disabled=True, custom_id="thisisalevelsub")
        self.strselect.callback = self.level_selected
        self.add_item(self.strselect)
        #Level Search options
        self.btn_search_by = nextcord.ui.Button(label="Search Levels by:", disabled=True, style=nextcord.ButtonStyle.green)
        self.add_item(self.btn_search_by)
        #Level Search Option: Name
        self.btn_search_name = nextcord.ui.Button(label="Name", style=nextcord.ButtonStyle.grey)
        self.btn_search_name.callback =  self.search_by_name
        self.add_item(self.btn_search_name)
        #Level Search Option: Author
        self.btn_search_author = nextcord.ui.Button(label="Author", style=nextcord.ButtonStyle.grey)
        self.btn_search_author.callback = self.search_by_author
        self.add_item(self.btn_search_author)
        # Level Search Option: Workshop ID
        self.btn_search_wsid = nextcord.ui.Button(label="Workshop ID", style=nextcord.ButtonStyle.grey)
        self.btn_search_wsid.callback = self.search_by_wsid
        self.add_item(self.btn_search_wsid)

    async def search_by_name(self, ctx):
        self.modal = nextcord.ui.Modal(title="Level Search", auto_defer=True)
        self.modal_txtinput = nextcord.ui.TextInput(label="Level Name", required=True)
        self.modal.add_item(self.modal_txtinput)
        self.modal.callback = self.search_name_callback
        await ctx.response.send_modal(self.modal)

    async def search_name_callback(self, ctx):
        self.searchcache = {}
        req = requests.get(f"https://jsonapi.zworpshop.com/levels?filter=contains(name,%27{self.modal_txtinput.value}%27)")
        if req.status_code != 200:
            log(f"From LevelSelect received status code {req.status_code} in Level name Search, that's bad :/")
            await ctx.send("An error occurred. Please try again", ephemeral=True)
            return
        else:
            reqlvls, lvls, numid = json.loads(req.text), [], 1
            for x in reqlvls['data']:
                if len(lvls) < 26:
                    x = x['attributes']
                    lvls.append(nextcord.SelectOption(label=x['name'], description=x['fileAuthor'], value=numid))
                    self.searchcache[str(numid)] = fwogutils.convert_jsonapi_att(x)
                    numid += 1
                else:
                    break
            await self.set_options(ctx, lvls)

    async def search_by_author(self, ctx):
        self.modal = nextcord.ui.Modal(title="Level Search", auto_defer=True)
        self.modal_txtinput = nextcord.ui.TextInput(label="Author Name", required=True)
        self.modal.add_item(self.modal_txtinput)
        self.modal.callback = self.search_author_callback
        await ctx.response.send_modal(self.modal)

    async def search_author_callback(self, ctx):
        self.searchcache = {}
        req = requests.get(f"https://jsonapi.zworpshop.com/levels?filter=contains(fileAuthor,%27{self.modal_txtinput.value}%27)")
        if req.status_code != 200:
            log(f"From LevelSelect received status code {req.status_code} in Level author Search, that's bad :/")
            await ctx.send("An error occurred. Please try again", ephemeral=True)
            return
        else:
            reqlvls, lvls, numid = json.loads(req.text), [], 1
            for x in reqlvls['data']:
                if len(lvls) < 26:
                    x = x['attributes']
                    lvls.append(nextcord.SelectOption(label=x['name'], description=x['fileAuthor'], value=numid))
                    self.searchcache[str(numid)] = fwogutils.convert_jsonapi_att(x)
                    numid += 1
                else:
                    break
            await self.set_options(ctx, lvls)

    async def search_by_wsid(self, ctx):
        self.modal = nextcord.ui.Modal(title="Level Search", auto_defer=True)
        self.modal_txtinput = nextcord.ui.TextInput(label="Workshop ID", required=True)
        self.modal.add_item(self.modal_txtinput)
        self.modal.callback = self.search_wsid_callback
        await ctx.response.send_modal(self.modal)

    async def search_wsid_callback(self, ctx):
        self.searchcache = {}
        req = requests.get(f"https://jsonapi.zworpshop.com/levels?filter=equals(workshopId,%27{self.modal_txtinput.value}%27)")
        if req.status_code != 200:
            log(f"From LevelSelect received status code {req.status_code} in Level author Search, that's bad :/")
            await ctx.send("An error occurred. Please try again", ephemeral=True)
            return
        else:
            reqlvls, lvls, numid = json.loads(req.text), [], 1
            for x in reqlvls['data']:
                if len(lvls) < 26:
                    x = x['attributes']
                    lvls.append(nextcord.SelectOption(label=x['name'], description=x['fileAuthor'], value=numid))
                    self.searchcache[str(numid)] = fwogutils.convert_jsonapi_att(x)
                    numid += 1
                else:
                    break
            await self.set_options(ctx, lvls)

    async def level_selected(self, ctx):
        self.returnlist = []
        for x in self.strselect.values:
            self.returnlist.append(self.searchcache[x])
        fwogutils.dump_returnlist(self.returnlist)

    async def set_options(self, ctx, options):
        if len(options) >= self.max:
            self.strselect.disabled = False
            self.strselect.placeholder = f"Select Level ({len(options)} Levels Found)"
            self.strselect.options = options
        else:
            self.strselect.placeholder = "No Levels found"
            self.strselect.options = [nextcord.SelectOption(label="You arent supposed to see this!", description="Please tell Fwogiie if you see this")]
            self.strselect.disabled = True
        await ctx.edit(view=self)

    async def clear_options(self, ctx):
        self.strselect.options = [nextcord.SelectOption(label='Options were cleared', description='Your arent supposed to see this, please tell fwogiie about this :3', value=1)]
        await ctx.edit(view=self)

class DownloadPlaylist(nextcord.ui.View):
    def __init__(self, download_url:str, playlist:Playlist):
        super().__init__()
        self.playlist = playlist
        btn = nextcord.ui.Button(label="Download", style=nextcord.ButtonStyle.url, url=download_url)
        self.add_item(btn)

    @nextcord.ui.button(label="Import by:", style=nextcord.ButtonStyle.green, disabled=True)
    async def import_by(self):
        pass

    @nextcord.ui.button(label="Edit Playlist", style=nextcord.ButtonStyle.grey, row=1)
    async def edit_pl_callback(self, btn, ctx):
        await ctx.edit(view=EditPlaylist(self.playlist))


class EditPlaylist(nextcord.ui.View):
    def __init__(self, playlist:Playlist):
        super().__init__()
        self.playlist = playlist
        modal = nextcord.ui.Modal(title="Rename Playlist")
        self.modaltext = nextcord.ui.TextInput(label="Name")
        modal.add_item(self.modaltext)
        modal.callback = self.modal_callback
        self.modal = modal

    @nextcord.ui.button(label="Edit:", style=nextcord.ButtonStyle.green, disabled=True)
    async def edit(self):
        pass

    @nextcord.ui.button(label="Name", style=nextcord.ButtonStyle.grey)
    async def edit_name(self, btn, ctx):
        await ctx.response.send_modal(self.modal)

    async def modal_callback(self, ctx):
        self.playlist.name = self.modaltext.value
        await ctx.edit(embed=self.playlist.embed)

    @nextcord.ui.button(label="Time +", style=nextcord.ButtonStyle.grey)
    async def time_add(self, btn, ctx):
        self.playlist.roundlength += 30
        await ctx.edit(embed=self.playlist.embed)

    @nextcord.ui.button(label="Time -", style=nextcord.ButtonStyle.grey)
    async def time_remove(self, btn, ctx):
        self.playlist.roundlength -= 30
        await ctx.edit(embed=self.playlist.embed)

    @nextcord.ui.button(label="Toggle Shuffle", style=nextcord.ButtonStyle.grey)
    async def shuffle_toggle(self, btn, ctx):
        if self.playlist.shuffle is True:
            self.playlist.shuffle = False
        else:
            self.playlist.shuffle = True
        await ctx.edit(embed=self.playlist.embed)

    @nextcord.ui.button(label="Actions:", style=nextcord.ButtonStyle.green, disabled=True, row=1)
    async def actions(self):
        pass

    @nextcord.ui.button(label="Reverse Playlist", style=nextcord.ButtonStyle.grey, row=1)
    async def reverse_pl(self, btn, ctx):
        self.playlist.levels.reverse()
        await ctx.edit(embed=self.playlist.embed)

    @nextcord.ui.button(label="Apply", style=nextcord.ButtonStyle.green, row=2)
    async def apply(self, btn, ctx):
        await ctx.edit(view=DownloadPlaylist(await self.playlist.get_download_url(), self.playlist))