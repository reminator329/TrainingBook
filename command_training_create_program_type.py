import discord
from discord import ui
from typing import Optional

import command
import datamodel
import storage


class ProgramNameModal(ui.Modal, title="Nom du programme"):
    name = ui.TextInput(label="Nom du programme", required=True)

    def __init__(self):
        super().__init__()
        self.result: Optional[str] = None

    async def on_submit(self, interaction: discord.Interaction):
        response = interaction.response
        assert isinstance(response, discord.InteractionResponse)

        self.result = self.name.value
        await response.defer()


class RestTimeModal(ui.Modal, title="Temps de repos"):
    def __init__(self, exercise_name: str):
        super().__init__()
        self.exercise_name = exercise_name
        self.rest_time = ui.TextInput(label="Temps de repos (en secondes)", placeholder="Ex: 60")
        self.result = None
        self.add_item(self.rest_time)

    async def on_submit(self, interaction: discord.Interaction):
        response = interaction.response
        assert isinstance(response, discord.InteractionResponse)
        try:
            self.result = int(self.rest_time.value)
            await response.defer()
        except ValueError:
            await response.send_message("Veuillez entrer un nombre entier valide.", ephemeral=True)

class ExerciseSelect(ui.Select):
    def __init__(self, exercises: list[datamodel.ExerciseTemplate]):
        options = [
            discord.SelectOption(label=ex.name, value=ex.name)
            for ex in exercises
        ]
        super().__init__(placeholder="Ajouter un exercice.", min_values=1, max_values=1, options=options)
        self.exercises = {e.name: e for e in exercises}

    async def callback(self, interaction: discord.Interaction):
        response = interaction.response
        assert isinstance(response, discord.InteractionResponse)

        selected_exercise = self.values[0]

        modal = RestTimeModal(selected_exercise)
        await response.send_modal(modal)
        await modal.wait()

        if modal.result is not None:
            view: ProgramBuilderView = self.view
            view.new_program.add_exercise_program(datamodel.ExerciseProgram(self.exercises[selected_exercise], modal.result))

            await interaction.followup.send(
                f"Ajouté : **{selected_exercise}** avec {modal.result}s de repos.",
                ephemeral=True
            )

            view.remove_item(self)
            new_select = ExerciseSelect(list(view.exercises_available.values()))
            view.select = new_select
            view.add_item(new_select)
            await interaction.message.edit(view=view)



class ProgramBuilderView(ui.View):
    def __init__(self, user: discord.User, new_program: datamodel.ProgramTemplate, exercises: list[datamodel.ExerciseTemplate]):
        super().__init__(timeout=3600)
        self.user = user
        self.new_program = new_program
        self.exercises_available = {e.name: e for e in exercises}
        self.finished = False

        self.select = ExerciseSelect(exercises)
        self.add_item(self.select)

    @ui.button(label="Terminer", style=discord.ButtonStyle.success)
    async def finish(self, interaction: discord.Interaction, button: discord.ui.Button):
        response = interaction.response
        assert isinstance(response, discord.InteractionResponse)

        if interaction.user != self.user:
            await response.send_message("Ce menu ne vous appartient pas.", ephemeral=True)
            return

        self.finished = True
        self.stop()
        await response.send_message("Programme terminé et enregistré !", ephemeral=True)

    async def on_timeout(self):
        print("ProgramBuilderView timed out")
        for child in self.children:
            child.disabled = True

        self.stop()


async def execute(interaction: discord.Interaction):
    response = interaction.response
    assert isinstance(response, discord.InteractionResponse)
    channel = interaction.channel

    # Étape 1 : entrer le nom du programme
    modal = ProgramNameModal()
    await response.send_modal(modal)
    await modal.wait()

    program_name = modal.result
    if not program_name:
        await channel.send("Nom du programme invalide.")
        return

    new_program = datamodel.ProgramTemplate(
        name=program_name
    )

    # Étape 2 : créer la view pour ajouter les exercices
    bdd = storage.get_storage()
    exercise_types = bdd.get_exercises_template()

    view = ProgramBuilderView(interaction.user, new_program, exercise_types)
    await channel.send(f"Ajoutons des exercices au programme **{program_name}** :", view=view)

    await view.wait()

    if view.finished:
        bdd.add_program_type(new_program)
    else:
        await channel.send("Création annulée ou expirée.", ephemeral=True)

class CommandTrainingCreateProgramType(command.Command):

    def __init__(self):
        super().__init__("create-program-type", "Save a new programme type", execute)