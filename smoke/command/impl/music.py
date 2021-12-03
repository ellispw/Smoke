import asyncio

from discord.ext import commands

from smoke.command.command import Command
from smoke.embed.embed import Embed
from smoke.embed.embed_type import EmbedType


class Music(Command):
    def __init__(self, bot):
        super().__init__(bot=bot, name="Music", desc="Plays music in a voice channel",
                         perms=["smoke.music.play", "smoke.music.pause", "smoke.music.skip", "smoke.music.queue"])

    async def setup_player(self, ctx):
        embed = Embed.build(fields=[("Music Player", "Use the reactions to control the music.")],
                            member=ctx.author,
                            embed_type=EmbedType.INFO).get()
        msg = await ctx.channel.send(embed=embed)

        options = ["◀", "▶", "⏯", "⏹", "↕"]
        for option in options:
            await msg.add_reaction(option)

        def check_reaction(r, m):
            if r not in options or m != ctx.author or r.message != msg:
                return False

            return True

        try:
            reaction, member = await self.bot.wait_for("reaction_add", check=check_reaction, timeout=30)
        except asyncio.TimeoutError:
            await msg.clear_reactions()
        else:
            if reaction == "◀":
                pass
            elif reaction == "▶":
                pass
            elif reaction == "⏯":
                pass
            elif reaction == "⏹":
                # disconnect bot
                pass
            elif reaction == "↕":
                # queue
                pass

    @commands.command()
    @commands.guild_only()
    async def music(self, ctx):
        await self.setup_player(ctx)
