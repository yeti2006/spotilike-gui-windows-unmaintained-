import json


def get_id(dadict, name):
    for key, value in dadict.items():
        if dadict[key]['name'] == name:
            return key

with open("config/data.json") as f:
    data = json.load(f)
    
print(get_id(data, "Dc"))