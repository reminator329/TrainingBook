import discord.app_commands
from discord import AppCommandContext, AppInstallationType
from discord.app_commands import Group, CommandTree
from discord.utils import MISSING


class Command:

    def __init__(self,
                 name: str,
                 description: str,
                 callback: callable,
                 nsfw: bool = False,
                 parent: Group = None,
                 guild_ids=None,
                 allowed_contexts: AppCommandContext = None,
                 allowed_installs: AppInstallationType = None,
                 auto_locale_strings: bool = True,
                 extras=MISSING):

        self.discord_command = discord.app_commands.Command(
            name=name,
            description=description,
            callback=callback,
            nsfw=nsfw,
            parent=parent,
            guild_ids=guild_ids,
            allowed_contexts=allowed_contexts,
            allowed_installs=allowed_installs,
            auto_locale_strings=auto_locale_strings,
            extras=extras,
        )

    def get_discord_command(self):
        return self.discord_command
