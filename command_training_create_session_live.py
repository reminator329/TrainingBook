import discord
from discord import ui
from datetime import datetime
import asyncio

import command
import storage
import datamodel


class SessionInputModal(ui.Modal):
    def __init__(self, exercise_program: datamodel.ExerciseProgram):
        super().__init__(title=f"Saisie pour {exercise_program.exerciseTemplate.name}")
        self.exercise_program = exercise_program
        self.weight = ui.TextInput(label="Poids (kg)", required=True)
        self.reps = ui.TextInput(label="Répétitions", required=True)

        self.add_item(self.weight)
        self.add_item(self.reps)

    async def on_submit(self, interaction: discord.Interaction):
        response = interaction.response
        assert isinstance(response, discord.InteractionResponse)
        await response.defer()


class RealTimeSessionView(ui.View):
    def __init__(self, user: discord.User, program: datamodel.Program):
        super().__init__(timeout=1800)
        self.user = user
        self.program = program
        self.session = datamodel.Session(template=program, date=datetime.now().isoformat())
        self.index = 0
        self.message: discord.Message | None = None
        self.rest_task: asyncio.Task | None = None
        self.rest_remaining = 0
        self.x = 10

        self.next_button = ui.Button()
        self.next_button.label = self.get_button_label()
        self.next_button.style = discord.ButtonStyle.primary
        self.next_button.callback = self.send_modal

        self.skip_button = ui.Button()
        self.skip_button.label = "Passer le minuteur"
        self.skip_button.style = discord.ButtonStyle.success
        self.skip_button.disabled = True
        self.skip_button.callback = self.skip_rest

        self.cancel_button = ui.Button()
        self.cancel_button.label="Annuler"
        self.cancel_button.style = discord.ButtonStyle.danger
        self.cancel_button.callback = self.cancel_session


        self.add_item(self.next_button)
        self.add_item(self.skip_button)
        # self.add_item(self.cancel_button)

        self.previous_results_by_exercise_program_id: dict[str, list[datamodel.Exercise]] = {}
        self.load_previous_results()

    def get_button_label(self):
        if self.index >= len(self.program.exercisePrograms):
            return "Terminer la séance"
        return f"Exercice terminé"

    def load_previous_results(self):
        bdd = storage.get_storage()
        user = bdd.get_user_from_user_id(self.user.id)
        sessions = user.sessions
        sessions.sort(key=lambda s: datetime.fromisoformat(s.date) if isinstance(s.date, str) else s.date)

        for session in sessions:
            if session.template.id == self.program.id:
                for ex in session.results:
                    key = ex.exerciseProgram.id
                    self.previous_results_by_exercise_program_id.setdefault(key, []).append(ex)

    def format_previous_info(self, exercise_program_id: str) -> str:
        history = self.previous_results_by_exercise_program_id.get(exercise_program_id, [])
        if not history:
            return "*Aucune donnée précédente.*"

        history = history[-self.x:]
        res = ""
        for i, e in enumerate(history):
            if i == 0:
                res += f"\u2022 {e.weight} kg x {e.reps}"
            else:
                res += "\n"
                prev = history[i - 1]
                progress_weight = ":arrow_upper_right:" if prev.weight < e.weight else ":arrow_lower_right:" if prev.weight > e.weight else ":arrow_right:"
                progress_reps = ":arrow_upper_right:" if prev.reps < e.reps else ":arrow_lower_right:" if prev.reps > e.reps else ":arrow_right:"
                res += f"\u2022 {e.weight} kg {progress_weight} x {e.reps} {progress_reps}"
        return res

    async def send_modal(self, interaction: discord.Interaction):
        response = interaction.response
        assert isinstance(response, discord.InteractionResponse)

        if interaction.user != self.user:
            await response.send_message("❌ Ce menu ne vous appartient pas.")
            return

        if self.index >= len(self.program.exercisePrograms):
            await response.send_message("🎉 Séance terminée.")
            return

        modal = SessionInputModal(self.program.exercisePrograms[self.index])
        await response.send_modal(modal)
        await modal.wait()

        try:
            weight = float(modal.weight.value)
            reps = int(modal.reps.value)
            result = datamodel.Exercise(exercise_program=modal.exercise_program, weight=weight, reps=reps)

            error = self.session.add_exercise_result(result)
            if error:
                await interaction.followup.send(f"❌ {error}")
                return

            await interaction.followup.send(f"✅ Enregistré : {weight}kg x {reps} pour {modal.exercise_program.exerciseTemplate.name}")
            await self.start_rest_timer(interaction)

        except ValueError:
            await interaction.followup.send("Entrée invalide.")

    async def start_rest_timer(self, interaction: discord.Interaction):
        ep = self.program.exercisePrograms[self.index]
        self.rest_remaining = ep.restTimeSeconds
        self.skip_button.disabled = False
        self.next_button.disabled = True

        self.index += 1

        await self.send_next_exercise_message(interaction)

        if self.index < len(self.program.exercisePrograms):
            self.rest_task = asyncio.create_task(self.update_rest_loop(interaction))
        else:
            await self.end_rest(interaction)

    async def update_rest_loop(self, interaction: discord.Interaction):
        while self.rest_remaining > 0:
            await asyncio.sleep(5)
            self.rest_remaining -= 5
            await self.message.edit(content=self.get_content_for_next_exercise(), view=self)
        await self.end_rest(interaction)

    async def end_rest(self, interaction: discord.Interaction):
        self.skip_button.disabled = True
        self.next_button.disabled = False
        await self.message.edit(content=self.get_content_for_next_exercise(), view=self)

        if self.index >= len(self.program.exercisePrograms):
            bdd = storage.get_storage()
            user = datamodel.User(self.user.id, self.user.mention)
            bdd.upcreate_session_and_add_to_user(user, self.session)
            await interaction.followup.send("📅 Séance enregistrée avec succès !")
            self.clear_items()
            self.stop()

    async def skip_rest(self, interaction: discord.Interaction):
        if self.rest_task:
            self.rest_task.cancel()
        await self.end_rest(interaction)

    async def send_next_exercise_message(self, interaction: discord.Interaction):
        content = self.get_content_for_next_exercise()

        self.message = await interaction.followup.send(content, view=self)

    def get_content_for_next_exercise(self) -> str:
        if self.index >= len(self.program.exercisePrograms):
            return "🎉 Séance terminée."

        ep_next = self.program.exercisePrograms[self.index]
        history_text = self.format_previous_info(ep_next.id)

        # On récupère le temps de repos de l’exercice précédent (celui qu’on vient de faire)
        if self.index == 0:
            rest_time = 0
        else:
            ep_previous = self.program.exercisePrograms[self.index - 1]
            rest_time = ep_previous.restTimeSeconds

        minutes, seconds = divmod(rest_time, 60)
        remaining = max(self.rest_remaining, 0)

        return (
            f"➡️ **Exercice suivant** : `{ep_next.exerciseTemplate.name}`\n"
            f"📈 **Historique (" + str(self.x) + f" dernières) :**\n{history_text}\n\n"
            f"🕒 Temps de repos avant de commencer : {minutes}m {seconds}s\n"
            f"⏳ Temps restant : {remaining}s"
        )

    async def cancel_session(self, interaction: discord.Interaction):
        response = interaction.response
        assert isinstance(response, discord.InteractionResponse)

        if interaction.user != self.user:
            await response.send_message("❌ Ce menu ne vous appartient pas.")
            return
        await response.send_message("❌ Séance annulée.")
        self.clear_items()
        self.stop()


async def execute(interaction: discord.Interaction):
    response = interaction.response
    assert isinstance(response, discord.InteractionResponse)

    bdd = storage.get_storage()
    programs = bdd.get_programs()

    if not programs:
        await response.send_message("Aucun programme trouvé.")
        return

    options = [discord.SelectOption(label=p.name, value=p.name) for p in programs]
    select = ui.Select(placeholder="Choisissez un programme", options=options)

    async def select_callback(inter: discord.Interaction):
        response_callback = inter.response
        assert isinstance(response_callback, discord.InteractionResponse)

        selected_program = next(p for p in programs if p.name == select.values[0])
        view_callback = RealTimeSessionView(inter.user, selected_program)
        await response_callback.defer()
        await view_callback.send_next_exercise_message(inter)

    select.callback = select_callback

    view = ui.View()
    view.add_item(select)
    await response.send_message("🫠 Choisissez un programme :", view=view)


class CommandTrainingLiveSession(command.Command):
    def __init__(self):
        super().__init__("live-session", "Save a new session in real time", execute)
