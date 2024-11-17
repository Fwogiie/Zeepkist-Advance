import nextcord, discord
from pathvalidate import sanitize_filename
import fwogutils


class Playlist(object):
    def __init__(self, name:str="No name", roundlength:float=480.0, shuffle:bool=False, json:tuple=None):
        super().__init__()
        if json is None:
            self._name = name
            self._roundlength = roundlength
            self._shuffle = shuffle
            self._levels = []
        else:
            self._name = json["name"]
            self._roundlength = json["roundLength"]
            self._shuffle = json["shufflePlaylist"]
            self._levels = json["levels"]

    @property
    def name(self) -> str:
        return self._name

    @name.setter
    def name(self, value:str):
        self._name = value

    @property
    def roundlength(self) -> float:
        return self._roundlength

    @roundlength.setter
    def roundlength(self, value:float):
        self._roundlength = value

    @property
    def shuffle(self) -> bool:
        return self._shuffle

    @shuffle.setter
    def shuffle(self, value:bool):
        self._shuffle = value

    @property
    def levels(self) -> list:
        return self._levels

    @levels.setter
    def levels(self, value:list):
        self._levels = value

    @property
    def level_count(self):
        return len(self._levels)

    @property
    def playlist_json(self):
        return {"name": self.name, "amountOfLevels": self.level_count, "roundLength": self.roundlength, "shufflePlaylist": self.shuffle, "UID": [], "levels": self._levels}

    @property
    def embed(self):
        embed = discord.Embed(title="Playlist", color=nextcord.Color.blue())
        embed.add_field(name="Playlist Info:", value=f"Name: {self.name}\nTime (Round Length): {fwogutils.format_time(self.roundlength)[:5]}\n"
                                                     f"Shuffle: {self.shuffle}\nAmount of Levels: {self.level_count}\n"
                                                     f"First level: {self._levels[0]['Name']} by {self._levels[0]['Author']}\n"
                                                     f"Last level: {self._levels[-1]['Name']} by {self._levels[-1]['Author']}")
        return embed

    async def get_download_url(self):
        fwogutils.dumppl(self.playlist_json)
        fwogutils.renamepl(sanitize_filename(self._name))
        msg = await fwogutils.bot.get_channel(1213563680080273408).send(file=nextcord.File(f"storage/{sanitize_filename(self._name)}.zeeplist"))
        fwogutils.undorename(sanitize_filename(self._name))
        return msg.attachments[0].url

    def add_level(self, uid:str, workshopid:str, name:str, author:str):
        self._levels.append({"UID": uid, "WorkshopID": workshopid, "Name": name, "Author": author})