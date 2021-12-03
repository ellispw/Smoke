import discord
from discord.ext import commands

from smoke.command.command import Command
from smoke.embed.embed import Embed
from smoke.embed.embed_type import EmbedType
from smoke.permission.permission_handler import PermissionHandler


class Kick(Command):
    def __init__(self, bot):
        super().__init__(bot=bot, name="Kick", desc="Kicks a member from the guild", perms=["smoke.kick"])

    @commands.command()
    @commands.guild_only()
    async def kick(self, ctx, member: discord.Member):
        if not await PermissionHandler.has_permissions(ctx.author, ctx.guild, "smoke.kick"):
            await ctx.channel.send(embed=PermissionHandler.invalid_perms_embed)
            return

        try:
            await member.kick()
            await ctx.author.send(f"You have been kicked from '{ctx.guild.name}'.")
            await ctx.channel.send(
                embed=Embed.build(
                    fields=[("Kick successful", f"Member '{ctx.author.name}' kicked successfully.")],
                    member=ctx.author,
                    embed_type=EmbedType.SUCCESS).get())
        except discord.Forbidden:
            await ctx.channel.send(
                embed=Embed.build(fields=[("Kick failed", f"I don't have permission to kick {ctx.author.name}!")],
                                  embed_type=EmbedType.ERROR).get())
