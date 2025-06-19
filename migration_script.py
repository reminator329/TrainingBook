import json
from logging import fatal

import datamodel

file_data = open("data.json", "r")

data_json = json.load(file_data)

file_data.close()

object_to_check = [value for value in data_json.values()]
while len(object_to_check) > 0:

    obj = object_to_check.pop()

    if isinstance(obj, dict):
        object_to_check.extend([value for value in obj.values()])
        if "_class" in obj:
            obj["id"] = datamodel.generate_id()

    if isinstance(obj, list):
        object_to_check.extend(obj)


file = open("data_json.json", "w")

json.dump(data_json, file, indent=4)

file.close()