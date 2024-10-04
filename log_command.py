from fwogutils import bot, log
import nextcord
from nextcord.errors import HTTPException

@bot.is_owner
@bot.command(name="log")
async def ownlog(ctx, type: str, *, text: str = None):
    try:
        if type == "send" and text is None:
            await ctx.reply("yes ma'am", file=nextcord.File("log.txt"))
        elif type == "send" and text == "true":
            with open("log.txt", 'r') as fr:
                ctn = {1: "", 2: 0, 3: 5}
                block = False
                splitted = fr.read().split('\n')
                while block is False:
                    logblock = splitted[ctn[2]:ctn[3]]
                    if logblock:
                        for x in logblock:
                            ctn[1] += f"{x}\n"
                        ctn[3] += 5
                        ctn[2] += 5
                        await ctx.send(f"```{ctn[1]}```")
                        ctn[1] = ""
                    else:
                        block = True
        elif type == "add":
            log(text)
            await ctx.reply(f"Added `{text}` to log.txt")
        elif type == "clear":
            log("bruh", "clear")
            await ctx.reply("cleared log.txt")
        else:
            await ctx.reply("Yo fucking stupid bruv?")
    except HTTPException as ewwor:
        await ctx.send(f"HTTPSException: {ewwor}")

print(f"| {__name__} loaded in")