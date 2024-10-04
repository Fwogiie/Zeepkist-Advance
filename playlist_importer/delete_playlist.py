from fwogutils import bot
import requests

@bot.command()
async def delpl(ctx, plcode: str):
    if ctx.author.id == 785037540155195424:
        req = requests.post(f"https://fwogiiedev.com/api/playlists?customcode={plcode}&delete=True", json={})
        await ctx.send(f"`{req.status_code}` {req.text}")

print(f"| {__name__} loaded in")