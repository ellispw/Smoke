from discord import Forbidden
from discord.ext import commands

from smoke.command.command import Command
from smoke.embed.embed import Embed
from smoke.embed.embed_type import EmbedType
from smoke.permission.permission_handler import PermissionHandler


class Ban(Command):
    def __init__(self, bot):
        super().__init__(bot=bot, name="Ban", desc="Bans a member from the guild", perms=["smoke.ban"])

    @commands.command()
    @commands.guild_only()
    async def ban(self, ctx, member):
        if not await PermissionHandler.has_permissions(ctx.author, ctx.guild, "smoke.ban"):
            await ctx.channel.send(embed=PermissionHandler.invalid_perms_embed)
            return

        try:
            member.ban(reason="Smoke Bot Ban", delete_message_days=7)
            await ctx.channel.send(embed=Embed.build(fields=[(f"{member.display_name} Banned Successfully",
                                                              f"Successfully removed {member.display_name}"
                                                              f" from the guild")],
                                                     member=ctx.author, embed_type=EmbedType.SUCCESS))
        except Forbidden:
            await ctx.channel.send(
                embed=Embed.build(fields=[("Kick failed", f"I don't have permission to kick {ctx.author.name}!")],
                                  embed_type=EmbedType.ERROR).get())
