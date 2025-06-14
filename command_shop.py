from enum import Enum
from typing import Literal

import discord
from discord import app_commands

import command


# Defines a custom Select containing colour options
# that the user can choose. The callback function
# of this class is called when the user changes their choice
class Dropdown(discord.ui.Select):
    def __init__(self):

        # Set the options that will be presented inside the dropdown
        options = [
            discord.SelectOption(label='Red', description='Your favourite colour is red', emoji='🟥'),
            discord.SelectOption(label='Green', description='Your favourite colour is green', emoji='🟩'),
            discord.SelectOption(label='Blue', description='Your favourite colour is blue', emoji='🟦'),
        ]

        # The placeholder is what will be shown when no option is chosen
        # The min and max values indicate we can only pick one of the three options
        # The options parameter defines the dropdown options. We defined this above
        super().__init__(placeholder='Choose your favourite colour...', min_values=1, max_values=1, options=options)

    async def callback(self, interaction: discord.Interaction):
        # Use the interaction object to send a response message containing
        # the user's favourite colour or choice. The self object refers to the
        # Select object, and the values attribute gets a list of the user's
        # selected options. We only want the first one.
        await interaction.response.send_message(f'Your favourite colour is {self.values[0]}')

# Define a simple View that gives us a counter button
class Counter(discord.ui.View):

    def __init__(self):

        super().__init__(timeout=10)
        self.message = None
        self.add_item(Dropdown())

    # Define the actual button
    # When pressed, this increments the number displayed until it hits 5.
    # When it hits 5, the counter button is disabled and it turns green.
    # note: The name of the function does not matter to the library
    @discord.ui.button(label='0', style=discord.ButtonStyle.red)
    async def count(self, interaction: discord.Interaction, button: discord.ui.Button):
        number = int(button.label) if button.label else 0
        if number + 1 >= 5:
            button.style = discord.ButtonStyle.green
            button.disabled = True
        button.label = str(number + 1)

        response = interaction.response
        assert isinstance(response, discord.InteractionResponse)
        # Make sure to update the message with our updated selves
        await response.edit_message(view=self)

    async def on_timeout(self):
        print("TIMEOUT")
        for child in self.children:
            print(str(type(child)))
            child.disabled = True
            child.style = discord.ButtonStyle.green

        # Optionnel : éditer le message pour montrer que c’est désactivé
        assert isinstance(self.message, discord.Message)
        await self.message.edit(view=self)


# Define a simple View that gives us a confirmation menu
class Confirm(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=10)
        self.value = None

    # When the confirm button is pressed, set the inner value to `True` and
    # stop the View from listening to more input.
    # We also send the user an ephemeral message that we're confirming their choice.
    @discord.ui.button(label='Confirm', style=discord.ButtonStyle.green)
    async def confirm(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_message('Confirming', ephemeral=True)
        self.value = True
        self.stop()

    # This one is similar to the confirmation button except sets the inner value to `False`
    @discord.ui.button(label='Cancel', style=discord.ButtonStyle.grey)
    async def cancel(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_message('Cancelling', ephemeral=True)
        self.value = False
        self.stop()

    async def on_timeout(self):
        self.value = False
        for child in self.children:
            print(str(type(child)))
            child.disabled = True
            child.style = discord.ButtonStyle.green

        # Optionnel : éditer le message pour montrer que c’est désactivé
        assert isinstance(self.message, discord.Message)
        await self.message.edit(view=self)
        self.stop()



class Fruits(Enum):
    apple = 0
    banana = 1
    cherry = 2
    dragonfruit = 3


@app_commands.describe(action='The action to do in the shop', item='The target item')
async def execute(interaction: discord.Interaction, action: Literal['Buy', 'Sell'], item: Fruits):
    response = interaction.response
    assert isinstance(response, discord.InteractionResponse)
    # await response.send_message(f'Action: {action}\nItem: {item.name} (value={item.value})')
    # We create the view and assign it to a variable so we can wait for it later.
    view = Confirm()
    await response.send_message('Do you want to continue?', view=view, ephemeral=False)

    # Wait for the View to stop listening for input...
    await view.wait()
    if view.value is None:
        print('Timed out...')
    elif view.value:
        print('Confirmed...')
    else:
        print('Cancelled...')

    view2 = Counter()


    sent_message = await interaction.channel.send("Compte", view=view2)
    view2.message = sent_message


class CommandShop(command.Command):

    def __init__(self):
        super().__init__("shop", "Interact with the shop", execute)
