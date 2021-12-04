import asyncio
import re
import urllib.request

from discord.ext import commands

from smoke.command.command import Command
from smoke.embed.embed import Embed
from smoke.embed.embed_type import EmbedType
from smoke.permission.permission_handler import PermissionHandler


class Music(Command):
    queue = {}

    def __init__(self, bot):
        super().__init__(bot=bot, name="Music", desc="Plays music in a voice channel",
                         perms=["smoke.music", "smoke.music.play", "smoke.music.pause", "smoke.music.skip",
                                "smoke.music.disconnect", "smoke.music.queue"])

    @staticmethod
    async def search_youtube(self, keyword):
        html = urllib.request.urlopen("https://www.youtube.com/results?search_query=" + keyword)
        video_ids = re.findall(r"watch\?v=(\S{11})", html.read().decode())

        if not video_ids:
            return "https://www.youtube.com/watch?v=0lhhrUuw2N8"

        return f"https://www.youtube.com/watch?v={video_ids[0]}"

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
                def check_message(m):
                    if m.channel != msg.channel:
                        return False

                    return True

                song_name = await self.bot.wait_for("message", check=check_message)

    @commands.command()
    @commands.guild_only()
    async def music(self, ctx):
        if not PermissionHandler.has_permissions(ctx.author, ctx.guild, "smoke.music"):
            await ctx.channel.send(embed=PermissionHandler.invalid_perms_embed)
            return

        await self.setup_player(ctx)
