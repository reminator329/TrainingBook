import discord
from discord import ui
from datetime import datetime

import command
import storage
import datamodel

class SessionInputModal(ui.Modal):
    def __init__(self, exercise_program: datamodel.ExerciseProgram):
        super().__init__(title=f"Saisie pour {exercise_program.exerciseTemplate.name}")
        self.result = None
        self.exercise_program = exercise_program

        self.weight = ui.TextInput(label="Poids (kg)", required=True)
        self.reps = ui.TextInput(label="Répétitions", required=True)

        self.add_item(self.weight)
        self.add_item(self.reps)

    async def on_submit(self, interaction: discord.Interaction):
        response = interaction.response
        assert isinstance(response, discord.InteractionResponse)
        await response.defer()


class DateInputModal(ui.Modal):
    def __init__(self):
        super().__init__(title="Date de la séance")
        self.date_input = ui.TextInput(
            label="Date de la séance (JJ/MM/AAAA)", placeholder="Par ex. : 22/06/2025", required=True
        )
        self.add_item(self.date_input)
        self.result_date: str | None = None

    async def on_submit(self, interaction: discord.Interaction):
        response = interaction.response
        assert isinstance(response, discord.InteractionResponse)

        try:
            # Validation simple du format
            date_obj = datetime.strptime(self.date_input.value, "%d/%m/%Y")
            self.result_date = date_obj.isoformat()
            await response.defer()  # Pas de message visible
        except ValueError:
            await response.send_message("❌ Format de date invalide. Utilisez JJ/MM/AAAA.", ephemeral=True)

        self.stop()

class SessionInProgressView(ui.View):
    def __init__(self, user: discord.User, program: datamodel.Program, session_date: str):
        super().__init__(timeout=1800)

        self.user = user
        self.program = program
        # self.session = datamodel.Session(template=program, date=datetime.now().isoformat())
        self.session = datamodel.Session(template=program, date=session_date)
        self.index = 0

        self.next_button = ui.Button(label=self.get_button_label(), style=discord.ButtonStyle.primary)
        self.cancel_button = ui.Button(label="Annuler", style=discord.ButtonStyle.danger)

        self.next_button.callback = self.send_modal
        self.cancel_button.callback = self.cancel_session

        self.add_item(self.next_button)
        self.add_item(self.cancel_button)

        self.previous_results_by_exercise_program_id: dict[str, list[datamodel.Exercise]] = {}
        self.load_previous_results()

    def format_previous_info(self, exercise_program_id: str) -> str:
        history = self.previous_results_by_exercise_program_id.get(exercise_program_id, [])
        if not history:
            return "*Aucune donnée précédente.*"

        # On limite à x dernières occurrences (les plus récentes à la fin)
        history = history[-10:]  # derniers, déjà dans l’ordre croissant

        return "\n".join([
            f"• {e.weight} kg x {e.reps}" for e in history
        ])

    def load_previous_results(self):
        bdd = storage.get_storage()
        user = bdd.get_user_from_user_id(self.user.id)

        sessions = user.sessions

        # On trie les sessions par date (de la plus ancienne à la plus récente)
        sessions.sort(key=lambda s: datetime.fromisoformat(s.date) if isinstance(s.date, str) else s.date)


        for session in sessions:
            if session.template == self.program:
                for ex in session.results:
                    key = ex.exerciseProgram.id
                    self.previous_results_by_exercise_program_id.setdefault(key, []).append(ex)

    def get_button_label(self):
        if self.index >= len(self.program.exercisePrograms):
            return "Terminer la séance"
        ep = self.program.exercisePrograms[self.index]
        return f"Exercice suivant ({ep.exerciseTemplate.name})"

    async def send_modal(self, interaction: discord.Interaction):
        if interaction.user != self.user:
            await interaction.response.send_message("❌ Ce menu ne vous appartient pas.", ephemeral=True)
            return

        if self.index >= len(self.program.exercisePrograms):
            await interaction.response.send_message("🎉 Séance terminée.", ephemeral=True)
            return

        modal = SessionInputModal(self.program.exercisePrograms[self.index])
        await interaction.response.send_modal(modal)
        await modal.wait()


        try:

            weight = float(modal.weight.value)
            reps = int(modal.reps.value)
            result = datamodel.Exercise(
                exercise_program=modal.exercise_program,
                weight=weight,
                reps=reps
            )

            error = self.session.add_exercise_result(result)

            if error:
                await interaction.channel.send(f"❌ {error}")
                return

            await interaction.channel.send(
                f"✅ Enregistré : {weight}kg x {reps} pour {modal.exercise_program.exerciseTemplate.name}"
            )

            await self.advance(interaction)

        except ValueError:
            await interaction.channel.send("Entrée invalide.")

    async def advance(self, interaction: discord.Interaction):
        self.index += 1
        if self.index >= len(self.program.exercisePrograms):
            # Sauvegarde de la séance
            bdd = storage.get_storage()
            user = datamodel.User(self.user.id, self.user.mention)
            bdd.upcreate_session_and_add_to_user(user, self.session)

            await interaction.followup.send("📅 Séance enregistrée avec succès !", ephemeral=True)
            self.clear_items()
            self.stop()
        else:
            # Met à jour le bouton
            self.next_button.label = self.get_button_label()

            ep = self.program.exercisePrograms[self.index]
            history_text = self.format_previous_info(ep.id)

            await interaction.followup.send(
                f"➡️ **Exercice suivant** : `{ep.exerciseTemplate.name}`\n"
                f"📈 **Historique :**\n{history_text}",
                ephemeral=True,
                view=self
            )

    async def cancel_session(self, interaction: discord.Interaction):
        if interaction.user != self.user:
            await interaction.response.send_message("❌ Ce menu ne vous appartient pas.", ephemeral=True)
            return
        await interaction.response.send_message("❌ Séance annulée.", ephemeral=True)
        self.clear_items()
        self.stop()


async def execute(interaction: discord.Interaction):
    bdd = storage.get_storage()
    programs = bdd.get_programs()

    if not programs:
        await interaction.response.send_message("Aucun programme trouvé.", ephemeral=True)
        return

    # Sélection du programme
    options = [discord.SelectOption(label=p.name, value=p.name) for p in programs]
    select = ui.Select(placeholder="Choisissez un programme", options=options)

    async def select_callback(inter: discord.Interaction):
        selected_program = next(p for p in programs if p.name == select.values[0])

        # Demander la date de la séance
        date_modal = DateInputModal()
        await inter.response.send_modal(date_modal)
        await date_modal.wait()

        if not date_modal.result_date:
            return  # L'utilisateur n'a pas soumis ou a entré une date invalide

        # Créer la vue de séance avec la date fournie
        view = SessionInProgressView(inter.user, selected_program, date_modal.result_date)
        await inter.followup.send(
            f"📋 Programme **{selected_program.name}** sélectionné pour le {date_modal.result_date[:10]} !",
            view=view,
            ephemeral=True
        )

    select.callback = select_callback

    view = ui.View()
    view.add_item(select)
    await interaction.response.send_message("🫠 Choisissez un programme :", view=view, ephemeral=True)


class CommandTrainingCreateSession(command.Command):
    def __init__(self):
        super().__init__("create-session", "Save a new session", execute)
