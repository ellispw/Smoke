from discord.ext import commands


class Command(commands.Cog):
    def __init__(self, *, bot, name, desc, perms, usage="None available"):
        self.name = name
        self.bot = bot
        self.desc = desc
        self.usage = usage
        self.perms = perms
