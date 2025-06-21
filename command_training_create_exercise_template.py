import traceback

import discord

import command
import datamodel
import storage


class AddExerciseModal(discord.ui.Modal):

    def __init__(self):
        super().__init__(title="Ajouter un exercice")

        self.exercise_name = discord.ui.TextInput(
            label="Nom de l'exercice",
            placeholder="Ex: Développé couché",
            required=True,
            max_length=100
        )

        self.add_item(self.exercise_name)

    async def on_submit(self, interaction: discord.Interaction):
        response = interaction.response
        assert isinstance(response, discord.InteractionResponse)

        member = interaction.user
        assert isinstance(member, discord.Member)

        exercise_name = self.exercise_name.value.strip()

        user = datamodel.User(member.id, member.mention)
        exercise = datamodel.ExerciseType(exercise_name)

        bdd = storage.get_storage()
        bdd.upcreate_exercise_template_and_add_to_user(user, exercise)

        await response.send_message(user.mention + " Exercice ajouté : **" + str(exercise) + "** !", ephemeral=False)

    async def on_error(self, interaction: discord.Interaction, error: Exception) -> None:
        response = interaction.response
        assert isinstance(response, discord.InteractionResponse)
        await response.send_message('Oops! Something went wrong.', ephemeral=False)

        traceback.print_exception(type(error), error, error.__traceback__)

async def execute(interaction: discord.Interaction):
    response = interaction.response
    assert isinstance(response, discord.InteractionResponse)

    await response.send_modal(AddExerciseModal())


class CommandTrainingCreateExerciseTemplate(command.Command):

    def __init__(self):
        super().__init__("create-exercise", "Save a new exercise", execute)
