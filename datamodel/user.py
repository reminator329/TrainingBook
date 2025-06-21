from .training import *

class User(JsonSerializable):

    def __init__(self, user_id: int, mention: str):
        super().__init__()

        self.userId = user_id
        self.mention = mention
        self.exerciseTypes: list[ExerciseType] = []
        self.programTypes: list[ProgramType] = []