from datetime import datetime
from metamodel import *

class ExerciseTemplate(JsonSerializable):
    def __init__(self, name: str = None):
        self.name = name


class ExerciseProgram(JsonSerializable):

    def __init__(self, exercise_template: ExerciseTemplate, rest_time_seconds: int):
        self.exercise_template = exercise_template
        self.rest_time_seconds = rest_time_seconds


class Exercise(JsonSerializable):
    def __init__(self, exercise: ExerciseTemplate = None, weight: float = None, reps: int = None):
        self.exercise = exercise
        self.weight = weight
        self.reps = reps


class ProgramTemplate(JsonSerializable):
    def __init__(self, name: str = None):
        self.name = name
        self.exercises: list[ExerciseProgram] = []  # (exercise, rest_time_seconds)

    def add_exercise(self, exercise_program: ExerciseProgram):
        self.exercises.append(exercise_program)


class Program(JsonSerializable):
    def __init__(self, template: ProgramTemplate = None, date: datetime = None):
        self.template = template
        self.date = date
        self.results: list[Exercise] = []
