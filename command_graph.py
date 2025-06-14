from typing import NamedTuple

import discord
from discord import app_commands

import command


class Point(NamedTuple):
    x: int
    y: int


# The default transformer takes in a string option and you can transform
# it into any value you'd like.
#
# Transformers also support various other settings such as overriding
# properties like `choices`, `max_value`, `min_value`, `type`, or `channel_types`.
# However, this is outside of the scope of this example so check the documentation
# for more information.
class PointTransformer(app_commands.Transformer):
    async def transform(self, interaction: discord.Interaction, value: str) -> Point:
        (x, _, y) = value.partition(',')
        return Point(x=int(x.strip()), y=int(y.strip()))


# For more basic transformers for your own types without too much repetition,
# a concept known as "inline transformers" is supported. This allows you to use
# a classmethod to have a string based transformer. It's only useful
# if you only care about transforming a string to a class and nothing else.
class Point3D(NamedTuple):
    x: int
    y: int
    z: int

    # This is the same as the above transformer except inline
    @classmethod
    async def transform(cls, interaction: discord.Interaction, value: str):
        x, y, z = value.split(',')
        return cls(x=int(x.strip()), y=int(y.strip()), z=int(z.strip()))


async def execute(
        interaction: discord.Interaction,
        # In order to use the transformer, you should use Transform to tell the
        # library to use it.
        point: app_commands.Transform[Point, PointTransformer],
        point3d: Point3D
):
    response = interaction.response
    assert isinstance(response, discord.InteractionResponse)
    await response.send_message(str(point) + " " + (str(point3d)))


class CommandGraph(command.Command):

    def __init__(self):
        super().__init__("graphe", "Oui", execute)
