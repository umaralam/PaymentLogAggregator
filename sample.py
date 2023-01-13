import json
from pathlib import Path
import socket


hostname = socket.gethostname()
data = Path("common.json").read_text()
config = json.loads(data)

if config:
    try:
        for i in config[hostname]:
            if i == 'GRIFF':
                print(f'i={i}')
            elif i == 'PACKS':
                print(f'i={i}')
            else:
                print('GRIFF/PACKS key not present in common.json file')
                break
    except KeyError as ex:
        print('invalid hostname key')