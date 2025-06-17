from datetime import datetime

from .metamodel import *


class ExerciseTemplate(JsonSerializable):
    def __init__(self, name: str = None):
        self.name = name

    def __lt__(self, other):
        if not isinstance(other, ExerciseTemplate):
            return False
        return self.name < other.name


class ExerciseProgram(JsonSerializable):

    def __init__(self, exercise_template: ExerciseTemplate, rest_time_seconds: int):
        self.exercise_template = exercise_template
        self.rest_time_seconds = rest_time_seconds


class Exercise(JsonSerializable):
    def __init__(self, exercise_program: ExerciseProgram = None, weight: float = None, reps: int = None):
        self.exercise_program = exercise_program
        self.weight = weight
        self.reps = reps


class ProgramTemplate(JsonSerializable):
    def __init__(self, name: str = None):
        self.name = name
        self.exercise_programs: list[ExerciseProgram] = []  # (exercise, rest_time_seconds)

    def add_exercise_program(self, exercise_program: ExerciseProgram):
        self.exercise_programs.append(exercise_program)


class Program(JsonSerializable):
    def __init__(self, template: ProgramTemplate = None, date: datetime = None):
        self.template = template
        self.date = date
        self.results: list[Exercise] = []

    def add_exercise_result(self, exercise: Exercise) -> str | None:

        given_exercise_program = exercise.exercise_program

        if given_exercise_program not in self.template.exercise_programs:
            return "Error : The exercise_program of this exercise " + str(exercise) + " is not in this program."

        if given_exercise_program in [exercise_result.exercise_program for exercise_result in self.results]:
            return "Error : The exercise_program of this exercise " + str(exercise) + " is already done."

        self.results.append(exercise)
        return None

    def is_program_invalid_according_exercise_programs(self) -> bool:
        for exercise_result in self.results:
            if exercise_result.exercise_program not in self.template.exercise_programs:
                return True

        return False

    def is_program_completed(self) -> bool:
        if len(self.results) != len(self.template.exercise_programs):
            return False

        for exercise in self.results:
            if exercise.exercise_program not in self.template.exercise_programs:
                if self.is_program_invalid_according_exercise_programs():
                    print("Warning : This program is not valid.")
                return False

        return True
