import discord
import dotenv

from smoke.embed.embed_type import EmbedType


class Embed:
    def __init__(self, *, member=None, embed_type=EmbedType.INFO):
        color = 0

        if embed_type == EmbedType.INFO:
            color = 0x000000
        elif embed_type == EmbedType.ERROR:
            color = 0xff0000
        elif embed_type == EmbedType.SUCCESS:
            color = 0x00ff00

        self.embed = discord.Embed(color=color)
        self.embed.set_author(name=dotenv.dotenv_values()["BOT_NAME"])

        if member:
            self.embed.set_footer(text=f"{member.display_name}'s command", icon_url=member.avatar_url)

    def add_field(self, *, name, value, inline=True):
        self.embed.add_field(name=name, value=value, inline=inline)

    def get(self):
        return self.embed

    @staticmethod
    def build(*, fields, member=None, embed_type=EmbedType.INFO):
        embed = Embed(embed_type=embed_type, member=member)

        for field in fields:
            inline = True
            if len(field) == 3:
                inline = field[2]

            embed.add_field(name=field[0], value=field[1], inline=inline)

        return embed
