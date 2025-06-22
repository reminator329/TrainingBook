from datetime import datetime

from .metamodel import *


class ExerciseType(JsonSerializable):
    def __init__(self, name: str = None):
        super().__init__()
        self.name = name

    def __lt__(self, other):
        if not isinstance(other, ExerciseType):
            return False
        return self.name < other.name


class ExerciseProgram(JsonSerializable):

    def __init__(self, exercise_template: ExerciseType, rest_time_seconds: int):
        super().__init__()
        self.exerciseTemplate = exercise_template
        self.restTimeSeconds = rest_time_seconds


class Exercise(JsonSerializable):
    def __init__(self, exercise_program: ExerciseProgram = None, weight: float = None, reps: int = None):
        super().__init__()
        self.exerciseProgram = exercise_program
        self.weight = weight
        self.reps = reps


class ProgramType(JsonSerializable):
    def __init__(self, name: str = None):
        super().__init__()
        self.name = name
        self.exercisePrograms: list[ExerciseProgram] = []  # (exercise, rest_time_seconds)

    def add_exercise_program(self, exercise_program: ExerciseProgram):
        self.exercisePrograms.append(exercise_program)


class Session(JsonSerializable):
    def __init__(self, template: ProgramType = None, date: datetime = None):
        super().__init__()
        self.template = template
        self.date = date
        self.results: list[Exercise] = []

    def add_exercise_result(self, exercise: Exercise) -> str | None:

        given_exercise_program = exercise.exerciseProgram

        if given_exercise_program not in self.template.exercisePrograms:
            return "Error : The exercise_program of this exercise " + str(exercise) + " is not in this program."

        if given_exercise_program in [exercise_result.exerciseProgram for exercise_result in self.results]:
            return "Error : The exercise_program of this exercise " + str(exercise) + " is already done."

        self.results.append(exercise)
        return None

    def is_program_invalid_according_exercise_programs(self) -> bool:
        for exerciseResult in self.results:
            if exerciseResult.exerciseProgram not in self.template.exercisePrograms:
                return True

        return False

    def is_program_completed(self) -> bool:
        if len(self.results) != len(self.template.exercisePrograms):
            return False

        for exercise in self.results:
            if exercise.exerciseProgram not in self.template.exercisePrograms:
                if self.is_program_invalid_according_exercise_programs():
                    print("Warning : This program is not valid.")
                return False

        return True
