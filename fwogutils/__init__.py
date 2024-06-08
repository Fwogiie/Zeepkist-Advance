import datetime
import time
import nextcord
import tzlocal
from discord.ext import commands, tasks
import inspect
import pytz
import requests
import json
import os

intents = nextcord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix='!',
                   intents=intents,
                   owner_id=785037540155195424)

bot_ids = [1143521016031744025, 1126430942924386315]


def log(text: str, type: str=None):
    with open("log.txt", mode="r+") as logging:
        txt = logging.read()
        if type == "clear":
            logging.truncate(0)
            logging.seek(0)
            logging.write("Cleared")
        else:
            logging.truncate(0)
            logging.seek(0)
            logging.write(f"{txt}\nin {inspect.stack()[1].function} @ {datetime.datetime.now(tz=pytz.timezone('Europe/Brussels')).strftime('%m/%d, %H:%M:%S')} : {text}")


def errormessage(error):
    return f"An error occured. if this persists please report it in the zeepkist modding server: [here](https://discord.gg/a4FxG9RpV3) in this thread: https://discord.com/channels/972933002516647986/1126438917420359691 \n \n Error: `{str(error)}`"

def format_time(time: float):
    """
    you go girl <3
    """
    minutes = int(time // 60)
    seconds = int(time % 60)
    milliseconds = int((time % 1) * 1000)
    formatted_time = f"{minutes:02d}:{seconds:02d}:{milliseconds:03d}"
    return formatted_time

def hex_to_rgb(hex):
  return tuple(int(hex[i:i+2], 16) for i in (0, 2, 4))


def getgtruser(id: int=None, discid: int=None):
    """
    remember fwogiie,
    to get username: steamName
    to get user steam ID: steamId
    to get user discord ID: discordId

    stay awesome girl <3
    """
    if id != None:
        req = requests.get(f"https://api.zeepkist-gtr.com/users/{id}")
        if req.status_code != 200:
            return [False, req.status_code]
        else:
            return [True, json.loads(req.text)]
    elif discid != None:
        req = requests.get(f"https://api.zeepkist-gtr.com/users/discord/{discid}")
        if req.status_code != 200:
            return [False, req.status_code]
        else:
            return [True, json.loads(req.text)]


def getgtrrecord(id: int):
    """
    {
  "id": 0,
  "time": 0,
  "splits": [
    0
  ],
  "isValid": true,
  "gameVersion": "string",
  "modVersion": "string",
  "level": "string",
  "user": 0
   }

stay silly girl :3
    """
    return json.loads(requests.get(f"https://api.zeepkist-gtr.com/records/{id}").text)

def getgtruserrankings(limit: int, offset: int):
    """
    {
  "totalAmount": 0,
  "rankings": [
    {
      "user": {
        "id": 0,
        "steamId": "string",
        "steamName": "string",
        "discordId": "string"
      },
      "amountOfWorldRecords": 0,
      "position": 0,
      "score": 0
    }
  ]
}

good girl :>
    """
    return json.loads(requests.get(f"https://api.zeepkist-gtr.com/users/rankings?Limit={limit}&Offset={offset}").text)

def getgtruserrank(id: int):
    """
    {
  "amountOfWorldRecords": 0,
  "position": 0,
  "score": 0
}

girl!
    """
    return json.loads(requests.get(f"https://api.zeepkist-gtr.com/users/ranking/{id}").text)

def checkzeeplist(filename: str):
    """
    returns True if the filename is "zeeplist"
    useful for quite a bit of stuff :3

    go girl! :>
    """
    if filename.split(".")[1:][0] == "zeeplist":
        return True
    else:
        return False

def dumppl(pl):
    with open("playlist.zeeplist", 'w') as f:
        json.dump(pl, f, indent=2)

def renamepl(name):
    os.rename("playlist.zeeplist", f"{name}.zeeplist")

def undorename(name):
    os.rename(f"{name}.zeeplist", "playlist.zeeplist")

def addgtruser(discid: str, user: str):
    with open("users.json", 'r') as f:
        data = json.loads(f.read())
        data["linked"][discid] = user
        data["linked"][discid]["settings"] = {"notifs": {"RU": False, "RD": False, "WRST": False}}
        data["linked"][discid]["userdata"] = {"position": 6969}
    with open("users.json", 'w') as ft:
        json.dump(data, ft, indent=2)

def add_usercache(id: int):
    """
    this is obsolete, don't use this fwogiie <3
    """
    user = getgtruser(id=id)
    if user[0]:
        with open("users.json", 'r') as f:
            data = json.loads(f.read())
            data["usercache"][str(id)] = user[1]
        with open("users.json", 'w') as ft:
            json.dump(data, ft, indent=2)

def get_linked_users():
    with open("users.json", 'r') as f:
        data = json.loads(f.read())
        return data['linked']

def gtrlb_shedule():
    times = [datetime.time(hour=0, minute=5), datetime.time(hour=6, minute=5), datetime.time(hour=12, minute=5),
             datetime.time(hour=18, minute=5)]
    return times

def setlinkedusersetting(setting: str, value, user):
    with open("users.json", 'r') as f:
        data = json.loads(f.read())
        data["linked"][str(user)]["settings"]["notifs"][str(setting)] = value
        if setting == 'RU' and value is True:
            data["usercache"]["RUusers"].append(str(user))
            data["linked"][str(user)]["userdata"]["position"] = jsonapi_get_playerrank(data["linked"][str(user)]["id"])
        if setting == 'RD' and value is True:
            data["usercache"]["RDusers"].append(str(user))
            data["linked"][str(user)]["userdata"]["position"] = jsonapi_get_playerrank(data["linked"][str(user)]["id"])
        if setting == 'WRST' and value is True:
            data["usercache"]["WRSTusers"][str(data["linked"][str(user)]["id"])] = {"discid": str(user)}
        if setting == 'RU' and value is False:
            data["usercache"]["RUusers"].remove(str(user))
        if setting == 'RD' and value is False:
            data["usercache"]["RDusers"].remove(str(user))
        if setting == 'WRST' and value is False:
            data["usercache"]["WRSTusers"].pop(str(data["linked"][str(user)]["id"]))
    with open("users.json", 'w') as ft:
        json.dump(data, ft, indent=2)

def getlinkedusersettings(user):
    with open("users.json", 'r') as f:
        data = json.loads(f.read())
        return data["linked"][str(user)]["settings"]

def userislinked(id):
    with open("users.json", 'r') as f:
        data = json.loads(f.read())
    if str(id) in data["linked"]:
        return True
    else:
        return False

def getRUusers():
    with open("users.json", 'r') as f:
        data = json.loads(f.read())
        return data["usercache"]["RUusers"]

def getRDusers():
    with open("users.json", 'r') as f:
        data = json.loads(f.read())
        return data["usercache"]["RDusers"]

def getWRSTusers():
    with open("users.json", 'r') as f:
        data = json.loads(f.read())
        return data["usercache"]["WRSTusers"]

def getlinkeduserdata(user):
    with open("users.json", 'r') as f:
        data = json.loads(f.read())
        return data["linked"][str(user)]["userdata"]

def setlinkedranking(user: str, pos: int):
    with open("users.json", 'r') as f:
        data = json.loads(f.read())
        data["linked"][user]["userdata"]["position"] = pos
        with open("users.json", 'w') as ft:
            json.dump(data, ft, indent=2)

def jsonapi_get_toplevelpoints(limit: int):
    if limit < 1000:
        if limit > 100:
            hashes = []
            pages = int(str(limit)[0])
            for x in range(pages):
                req = json.loads(requests.get(f"https://jsonapi.zeepkist-gtr.com/levelPoints?page[number]={x+1}&page[size]=100&sort=-points&fields[levelPoints]=level").text)
                for x in req["data"]:
                    if x["attributes"]["level"] not in hashes:
                        hashes.append(x["attributes"]["level"])
            req = json.loads(requests.get(f"https://jsonapi.zeepkist-gtr.com/levelPoints?page[number]={pages+1}&page[size]=100&sort=-points&fields[levelPoints]=level").text)
            for x in req["data"][0:int(str(limit)[1:69])]:
                if x["attributes"]["level"] not in hashes:
                    hashes.append(x["attributes"]["level"])
            return hashes
        else:
            hashes = []
            req = json.loads(requests.get(f"https://jsonapi.zeepkist-gtr.com/levelPoints?page[number]=1&page[size]={limit}&sort=-points&fields[levelPoints]=level").text)
            for x in req["data"]:
                if x["attributes"]["level"] not in hashes:
                    hashes.append(x["attributes"]["level"])
            return hashes
    else:
        return False

def converturlsepperations(data: list):
    returndata = ""
    for x in data:
        returndata += f"{x},"
    return returndata

def zworp_getlevelsbyhashlist(levels: str):
    """
    takes level hashes from converturlsepperations and returns all the info you need for a playlist.

    go girl!
    """
    zeeplist = {}
    loopy = True
    duplicheck = []
    loopsets = {"offset": 0, "limit": 4100}
    while loopy is True:
        reqlevels = levels[loopsets["offset"]:loopsets["limit"]]
        if list(reqlevels):
            rawreq = requests.get(f"https://api.zworpshop.com/levels/hashes/{reqlevels}")
            req = json.loads(rawreq.text)
            for x in req:
                if x['fileHash'] not in duplicheck:
                    zeeplist[x['fileHash']] = {
                        "UID": x['fileUid'],
                        "WorkshopID": int(x['workshopId']),
                        "Name": x['name'],
                        "Author": x['fileAuthor']
                    }
                    duplicheck.append(x['fileHash'])
            loopsets["offset"] += 4100
            loopsets["limit"] += 4100
        else:
            loopy = False
    return zeeplist

def zworp_getlevel(hash: str):
    req = requests.get(f"https://api.zworpshop.com/levels/hash/{hash}?IncludeReplaced=false&IncludeDeleted=false")
    if req.status_code != 200:
        return False
    else:
        return json.loads(req.text)

def jsonapi_get_playerrank(user: int):
    return json.loads(requests.get(f"https://jsonapi.zeepkist-gtr.com/users/{user}/playerPoints").text)['data'][0]['attributes']['rank']

def gtr_getalluserwrs(gtruserid: int):
    amount = json.loads(requests.get(f"https://api.zeepkist-gtr.com/wrs/user/{gtruserid}?Limit=0&Offset=0").text)["totalAmount"]
    pages = int(amount / 100)
    leftovers = int(str(amount)[1:69])
    wrs = []
    if pages > 0:
        for x in range(pages):
            wrpage = json.loads(requests.get(f"https://api.zeepkist-gtr.com/wrs/user/{gtruserid}?Limit={x+1}00&Offset={x}00").text)
            for wr in wrpage['items']:
                wrs.append(wr['level'])
    wrpage = json.loads(requests.get(f"https://api.zeepkist-gtr.com/wrs/user/{gtruserid}?Limit={leftovers}&Offset={pages}00").text)
    for wr in wrpage['items']:
        wrs.append(wr['level'])
    return wrs

def loc_setuserwrs(gtruserid: int, wrs: list):
    with open("gtrusercache.json", 'r') as f:
        data = json.loads(f.read())
        data[str(gtruserid)] = wrs
    with open("gtrusercache.json", 'w') as ft:
        json.dump(data, ft, indent=2)

def loc_getuserwrs(gtruserid: int):
    with open("gtrusercache.json", 'r') as f:
        data = json.loads(f.read())
        return data[str(gtruserid)]

def loc_removeuserwr(gtruserid: int, level: str):
    """
    scary!
    """
    with open("gtrusercache.json", 'r') as f:
        data = json.loads(f.read())
        data[str(gtruserid)].remove(level)
    with open("gtrusercache.json", 'w') as ft:
        json.dump(data, ft, indent=2)

def loc_adduserwr(gtruserid: int, level: str):
    """
    scary!
    """
    with open("gtrusercache.json", 'r') as f:
        data = json.loads(f.read())
        data[str(gtruserid)].append(level)
    with open("gtrusercache.json", 'w') as ft:
        json.dump(data, ft, indent=2)

def jsonfromreq(req):
    return json.loads(req.text)

class GTR:
    class Levels:
        class Hot:
            def __init__(self):
                self.req = requests.get("https://api.zeepkist-gtr.com/levels/hot")
            @property
            def levels(self):
                """{"level": "string", "recordsCount": 0}"""
                return jsonfromreq(self.req)["levels"]
            @property
            def status_code(self):
                return self.req.status_code

class Zworp:
    class Levels:
        class Hashes:
            def __init__(self, hashlist):
                self.req = requests.get(f"https://api.zworpshop.com/levels/hashes/{hashlist}?IncludeReplaced=false&IncludeDeleted=false")
            @property
            def levels(self):
                """[{
                    "id": 0,
                    "replacedBy": 0,
                    "deleted": true,
                    "workshopId": "string",
                    "authorId": "string",
                    "name": "string",
                    "createdAt": "2024-03-02T19:44:54.306Z",
                    "updatedAt": "2024-03-02T19:44:54.306Z",
                    "imageUrl": "string",
                    "fileUrl": "string",
                    "fileUid": "string",
                    "fileHash": "string",
                    "fileAuthor": "string",
                    "valid": true,
                    "validation": 0,
                    "gold": 0,
                    "silver": 0,
                    "bronze": 0
                  }]"""
                return jsonfromreq(self.req)
            @property
            def status_code(self):
                return self.req.status_code

def jsonapi_getrecord(id: int):
    return json.loads(requests.get(f"https://jsonapi.zeepkist-gtr.com/records/{id}").text)['data']['attributes']

def jsonapi_getgtrpositions(frompos: int, amount: int):
    return json.loads(requests.get(f"https://jsonapi.zeepkist-gtr.com/playerpoints?filter=greaterOrEqual(rank,%27{frompos}%27)&page[size]={amount}&fields[playerPoints]=rank,userId,worldRecords,points&sort=rank").text)

def getgtruserv2(userid: int=None, steamid: int=None, discordid: int=None):
    if userid != None:
        req = requests.get(f"https://api.zeepkist-gtr.com/users/{userid}")
        if req.status_code != 200:
            return False
        else:
            return json.loads(req.text)
    elif steamid != None:
        req = requests.get(f"https://api.zeepkist-gtr.com/users/steam/{steamid}")
        if req.status_code != 200:
            return False
        else:
            return json.loads(req.text)
    elif discordid != None:
        req = requests.get(f"https://api.zeepkist-gtr.com/users/discord/{discordid}")
        if req.status_code != 200:
            return False
        else:
            return json.loads(req.text)

def userhandler(userid: str=None, steamid: str=None, steamname: str=None, discordid: str=None):
    with open("gtrusercache.json", 'r') as cacheread:
        cache = json.loads(cacheread.read())
    if userid:
        try:
            return cache['userId'][str(userid)]
        except KeyError:
            user = getgtruserv2(userid=userid)
            if user is False:
                return False
            else:
                cache["userId"][str(user["id"])] = user
                cache["steamId"][str(user["steamId"])] = user
                cache["steamName"][str(user["steamName"])] = user
                if user["discordId"] != None or discordid != "-1":
                    cache["discordId"][str(user["discordId"])] = user
                with open("gtrusercache.json", 'w') as cachewrite:
                    json.dump(cache, cachewrite, indent=2)
                return user
    elif steamid:
        try:
            return cache['steamId'][str(steamid)]
        except KeyError:
            user = getgtruserv2(steamid=steamid)
            if user is False:
                return False
            else:
                cache["userId"][str(user["id"])] = user
                cache["steamId"][str(user["steamId"])] = user
                cache["steamName"][str(user["steamName"])] = user
                if user["discordId"] != None or discordid != "-1":
                    cache["discordId"][str(user["discordId"])] = user
                with open("gtrusercache.json", 'w') as cachewrite:
                    json.dump(cache, cachewrite, indent=2)
                return user
    elif steamname:
        try:
            return cache['steamName'][str(steamname)]
        except KeyError:
            return False
    elif discordid:
        try:
            return cache['discordId'][str(discordid)]
        except KeyError:
            user = getgtruserv2(discordid=discordid)
            if user is False:
                return False
            else:
                cache["userId"][str(user["id"])] = user
                cache["steamId"][str(user["steamId"])] = user
                cache["steamName"][str(user["steamName"])] = user
                if user["discordId"] != None or discordid != "-1":
                    cache["discordId"][str(user["discordId"])] = user
                with open("gtrusercache.json", 'w') as cachewrite:
                    json.dump(cache, cachewrite, indent=2)
                return user

def convert_jsonapi_att(att):
    return {"UID": att['fileUid'],"WorkshopID": att['workshopId'],"Name": att['name'],"Author": att['fileAuthor']}

def get_returnlist():
    with open("fwogutils/returnlist.txt", 'r') as read:
        return json.loads(read.read())["returnlist"]

def dump_returnlist(dump):
    with open("fwogutils/returnlist.txt", 'w') as write:
        dump = {"returnlist": dump}
        json.dump(dump, write)

# kept comment for now
"""for temp in range(15):
    num = 1
    req = requests.get(f"https://jsonapi.zworpshop.com/levels?page[size]=100&page[number]={num}")
    if req.status_code != 200:
        print(f"got status code {req.status_code} at num {num}.\ndata: {req.text}")
        break
    data = json.loads(req.text)
    if data['data']:
        lb, inituser = {}, []
        for x in data['data']:
            x = x['attributes']
            if x['fileAuthor'] not in inituser:
                lb[str(x['fileAuthor'])] = 1
                inituser.append(x['fileAuthor'])
            else:
                lb[str(x['fileAuthor'])] += 1
            print(f"{x['fileAuthor']} is assumed to have made a level.\ntheir level count is now: {lb[x['fileAuthor']]}")
        num += 1
    else:
        print("Scrape is assumed to be finished.")
        break
print(f"final assumed LB:")
for x in lb:
    print(x)"""