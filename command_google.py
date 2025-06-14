from urllib.parse import quote_plus

import discord
from discord import app_commands

import command

# Define a simple View that gives us a google link button.
# We take in `query` as the query that the command author requests for
class Google(discord.ui.View):
    def __init__(self, query: str):
        super().__init__()
        # we need to quote the query string to make a valid url. Discord will raise an error if it isn't valid.
        query = quote_plus(query)
        url = "https://www.google.com/search?q=" + query

        # Link buttons cannot be made with the decorator
        # Therefore we have to manually create one.
        # We add the quoted url to the button, and add the button to the view.
        self.add_item(discord.ui.Button(label='Click Here', url=url))

async def execute(interaction: discord.Interaction, query: str):
    response = interaction.response
    assert isinstance(response, discord.InteractionResponse)
    # await response.send_message(f'Action: {action}\nItem: {item.name} (value={item.value})')
    # We create the view and assign it to a variable so we can wait for it later.

    await response.send_message(f'Google Result for: `{query}`', view=Google(query))

class CommandGoogle(command.Command):

    def __init__(self):
        super().__init__("google", "Create google link", execute)
