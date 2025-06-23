import importlib
import json

import bson


def generate_id():
    return str(bson.ObjectId())


class JsonSerializable:

    def __init__(self, _id: str=None):

        self.id: str = _id if _id is not None else generate_id()

    def populate(self, hashmap: dict):

        for key, value in self.__dict__.items():
            if isinstance(value, JsonSerializable):
                if value.id in hashmap:
                    value = hashmap[value.id]
                else:
                    value.populate(hashmap)

            if isinstance(value, str):
                if value in hashmap:
                    value = hashmap[value]

            if isinstance(value, list):
                new_list = []
                for v in value:
                    if isinstance(v, JsonSerializable):
                        if v.id not in hashmap:
                            v.populate(hashmap)
                            new_list.append(v)
                        else:
                            new_list.append(hashmap[v.id])

                    if isinstance(v, str):
                        if v in hashmap:
                            new_list.append(hashmap[v])
                self.__setattr__(key, new_list)



    def dumps(self) -> str:
        return json.dumps(self.dump())

    def dump(self) -> dict:
        data: dict[str, str | dict | list] = {
            "_class": self.__class__.__name__,
            "_module": self.__class__.__module__
        }

        for key, value in self.__dict__.items():
            if isinstance(value, JsonSerializable):
                data[key] = value.dump()
            elif isinstance(value, list):
                data[key] = [
                    v.dump() if isinstance(v, JsonSerializable) else v
                    for v in value
                ]
            else:
                data[key] = value
        return data

    @classmethod
    def loads(cls, json_str: str) -> 'JsonSerializable':
        raw = json.loads(json_str)
        class_name = raw.pop("_class")
        module_name = raw.pop("_module")
        if not class_name or not module_name:
            raise ValueError("Missing _class or _module in JSON")

        module = importlib.import_module(module_name)
        target_cls = getattr(module, class_name)

        instance = target_cls.__new__(target_cls)

        for key, value in raw.items():
            if isinstance(value, dict) and "_class" in value:
                setattr(instance, key, JsonSerializable.loads(json.dumps(value)))
            elif isinstance(value, list):
                deserialized = [
                    JsonSerializable.loads(json.dumps(v)) if isinstance(v, dict) and "_class" in v else v
                    for v in value
                ]
                setattr(instance, key, deserialized)
            else:
                setattr(instance, key, value)

        return instance

    @classmethod
    def load(cls, dict_input: dict) -> 'JsonSerializable':
        raw = dict_input.copy()
        class_name = raw.pop("_class")
        module_name = raw.pop("_module")
        if not class_name or not module_name:
            raise ValueError("Missing _class or _module in JSON")

        module = importlib.import_module(module_name)
        target_cls = getattr(module, class_name)

        instance = target_cls.__new__(target_cls)

        for key, value in raw.items():
            if isinstance(value, dict) and "_class" in value:
                setattr(instance, key, JsonSerializable.loads(json.dumps(value)))
            elif isinstance(value, list):
                deserialized = [
                    JsonSerializable.loads(json.dumps(v)) if isinstance(v, dict) and "_class" in v else v
                    for v in value
                ]
                setattr(instance, key, deserialized)
            else:
                setattr(instance, key, value)

        return instance

    def __repr__(self):
        return self.__class__.__name__ + str(self.__dict__)
