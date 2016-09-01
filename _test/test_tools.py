import json

def print_b(di):
    if isinstance(di, dict) or isinstance(di, list):
        print(json.dumps(di, indent=4))
    else:
        print(di)
