import importlib
import json


class JsonSerializable:
    def dumps(self) -> str:
        data = {}
        for key, value in self.__dict__.items():
            if isinstance(value, JsonSerializable):
                data[key] = json.loads(value.dumps())
            elif isinstance(value, list):
                data[key] = [
                    json.loads(v.dumps()) if isinstance(v, JsonSerializable) else v
                    for v in value
                ]
            else:
                data[key] = value

        data["_class"] = self.__class__.__name__
        data["_module"] = self.__class__.__module__
        return json.dumps(data)

    @classmethod
    def loads(cls, json_str: str) -> 'JsonSerializable':
        raw = json.loads(json_str)
        class_name = raw.pop("_class", None)
        module_name = raw.pop("_module", None)
        if not class_name or not module_name:
            raise ValueError("Missing _class or _module in JSON")

        # Import dynamique
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