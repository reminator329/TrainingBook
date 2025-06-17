import argparse
from typing import Optional

import discord
from discord import app_commands

from command_add import CommandAdd
from command_channel_infos import CommandChannelInfo
from command_feedback import CommandFeedback
from command_google import CommandGoogle
from command_graph import CommandGraph
from command_hello import CommandHello
from command_shop import CommandShop
from command_tictactoe import CommandTicTacToe
from command_training_create_exercise_template import CommandTrainingCreateExerciseTemplate
from command_training_create_program_type import CommandTrainingCreateProgramType

MY_GUILD = discord.Object(id=1379158112862212167)  # replace with your guild id


class MyClient(discord.Client):
    def __init__(self, *, intents: discord.Intents):
        super().__init__(intents=intents)
        # A CommandTree is a special type that holds all the application command
        # state required to make it work. This is a separate class because it
        # allows all the extra state to be opt-in.
        # Whenever you want to work with application commands, your tree is used
        # to store and work with them.
        # Note: When using commands.Bot instead of discord.Client, the bot will
        # maintain its own tree instead.
        #





        self.tree = app_commands.CommandTree(self)
        commands = {
            CommandHello(),
            CommandAdd(),
            CommandChannelInfo(),
            CommandShop(),
            CommandGraph(),
            CommandFeedback(),
            CommandGoogle(),
            CommandTicTacToe(),
            CommandTrainingCreateExerciseTemplate(),
            CommandTrainingCreateProgramType()
        }

        for command in commands:
            self.tree.add_command(command.get_discord_command())

    # In this basic example, we just synchronize the app commands to one guild.
    # Instead of specifying a guild to every command, we copy over our global commands instead.
    # By doing so, we don't have to wait up to an hour until they are shown to the end-user.
    async def setup_hook(self):
        # This copies the global commands over to your guild.
        self.tree.copy_global_to(guild=MY_GUILD)
        await self.tree.sync(guild=MY_GUILD)


if __name__ == "__main__":

    parser = argparse.ArgumentParser()
    parser.add_argument("--token", required=True, help="Discord bot token")
    args = parser.parse_args()

    intents = discord.Intents.all()
    client = MyClient(intents=intents)


    @client.event
    async def on_ready():
        print(f'Logged in as {client.user} (ID: {client.user.id})')
        print('------')



    # To make an argument optional, you can either give it a supported default argument
    # or you can mark it as Optional from the typing standard library. This example does both.
    @client.tree.command()
    @app_commands.describe(
        member='The member you want to get the joined date from; defaults to the user who uses the command')
    async def joined(interaction: discord.Interaction, member: Optional[discord.Member] = None):
        """Says when a member joined."""
        # If no member is explicitly provided then we use the command user here
        member = member or interaction.user

        response = interaction.response
        assert isinstance(response, discord.InteractionResponse)

        # The format_dt function formats the date time into a human readable representation in the official client
        await response.send_message(f'{member} joined {discord.utils.format_dt(member.joined_at)}')


    # A Context Menu command is an app command that can be run on a member or on a message by
    # accessing a menu within the client, usually via right clicking.
    # It always takes an interaction as its first parameter and a Member or Message as its second parameter.

    # This context menu command only works on members
    @client.tree.context_menu(name='Show Join Date')
    async def show_join_date(interaction: discord.Interaction, member: discord.Member):
        response = interaction.response
        assert isinstance(response, discord.InteractionResponse)

        # The format_dt function formats the date time into a human readable representation in the official client
        await response.send_message(f'{member} joined at {discord.utils.format_dt(member.joined_at)}')


    # This context menu command only works on messages
    @client.tree.context_menu(name='Report to Moderators')
    async def report_message(interaction: discord.Interaction, message: discord.Message):
        # We're sending this response message with ephemeral=True, so only the command executor can see it
        await interaction.response.send_message(
            f'Thanks for reporting this message by {message.author.mention} to our moderators.', ephemeral=True
        )

        # Handle report by sending it into a log channel
        log_channel = interaction.guild.get_channel(1381255453740236882)  # replace with your channel id

        embed = discord.Embed(title='Reported Message')
        if message.content:
            embed.description = message.content

        embed.set_author(name=message.author.display_name, icon_url=message.author.display_avatar.url)
        embed.timestamp = message.created_at

        url_view = discord.ui.View()
        url_view.add_item(discord.ui.Button(label='Go to Message', style=discord.ButtonStyle.url, url=message.jump_url))

        await log_channel.send(embed=embed, view=url_view)


    client.run(args.token)

# See PyCharm help at https://www.jetbrains.com/help/pycharm/
