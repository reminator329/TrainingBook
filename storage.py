import json
import os
from abc import ABC, abstractmethod
from typing import List

import datamodel


class StorageInterface(ABC):

    @abstractmethod
    def get_exercises_template(self) -> List[datamodel.ExerciseType]:
        pass

    @abstractmethod
    def get_programs(self) -> List[datamodel.Program]:
        pass

    @abstractmethod
    def upcreate_exercise_template_and_add_to_user(self, user: datamodel.User,
                                                   exercise: datamodel.ExerciseType) -> None:
        pass

    @abstractmethod
    def upcreate_program_type_and_add_to_user(self, user: datamodel.User, program_type: datamodel.Program) -> None:
        pass

    @abstractmethod
    def upcreate_session_and_add_to_user(self, user: datamodel.User, session: datamodel.Session) -> None:
        pass

    @abstractmethod
    def get_user_from_user_id(self, user_id: int) -> datamodel.User:
        pass


class JsonStorage(StorageInterface):

    _instance: 'JsonStorage' = None

    DB_KEY_EXERCISE_TYPES = "exerciseTypes"
    DB_KEY_PROGRAMS = "programs"
    DB_KEY_USERS = "users"
    DB_KEY_SESSIONS = "sessions"

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self, path="data.json"):
        if getattr(self, "_initialized", False):
            return
        self.path = path
        self.data: dict = {
            JsonStorage.DB_KEY_EXERCISE_TYPES: [],
            JsonStorage.DB_KEY_PROGRAMS: [],
            JsonStorage.DB_KEY_USERS: [],
            JsonStorage.DB_KEY_SESSIONS: []
        }
        self.db_objects_by_id: dict = {}
        self._load()
        self._initialized = True

    def _init_db(self):
        file = open(self.path, "w", encoding="utf-8")
        json.dump(self.data, file)
        file.close()

    def _load(self):

        # Init DB if file not exist
        if not os.path.exists(self.path):
            self._init_db()

        # Load DB file
        f = open(self.path, "r", encoding="utf-8")
        data_file_json = json.load(f)
        f.close()

        # Create data model objects from json
        for key, json_objects in data_file_json.items():
            for json_object in json_objects:
                model_object = datamodel.JsonSerializable.load(json_object)
                model_object.populate(self.db_objects_by_id)
                self.db_objects_by_id[model_object.id] = model_object
                self.data[key].append(model_object)

    def _save(self):
        print(str(self.data))
        f = open(self.path, "w", encoding="utf-8")
        json.dump(self.data, f, indent=4, default=lambda o: o.dump())
        f.close()

    def get_exercises_template(self) -> List[datamodel.ExerciseType]:
        exercise_types = []
        for exerciseType in self.data[JsonStorage.DB_KEY_EXERCISE_TYPES]:
            print(str(exerciseType))
            assert isinstance(exerciseType, datamodel.ExerciseType)
            exercise_types.append(datamodel.ExerciseType.load(exerciseType.dump()))
        exercise_types.sort()
        return exercise_types

    def get_programs(self) -> List[datamodel.Program]:
        programs = []
        for program in self.data[JsonStorage.DB_KEY_PROGRAMS]:
            assert isinstance(program, datamodel.Program)
            programs.append(datamodel.Program.load(program.dump()))
        programs.sort()
        return programs

    def get_user_from_user_id(self, user_id: int) -> datamodel.User:
        user = None
        for user in self.data[JsonStorage.DB_KEY_USERS]:
            if user.userId == user_id:
                return datamodel.User.load(user.dump())
        return user

    def upcreate_json_serializable(self, json_serializable: datamodel.JsonSerializable, json_storate_key):

        object_in_db = None
        for object_candidate in self.data[json_storate_key]:
            if object_candidate.id == json_serializable.id:
                object_in_db = object_candidate
                break

        if object_in_db is not None:
            json_serializable.id = object_in_db.id
            self.data[JsonStorage.DB_KEY_USERS].remove(object_in_db)

        self.data[json_storate_key].append(json_serializable)
        self._save()

    def upcreate_user(self, user: datamodel.User):
        self.upcreate_json_serializable(user, JsonStorage.DB_KEY_USERS)

    def upcreate_exercise_template_and_add_to_user(self, user: datamodel.User, exercise_template: datamodel.ExerciseType):
        self.upcreate_json_serializable(exercise_template, JsonStorage.DB_KEY_EXERCISE_TYPES)

        user_in_db = self.get_user_from_user_id(user.userId)
        if user_in_db is None:
            user_in_db = user

        user_in_db.exerciseTypes.append(exercise_template)
        self.upcreate_user(user_in_db)

    def upcreate_program_type_and_add_to_user(self, user: datamodel.User, program_type: datamodel.Program) -> None:
        self.upcreate_json_serializable(program_type, JsonStorage.DB_KEY_PROGRAMS)

        user_in_db = self.get_user_from_user_id(user.userId)
        if user_in_db is None:
            user_in_db = user

        user_in_db.programTypes.append(program_type)
        self.upcreate_user(user_in_db)

    def upcreate_session_and_add_to_user(self, user: datamodel.User, session: datamodel.Session) -> None:
        self.upcreate_json_serializable(session, JsonStorage.DB_KEY_SESSIONS)

        user_in_db = self.get_user_from_user_id(user.userId)
        if user_in_db is None:
            user_in_db = user

        user_in_db.sessions.append(session)
        self.upcreate_user(user_in_db)



def get_storage() -> StorageInterface:
    return JsonStorage()
