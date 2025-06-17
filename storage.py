# storage/base.py
import json
import os
from abc import ABC, abstractmethod
from typing import List
import datamodel

class StorageInterface(ABC):

    @abstractmethod
    def get_exercises_template(self) -> List[datamodel.ExerciseTemplate]:
        pass

    @abstractmethod
    def add_exercise_template(self, exercise: datamodel.ExerciseTemplate) -> None:
        pass

    @abstractmethod
    def add_program_type(self, program_type: datamodel.ProgramTemplate) -> None:
        pass

class JsonStorage(StorageInterface):
    _instance: 'JsonStorage' = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self, path="data.json"):
        if getattr(self, "_initialized", False):
            return
        self.path = path
        self.data = {
            "exercisesTemplate": [],
            "programs": [],
            "sessions": []
        }
        self._load()
        self._initialized = True

    def _load(self):
        if not os.path.exists(self.path):
            with open(self.path, "w", encoding="utf-8") as f:
                json.dump(self.data, f)

        f = open(self.path, "r", encoding="utf-8")
        data_file_json = json.load(f)
        if data_file_json != "":
            self.data = data_file_json
        f.close()

        if data_file_json == "":
            self._save()

    def _save(self):
        print(str(self.data))
        f = open(self.path, "w", encoding="utf-8")
        json.dump(self.data, f, indent=4)
        f.close()

    def get_exercises_template(self) -> List[datamodel.ExerciseTemplate]:
        exercise_types = []
        for exerciseType_json in self.data["exercisesTemplate"]:
            print(str(exerciseType_json))
            exercise_types.append(datamodel.ExerciseTemplate.load(exerciseType_json))
        exercise_types.sort()
        return exercise_types

    def add_exercise_template(self, exercise_template: datamodel.ExerciseTemplate):
        if exercise_template not in self.data["exercisesTemplate"]:
            self.data["exercisesTemplate"].append(exercise_template.dump())
            self._save()


    def add_program_type(self, program_type: datamodel.ProgramTemplate) -> None:
        if program_type.name not in [p["name"] for p in self.data["programs"]]:
            self.data["programs"].append(program_type.dump())
            self._save()


def get_storage() -> StorageInterface:
    return JsonStorage()