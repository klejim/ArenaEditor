import json


def dumps(dict, indent=4):
    return json.dumps(dict, indent=indent)


def load(text):
    json_string = ""
    string = ""
    for line in text.split('\n'):
        string += line
        tmp = line[:]
        if tmp.strip()[:2] != "//":
            json_string += line
    return json.loads(json_string)
