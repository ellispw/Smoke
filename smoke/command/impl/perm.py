import discord
from discord.ext import commands

from smoke.command.command import Command
from smoke.embed.embed import Embed
from smoke.embed.embed_type import EmbedType
from smoke.permission.permission_handler import PermissionHandler


class Perm(Command):
    def __init__(self, bot):
        super().__init__(bot=bot, name="Perm", desc="Permission-related commands",
                         perms=["smoke.perm.list", "smoke.perm.add", "smoke.perm.remove"])

    @commands.command()
    @commands.guild_only()
    async def perm(self, ctx, member: discord.Member, action, *args):
        if action == "add":
            if not await PermissionHandler.has_permissions(member, ctx.guild, "smoke.perm.add"):
                await ctx.channel.send(embed=PermissionHandler.invalid_perms_embed)
                return

            added_perms = ", ".join(list(args))

            await PermissionHandler.add_permissions(member, ctx.guild, list(args))
            await ctx.channel.send(embed=Embed.build(
                fields=[("Permission Add Successful",
                         f"Permissions [{added_perms}] successfully added to member {member.mention}.")],
                member=ctx.author,
                embed_type=EmbedType.SUCCESS).get())
        elif action == "list":
            if not await PermissionHandler.has_permissions(member, ctx.guild, "smoke.perm.list"):
                await ctx.channel.send(embed=PermissionHandler.invalid_perms_embed)
                return

            perms = await PermissionHandler.get_permissions(member, ctx.guild)
            await ctx.channel.send(
                embed=Embed.build(fields=[(f"{member.display_name}'s Permissions:", f"{', '.join(perms)}")],
                                  member=ctx.author,
                                  embed_type=EmbedType.INFO).get())
        elif action == "remove":
            if not await PermissionHandler.has_permissions(member, ctx.guild, "smoke.perm.remove"):
                await ctx.channel.send(embed=PermissionHandler.invalid_perms_embed)
                return

            removed_perms = ", ".join(list(args))

            await PermissionHandler.remove_permissions(member, ctx.guild, list(args))
            await ctx.channel.send(embed=Embed.build(
                fields=[("Permission Remove Successful",
                         f"Permissions [{removed_perms}] successfully removed from member {member.mention}.")],
                member=ctx.author,
                embed_type=EmbedType.SUCCESS).get())
        else:
            await ctx.channel.send(
                embed=Embed.build(fields=[("Unknown Action", "Unknown action. Please check command usage.")],
                                  embed_type=EmbedType.ERROR).get())
