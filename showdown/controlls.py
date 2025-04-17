import json
import nextcord
import requests
from flask import request
import fwogutils
import showdown.leaderboards
from fwogutils import bot, log


get_level_query = """query MyQuery($workshopId: BigFloat = "") {
  allLevelItems(condition: {workshopId: $workshopId}) {
    nodes {
      name
      levelByIdLevel {
        hash
        id
      }
    }
  }
}"""

get_user_query = """query MyQuery($discordId: BigFloat = "") {
  allUsers(condition: {discordId: $discordId}) {
    nodes {
      steamId
      steamName
      id
    }
  }
}"""

#!!
@bot.slash_command(name="sd", guild_ids=[1127321762686836798])
async def sd_controlls(ctx):
    pass

# DONE
@sd_controlls.subcommand(name="set_map", description="MAP = map number beginning at 1 - USE 0 FOR QUALIFIER MAP!!")
async def sd_setmap(ctx, map: int, workshopid: int):
    log(f"Reached by {ctx.user}")
    if map <=7:
        if workshopid not in [0, -1]:
            req = requests.post(fwogutils.queries.post_url, json={"query": get_level_query, "variables": {"workshopId": workshopid}})
            if req.status_code != 200:
                await ctx.send(f"Error occurred. {req.status_code}")
                log(req.text)
                return
            resp = json.loads(req.text)
            resp = resp["data"]["allLevelItems"]["nodes"]
        else:
            resp = [{"levelByIdLevel": {"hash": 0}, "id": 0}]
        with open("showdown/storage.json", 'r') as read:
            stored = json.loads(read.read())
        if map == 0:
            stored["quali"] = {"hash": resp[0]["levelByIdLevel"]["hash"], "id": resp[0]["levelByIdLevel"]["id"]}
        else:
            stored[str(map)] = {"hash": resp[0]["levelByIdLevel"]["hash"], "id": resp[0]["levelByIdLevel"]["id"]}
        with open("showdown/storage.json", 'w') as write:
            json.dump(stored, write, indent=2)
        await ctx.send(f"{resp[0]['name']} added as map {map}")

# DONE
@bot.slash_command(name="register", description="Register for the Showdown event!", guild_ids=[1127321762686836798])
async def sd_register(ctx):
    req = requests.post(fwogutils.queries.post_url, json={"query": get_user_query, "variables": {"discordId": str(ctx.user.id)}})
    if req.status_code != 200:
        await ctx.send("Error occurred!")
        log(f"{req.status_code} - {req.text}")
        return
    resp = json.loads(req.text)
    resp = resp["data"]["allUsers"]["nodes"]
    if not resp:
        await ctx.send("You do not have GTR linked! Link it by going in your in-game mod settings!", ephemeral=True)
        return
    with open("showdown/storage.json", 'r') as read:
        stored = json.loads(read.read())
    if ctx.user.id in stored["regUsers"]:
        await ctx.send("You have already registered!", ephemeral=True)
        return
    stored["regUsers"].append(ctx.user.id)
    stored["regUsersBySteamId"].append(resp[0]["steamId"])
    stored["regUsersById"].append(resp[0]["id"])
    with open("showdown/storage.json", 'w') as write:
        json.dump(stored, write, indent=2)
    await ctx.send(f"You have registered under the name {resp[0]['steamName']}", ephemeral=True)
    await ctx.send(f"<@{ctx.user.id}> has registered!")

# DONE
@bot.slash_command(name="unregister", description="Unregister for the showdown event!", guild_ids=[1127321762686836798])
async def sd_unregister(ctx):
    with open("showdown/storage.json", 'r') as read:
        stored = json.loads(read.read())
    if ctx.user.id not in stored["regUsers"]:
        await ctx.send("You are not registered!", ephemeral=True)
        return
    userindex = stored["regUsers"].index(ctx.user.id)
    stored["regUsers"].pop(userindex)
    stored["regUsersBySteamId"].pop(userindex)
    stored["regUsersById"].pop(userindex)
    with open("showdown/storage.json", 'w') as write:
        json.dump(stored, write, indent=2)
    await ctx.send("Successfully Unregistered!", ephemeral=True)
    await ctx.send(f"{ctx.user.mention} Has unregistered!")

@sd_controlls.subcommand(name="set_quali_end_time")
async def sd_setqualiendtime(ctx, iso: str):
    with open("showdown/storage.json", 'r') as read:
        stored = json.loads(read.read())
    stored["endTime"] = iso
    with open("showdown/storage.json", 'w') as write:
        json.dump(stored, write, indent=2)
    await ctx.send(f"Alright, We'll be ending at {iso}")

@sd_controlls.subcommand(name="set_qualifier_channel")
async def sd_set_qualifier_channel(ctx, channel: nextcord.TextChannel, season: int):
    message = await channel.send(f"# Showdown Qualifier Season {season}", embed=nextcord.Embed(title=f"Showdown Qualifier Season {season}", description="Please hang on tight as we are setting up this leaderboard!", color=nextcord.Color.green()))
    with open("showdown/storage.json", 'r') as read:
        stored = json.loads(read.read())
    stored["qualiLb"] = {"channel": channel.id, "message": message.id}
    with open("showdown/storage.json", 'w') as write:
        json.dump(stored, write, indent=2)
    await ctx.send("Alright, Message has been sent and stored!")

@sd_controlls.subcommand(name="force_update_qualifier")
async def sd_force_update_qualifier(ctx):
    await showdown.leaderboards.update_qualifier()
    await ctx.send("Forced!")

@sd_controlls.subcommand(name="toggle_update_quali")
async def sd_toggle_update(ctx):
    with open("showdown/storage.json", 'r') as read:
        stored = json.loads(read.read())
    if stored["update?"] == True:
        stored["update?"] = False
        await ctx.send("Disabled updating of qualifier leaderboard.")
    elif stored["update?"] == False:
        stored["update?"] = True
        await ctx.send("Enabled updating of qualifier leaderboard.")
    with open("showdown/storage.json", 'w') as write:
        json.dump(stored, write, indent=2)

@sd_controlls.subcommand(name="kick")
async def sd_setqualiendtime(ctx, discordid: str):
    with open("showdown/storage.json", 'r') as read:
        stored = json.loads(read.read())
    userindex = stored["regUsers"].index(int(discordid))
    stored["regUsers"].pop(userindex)
    stored["regUsersBySteamId"].pop(userindex)
    stored["regUsersById"].pop(userindex)
    with open("showdown/storage.json", 'w') as write:
        json.dump(stored, write, indent=2)
    await ctx.send(f"Got <@{discordid}> the out of this event.")