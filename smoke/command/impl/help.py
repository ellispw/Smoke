from discord.ext import commands

from smoke.command.command import Command
from smoke.embed.embed import Embed


class Help(Command):
    def __init__(self, bot):
        super().__init__(bot=bot, name="Help", desc="Displays this message!", perms=["smoke.help"])

    @commands.command()
    @commands.guild_only()
    async def help(self, ctx, cmd=None):
        cogs = [(cog.name, cog.desc) for cog in self.bot.cogs.values()]
        embed = Embed.build(fields=cogs, member=ctx.author)
        await ctx.channel.send(embed=embed.get())
