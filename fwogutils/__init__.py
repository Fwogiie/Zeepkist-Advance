import datetime
import nextcord
from discord.ext import commands, tasks
import inspect
import pytz
import requests
import json
import os

import fwogutils
from fwogutils.queries import post_url

intents = nextcord.Intents.all()

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
            print(f"in {inspect.stack()[1].function} @ {datetime.datetime.now(tz=pytz.timezone('Europe/Brussels')).strftime('%m/%d, %H:%M:%S')} : {text}")


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
    remember naomi,
    to get username: steamName
    to get user steam ID: steamId
    to get user discord ID: discordId

    stay awesome girl <3
    """
    if id != None:
        req = requests.post(queries.post_url, json={"query": """
        query MyQuery($id: Int) {
  allUsers(condition: {id: $id}) {
    edges {
      node {
        id
        steamName
        steamId
        discordId
      }
    }
  }
}""", "variables": {"id": id}})
        if req.status_code != 200:
            return [False, req.status_code]
        else:
            return [True, json.loads(req.text)]
    elif discid != None:
        req = requests.post(queries.post_url, json={"query": """
        query MyQuery($discid: BigFloat) {
  allUsers(condition: {discordId: $discid}) {
    edges {
      node {
        id
        steamName
        steamId
        discordId
      }
    }
  }
}""", "variables": {"discid": str(discid)}})
        if req.status_code != 200:
            return [False, req.status_code]
        user = json.loads(req.text)
        user = user['data']['allUsers']['edges']
        if not user:
            return[False, 404]
        else:
            return [True, user[0]['node']]

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
    jsontxt = json.loads(requests.post(queries.post_url, json={"query": """
    query MyQuery($first: Int = 100, $offset: Int = 0) {
  allUserPoints(first: $first, offset: $offset, orderBy: POINTS_DESC) {
    edges {
      node {
        rank
        worldRecords
        points
        userByIdUser {
          steamName
        }
      }
    }
  }
}
""", "variables": {"first": limit, "offset": int(offset)}}).text)
    return jsontxt['data']['allUserPoints']['edges']

def getgtruserrank(id: int):
    """
    {
  "worldRecords": 0,
  "rank": 0,
  "points": 0
}

