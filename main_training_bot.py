import discord
import argparse


# Press the green button in the gutter to run the script.
if __name__ == "__main__":

    parser = argparse.ArgumentParser()
    parser.add_argument("--token", required=True, help="Discord bot token")
    args = parser.parse_args()

    # intents = discord.Intents.default()
    # intents.message_content = True

    intents = discord.Intents.all()
    client = discord.Client(intents=intents)

    @client.event
    async def on_ready():
        print("We have logged in as " + str(client.user))

    @client.event
    async def on_message(message):
        if message.author == client.user:
            return

        if message.content.startswith("$hello"):
            await message.channel.send("Hello You!")

    client.run(args.token)

# See PyCharm help at https://www.jetbrains.com/help/pycharm/
