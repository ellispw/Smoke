import json

from discord.ext import commands

from smoke.command.command import Command
from smoke.embed.embed import Embed
from smoke.embed.embed_type import EmbedType
from smoke.permission.permission_handler import PermissionHandler


class Lockdown(Command):
    def __init__(self, bot):
        super().__init__(bot=bot, name="Lockdown", desc="Locks down the server",
                         perms=["smoke.lockdown.enable", "smoke.lockdown.disable"])

    async def enter_lockdown(self, ctx):
        channel_ids = []

        for channel in ctx.guild.channels:
            # if read messages are on deny we want to save it
            if not channel.overwrites_for(ctx.guild.default_role).pair()[1].read_messages:
                channel_ids.append(channel.id)

            await channel.set_permissions(ctx.guild.default_role, read_messages=False)

        saved_members = {}

        for member in ctx.guild.members:
            if member.id not in saved_members:
                saved_members[member.id] = {}

            if "Lockdown Bypass" in [role.name for role in member.roles]:
                continue

            saved_members[member.id]["roles"] = [role.id for role in member.roles]
            perms = await PermissionHandler.get_permissions(member, ctx.guild)
            saved_members[member.id]["perms"] = perms
            await PermissionHandler.remove_permissions(member, ctx.guild, perms)
            for role in member.roles[1:]:
                try:
                    await member.remove_roles(role, reason="Lockdown")
                except Exception:
                    pass

        with open(f"guilds/{ctx.guild.id}.json", "r+") as file:
            guild_data = json.loads(file.read())
            guild_data["channel_backup"] = channel_ids
            guild_data["member_backup"] = saved_members
            file.seek(0)
            file.write(json.dumps(guild_data))
            file.truncate()

    async def disable_lockdown(self, ctx):
        guild_data = {}

        with open(f"guilds/{ctx.guild.id}.json", "r+") as file:
            guild_data = json.loads(file.read())

        for member in ctx.guild.members:
            if str(member.id) not in guild_data["member_backup"]:
                continue

            if "Lockdown Bypass" in [role.name for role in member.roles]:
                continue

            await PermissionHandler.add_permissions(member, ctx.guild,
                                                    guild_data["member_backup"][str(member.id)]["perms"])

            for role_id in guild_data["member_backup"][str(member.id)]["roles"]:
                role = [role for role in ctx.guild.roles if role.id == role_id]
                if role:
                    try:
                        await member.add_roles(role[0], reason="Lockdown")
                    except Exception:
                        pass

        for channel_id in guild_data["channel_backup"]:
            channel = [channel for channel in ctx.guild.channels if channel.id == int(channel_id)]
            if channel:
                try:
                    await channel[0].set_permissions(ctx.guild.default_role, read_messages=True)
                except Exception:
                    pass

    async def confirm_lockdown(self, ctx, message):
        embed = Embed.build(fields=[("Confirm Lockdown", message)], member=ctx.author).get()
        msg = await ctx.channel.send(embed=embed)
        await msg.add_reaction("👍")
        await msg.add_reaction("👎")

        def confirm_reaction(r, m):
            if m != ctx.author or r.message != msg:
                return False

            return True

        reaction, member = await self.bot.wait_for("reaction_add", check=confirm_reaction, timeout=30)

        if reaction.emoji == "👍":
            return True
        elif reaction.emoji == "👎":
            return False
        else:
            await ctx.channel.send(
                embed=Embed.build(fields=[("Invalid Response", "Please pick from the pre-reacted emojis.")],
                                  member=ctx.author, embed_type=EmbedType.ERROR).get())
            return await self.confirm_lockdown(ctx, message)

    @commands.command()
    @commands.guild_only()
    async def lockdown(self, ctx, action):
        if action == "enable":
            if not await PermissionHandler.has_permissions(ctx.author, ctx.guild, "smoke.lockdown.enable"):
                await ctx.channel.send(embed=PermissionHandler.invalid_perms_embed)
                return

            response = await self.confirm_lockdown(
                ctx,
                "Are you sure you want to enable lockdown mode? This will remove all roles of power and hide every "
                "currently visible channel.")

            if response:
                await ctx.channel.send(
                    embed=Embed.build(fields=[("Lockdown Commencing", "The server will now begin to lockdown.")],
                                      member=ctx.author, embed_type=EmbedType.INFO).get())

                await self.enter_lockdown(ctx)
            else:
                await ctx.channel.send(
                    embed=Embed.build(fields=[("Lockdown Cancelled", "The lockdown has been cancelled.")],
                                      member=ctx.author, embed_type=EmbedType.INFO).get())
                return
        elif action == "disable":
            if not await PermissionHandler.has_permissions(ctx.author, ctx.guild, "smoke.lockdown.disable"):
                await ctx.channel.send(embed=PermissionHandler.invalid_perms_embed)
                return

            response = await self.confirm_lockdown(
                ctx,
                "Are you sure you want to disable lockdown mode? This will restore your server to it's pre-lockdown "
                "state.")

            if response:
                await ctx.channel.send(
                    embed=Embed.build(fields=[("Lockdown Disabling", "The server will now begin to restore.")],
                                      member=ctx.author, embed_type=EmbedType.INFO).get())
                await self.disable_lockdown(ctx)
            else:
                await ctx.channel.send(
                    embed=Embed.build(fields=[("Lockdown Continuing", "The lockdown will continue to be enforced.")],
                                      member=ctx.author, embed_type=EmbedType.INFO).get())
        else:
            await ctx.channel.send(
                embed=Embed.build(fields=[("Unknown Action", "Unknown action. Please check command usage.")],
                                  embed_type=EmbedType.ERROR).get())
