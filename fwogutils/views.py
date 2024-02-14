import datetime
import time
import aiohttp
import requests
import json
import os
import nextcord
import re
import discord
from discord.ext import commands, tasks
from nextcord.errors import HTTPException
import privaat
import urllib
from urllib.parse import quote
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
import inspect
import pytz
import calendar
import subprocess
import ast
import copy
import sys
import fwogutils
from fwogutils import bot as bot
from fwogutils import log as log
from fwogutils import format_time as format_time
from nextcord import webhook, Webhook
import random
from nextcord.components import Button


gtrrankings = fwogutils.getgtruserrankings(limit=100, offset=0)
class LButtons(nextcord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @nextcord.ui.button(label="Show more", style=nextcord.ButtonStyle.grey)
    async def show_more(self, button: nextcord.Button, ctx: nextcord.Interaction):
        log(f"reached by {ctx.user} ({ctx.user.id})")
        stringedrankings = ""
        stringranks = ""
        strranks = ""
        for x in gtrrankings["rankings"][:30]:
            stringedrankings += f"{x['position']}. `{x['user']['steamName']}` with **{x['score']}** points and **{x['amountOfWorldRecords']}** World Records\n"
        for x in gtrrankings["rankings"][30:60]:
            stringranks += f"{x['position']}. `{x['user']['steamName']}` with **{x['score']}** points and **{x['amountOfWorldRecords']}** World Records\n"
        for x in gtrrankings["rankings"][60:90]:
            strranks += f"{x['position']}. `{x['user']['steamName']}` with **{x['score']}** points and **{x['amountOfWorldRecords']}** World Records\n"
        embed = discord.Embed(title="GTR Rankings", description=stringedrankings, color=nextcord.Color.blue())
        embeda = discord.Embed(title=" ", description=stringranks, color=nextcord.Color.blue())
        embedb = discord.Embed(title=" ", description=strranks, color=nextcord.Color.blue())
        await ctx.send(embeds=[embed, embeda, embedb], ephemeral=True)

    @nextcord.ui.button(label="My ranking")
    async def my_rank(self, button: nextcord.Button, ctx: nextcord.Interaction):
        log(f"reached by {ctx.user} ({ctx.user.id})")
        userid = ctx.user.id
        ctx = await ctx.send("processing", ephemeral=True)
        linked = fwogutils.get_linked_users()
        if str(userid) in linked:
            log(f"user had gtr linked, showing rank!")
            userrank = fwogutils.getgtruserrank(linked[str(userid)]["id"])
            closeranks = fwogutils.getgtruserrankings(limit=userrank['position']+5, offset=userrank['position']-6)
            ranks = ""
            for x in closeranks["rankings"]:
                if x['position'] != userrank['position']:
                    ranks += f"{x['position']}. `{x['user']['steamName']}` with **{x['score']}** points and **{x['amountOfWorldRecords']}** World Records\n"
                else:
                    ranks += f"> {x['position']}. `{x['user']['steamName']}` with **{x['score']}** points and **{x['amountOfWorldRecords']}** World Records\n"
            embed = discord.Embed(title="Your Rank", description=ranks, color=nextcord.Color.blue())
            await ctx.edit(embed=embed)
        else:

            log(f"user did not have gtr linked!")
            await ctx.edit("You did not link your GTR! use `/link gtr` to do so!")