girl!
    """
    return json.loads(requests.post(queries.post_url, json={"query": """
    query MyQuery($user: Int) {
  allUsers(condition: {id: $user}) {
    edges {
      node {
        userPointsByIdUser {
          nodes {
            rank
            worldRecords
            points
          }
        }
      }
    }
  }
}""", "variables": {"user": id}}).text)['data']['allUsers']['edges'][0]['node']['userPointsByIdUser']['nodes'][0]

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
    with open("storage/playlist.zeeplist", 'w') as f:
        json.dump(pl, f, indent=2)

def renamepl(name):
    os.rename("storage/playlist.zeeplist", f"storage/{name}.zeeplist")

def undorename(name):
    os.rename(f"storage/{name}.zeeplist", "storage/playlist.zeeplist")

def addgtruser(discid: str, user: dict):
    with open("storage/users.json", 'r') as f:
        data = json.loads(f.read())
        data["linked"][discid] = user
        data["linked"][discid]["settings"] = {"notifs": {"RU": False, "RD": False, "WRST": False}}
        data["linked"][discid]["userdata"] = {"position": fwogutils.getusergtrposition(int(user["id"]))}
    with open("storage/users.json", 'w') as ft:
        json.dump(data, ft, indent=2)

def get_linked_users():
    with open("storage/users.json", 'r') as f:
        data = json.loads(f.read())
        return data['linked']

def gtrlb_shedule():
    times = []
    for x in range(24):
        times.append(datetime.time(hour=x, minute=5))
    return times

def setlinkedusersetting(setting: str, value, user):
    with open("storage/users.json", 'r') as f:
        data = json.loads(f.read())
        data["linked"][str(user)]["settings"]["notifs"][str(setting)] = value
        if setting == 'RU' and value is True:
            data["usercache"]["RUusers"].append(str(user))
            data["linked"][str(user)]["userdata"]["position"] = getgtruserrank(data["linked"][str(user)]["id"])['rank']
        if setting == 'RD' and value is True:
            data["usercache"]["RDusers"].append(str(user))
            data["linked"][str(user)]["userdata"]["position"] = getgtruserrank(data["linked"][str(user)]["id"])['rank']
        if setting == 'WRST' and value is True:
            data["usercache"]["WRSTusers"][str(data["linked"][str(user)]["id"])] = {"discid": str(user)}
        if setting == 'RU' and value is False:
            data["usercache"]["RUusers"].remove(str(user))
        if setting == 'RD' and value is False:
            data["usercache"]["RDusers"].remove(str(user))
        if setting == 'WRST' and value is False:
            data["usercache"]["WRSTusers"].pop(str(data["linked"][str(user)]["id"]))
    with open("storage/users.json", 'w') as ft:
        json.dump(data, ft, indent=2)

def getlinkedusersettings(user):
    with open("storage/users.json", 'r') as f:
        data = json.loads(f.read())
        return data["linked"][str(user)]["settings"]

def userislinked(id):
    with open("storage/users.json", 'r') as f:
        data = json.loads(f.read())
    if str(id) in data["linked"]:
        return True
    else:
        return False

def getRUusers():
    with open("storage/users.json", 'r') as f:
        data = json.loads(f.read())
        return data["usercache"]["RUusers"]

def getRDusers():
    with open("storage/users.json", 'r') as f:
        data = json.loads(f.read())
        return data["usercache"]["RDusers"]

def getWRSTusers():
    with open("storage/users.json", 'r') as f:
        data = json.loads(f.read())
        return data["usercache"]["WRSTusers"]

def getlinkeduserdata(user):
    with open("storage/users.json", 'r') as f:
        data = json.loads(f.read())
        return data["linked"][str(user)]["userdata"]

def setlinkedranking(user: str, pos: int):
    with open("storage/users.json", 'r') as f:
        data = json.loads(f.read())
        data["linked"][user]["userdata"]["position"] = pos
        with open("storage/users.json", 'w') as ft:
            json.dump(data, ft, indent=2)


def get_returnlist():
    with open("fwogutils/returnlist.txt", 'r') as read:
        return json.loads(read.read())["returnlist"]

def dump_returnlist(dump):
    with open("fwogutils/returnlist.txt", 'w') as write:
        dump = {"returnlist": dump}
        json.dump(dump, write)

def is_test_build():
    if bot.user.id == 1126430942924386315:
        return False
    else:
        return True

def getrankings(offset:int=0, limit:int=20) -> []:
    """
    {
    "points": 0,
    "rank": 0,
    "worldRecords":0,
    "steamName": "str",
    "steamId": int,
    "discordId": int
    }
    """
    req = requests.post(post_url, json={"query": queries.rankings, "variables": {"offset": offset, "limit": limit}})
    if req.status_code != 200:
        log(str(req.status_code))
        return False
    reqjson, formattedlist = json.loads(req.text), []
    for x in reqjson["data"]["allUserPoints"]["nodes"]:
        formattedlist.append({"points": x["points"], "rank": x["rank"], "worldRecords": x["worldRecords"],
                              "steamName": x["userByIdUser"]["steamName"], "discordId": x["userByIdUser"]["discordId"],
                              "steamId": x["userByIdUser"]["steamId"]})
    return formattedlist

def getnotifusers():
    """
    {
    "RUusers": ["userDiscordId"],
    "RDusers": ["userDiscordId"],
    "WRSTusers": {"userGtrId": {"discid": "userDiscordId"}}
    }
    """
    with open("storage/users.json", 'r') as readfile:
        users = json.loads(readfile.read())
    return users["usercache"]

def getstoreduser(discordid: str):
    """
    {
    "id": userGtrId,
    "steamName: "userSteamName",
    "steamId": "userSteamId",
    "settings": {},
    "userdata": {"position": int}
    }
    """
    with open("storage/users.json", 'r') as readfile:
        users = json.loads(readfile.read())
    try:
        return users["linked"][discordid]
    except KeyError:
        return False

def getusergtrposition(gtruserid: int) -> int:
    request = requests.post(queries.post_url, json={"query": queries.get_user_pos, "variables": {"id": gtruserid}})
    if request.status_code != 200:
        log(f"Error! code: {request.status_code}, error: #{request.text}")
        return False
    else:
        log(f"returning rank from user {gtruserid}")
        try:
            return json.loads(request.text)["data"]["allUsers"]["edges"][0]["node"]["userPointsByIdUser"]["edges"][0]["node"]["rank"]
        except IndexError:
            log("IndexError!")
            return False

async def getusergtrpositionasync(gtruserid: int) -> int:
    request = requests.post(queries.post_url, json={"query": queries.get_user_pos, "variables": {"id": gtruserid}})
    if request.status_code != 200:
        log(f"Error! code: {request.status_code}, error: #{request.text}")
        return False
    else:
        log(f"returning rank from user {gtruserid}")
        try:
            return json.loads(request.text)["data"]["allUsers"]["edges"][0]["node"]["userPointsByIdUser"]["edges"][0]["node"]["rank"]
        except IndexError:
            log("IndexError!")
            return False

def updateuserposition(user: str, updatedpos: int):
    with open("storage/users.json", 'r') as readfile:
        users = json.loads(readfile.read())
    users["linked"][user]["userdata"]["position"] = updatedpos
    with open("storage/users.json", 'w') as writefile:
        json.dump(users, writefile, indent=2)