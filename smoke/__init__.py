from discord.ext import commands
from discord import Intents, Client, client

from smoke.command.impl.help import Help
from smoke.command.impl.kick import Kick
from smoke.command.impl.lockdown import Lockdown
from smoke.command.impl.perm import Perm
from smoke.command.impl.verify import Verify

import dotenv

from smoke.embed.embed import Embed


class Smoke:
    def __init__(self):
        self.env = dotenv.dotenv_values()

        intents = Intents.default()
        intents.members = True
        self.bot = commands.Bot(command_prefix=self.env["PREFIX"], intents=intents)
        self.bot.remove_command("help")

        Embed.embed_bot = self.bot

        self.bot.add_cog(Verify(self.bot))
        self.bot.add_cog(Kick(self.bot))
        self.bot.add_cog(Help(self.bot))
        self.bot.add_cog(Perm(self.bot))
        self.bot.add_cog(Lockdown(self.bot))

        @self.bot.event
        async def on_error(event, *args, **kwargs):
            print(f"Error occurred in event {event}")

    def run(self):
        self.bot.run(self.env["TOKEN"])
