import json
import time
import glob

from smoke.embed.embed import Embed
from smoke.embed.embed_type import EmbedType


class PermissionHandler:
    invalid_perms_message = "You lack the required permissions to perform this command."
    invalid_perms_embed = Embed.build(fields=[("Invalid Permissions", invalid_perms_message)],
                                      embed_type=EmbedType.ERROR).get()

    cache = {}
    last_cache_update = 0

    @staticmethod
    async def from_disk():
        for path in glob.iglob("guilds/*.json"):
            with open(path, "r") as file:
                PermissionHandler.cache[path[path.index("\\") + 1:path.index(".")]] = json.loads(file.read())

    @staticmethod
    async def refresh_disk():
        for gid in PermissionHandler.cache:
            data = json.dumps(PermissionHandler.cache[gid])
            with open(f"guilds/{gid}.json", "w") as file:
                file.write(data)
                file.flush()

    @staticmethod
    async def get_permissions(member, guild):
        if "Smoke Operator" in [role.name for role in member.roles]:
            return ["*"]

        if PermissionHandler.last_cache_update == 0:
            await PermissionHandler.from_disk()

        # 5 minute cache update
        if time.time() - 60 * 5 > PermissionHandler.last_cache_update:
            await PermissionHandler.refresh_disk()
            PermissionHandler.last_cache_update = time.time()

        if str(guild.id) not in PermissionHandler.cache:
            return []

        if str(member.id) not in PermissionHandler.cache[str(guild.id)]:
            PermissionHandler.cache[str(guild.id)][str(member.id)] = []

        return PermissionHandler.cache[str(guild.id)][str(member.id)]

    @staticmethod
    async def has_permissions(member, guild, perm):
        return perm in await PermissionHandler.get_permissions(member, guild) \
               or "*" in await PermissionHandler.get_permissions(member, guild)

    @staticmethod
    async def add_permissions(member, guild, perms):
        if str(guild.id) not in PermissionHandler.cache:
            PermissionHandler.cache[str(guild.id)] = {}

        if str(member.id) not in PermissionHandler.cache[str(guild.id)]:
            PermissionHandler.cache[str(guild.id)][str(member.id)] = []

        current_perms = PermissionHandler.cache[str(guild.id)][str(member.id)]
        duplicates_removed = [perm for perm in perms if perm not in current_perms]
        PermissionHandler.cache[str(guild.id)][str(member.id)] = current_perms + duplicates_removed

    @staticmethod
    async def remove_permissions(member, guild, perms):
        if str(guild.id) not in PermissionHandler.cache or str(member.id) not in PermissionHandler.cache[str(guild.id)]:
            return

        current_perms = PermissionHandler.cache[str(guild.id)][str(member.id)]
        new_perms = [perm for perm in current_perms if perm not in perms]
        PermissionHandler.cache[str(guild.id)][str(member.id)] = new_perms
