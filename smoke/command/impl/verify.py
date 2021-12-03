import asyncio
import os
import string

import discord
from discord.ext import commands

from smoke.command.command import Command
from captcha.image import ImageCaptcha
import random

from smoke.embed.embed import Embed
from smoke.embed.embed_type import EmbedType
from smoke.permission.permission_handler import PermissionHandler


class Verify(Command):
    def __init__(self, bot):
        super().__init__(bot=bot, name="Verify", desc="Verifies you're not a bot",
                         perms=["smoke.verify", "smoke.force_verify"])

    @staticmethod
    async def give_verify_role(guild, member, channel):
        verified_role = [r for r in guild.roles if r.name == "Verified"]

        if not verified_role:
            await channel.send("There is no 'Verified' role to give you!")
            return

        try:
            await member.add_roles(verified_role[0])
        except discord.Forbidden:
            await channel.send("I do not have permission to give you the 'Verified' role!")
            return

    @commands.command()
    @commands.guild_only()
    async def force_verify(self, ctx, member: discord.Member):
        if not PermissionHandler.has_permissions(ctx.author, ctx.guild, "smoke.force_verify"):
            await ctx.channel.send(embed=PermissionHandler.invalid_perms_embed)
            return

        await Verify.give_verify_role(ctx.guild, member, ctx.channel)
        await ctx.channel.send(f"{member.name} verified successfully")

    @commands.command()
    @commands.guild_only()
    async def verify(self, ctx):
        if "Verified" in [role.name for role in ctx.message.author.roles]:
            await ctx.channel.send(embed=Embed.build(
                fields=[("Already Verified", "You cannot use this command as you're already verified.")],
                member=ctx.author, embed_type=EmbedType.ERROR).get())
            return

        image = ImageCaptcha(width=300, height=80)

        s = "".join([random.choice(string.ascii_lowercase + string.ascii_uppercase) for i in range(0, 6)])
        image.write(s, f"{s}.png")

        image = discord.File(f"{s}.png")
        embed = discord.Embed()
        embed.add_field(name="Instructions", value="Please re-type the given string (case **INSENSITIVE**).")
        embed.set_image(url=f"attachment://{s}.png")

        await ctx.channel.send(embed=embed, file=image)
        os.remove(f"{s}.png")

        def confirm_message(m):
            return m.author == ctx.message.author and m.guild == ctx.guild

        try:
            msg = await self.bot.wait_for("message", check=confirm_message, timeout=30)
        except asyncio.TimeoutError:
            await ctx.channel.send("Timed out, please re-verify.")
        else:
            if msg.content.lower() == s.lower():
                await Verify.give_verify_role(ctx.guild, msg.author, msg.channel)
                await ctx.author.send(f"Successfully verified in guild: '{ctx.guild.name}'.")
            else:
                await ctx.send("Your message does not match the CAPTCHA, please re-verify.")
