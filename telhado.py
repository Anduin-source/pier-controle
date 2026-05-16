import tinytuya
import sys
import json
import os

CONFIG_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'config.json')
with open(CONFIG_FILE, 'r') as f:
    _cfg = json.load(f)

DEVICE_ID = _cfg['cobertura']['id']
IP_LOCAL  = _cfg['cobertura']['ip']
LOCAL_KEY = _cfg['cobertura']['key']
VERSION   = 3.4
