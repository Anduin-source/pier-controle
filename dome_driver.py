import threading
import time
import socket
import json
import os
import sys
from flask import Flask, jsonify, request
import tinytuya

# ---------------------------------------------------------------------------
# Configuração — lida de config.json (não versionado)
# ---------------------------------------------------------------------------

CONFIG_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'config.json')

def carregar_config():
    if not os.path.exists(CONFIG_FILE):
        print("ERRO: config.json não encontrado.")
        print("Copie config.exemplo.json para config.json e preencha suas credenciais.")
        sys.exit(1)
    with open(CONFIG_FILE, 'r') as f:
        return json.load(f)

cfg = carregar_config()

COB_ID  = cfg['cobertura']['id']
COB_IP  = cfg['cobertura']['ip']
COB_KEY = cfg['cobertura']['key']
VERSION = 3.4

# ---------------------------------------------------------------------------
# Estado interno
# ---------------------------------------------------------------------------

_connected = False
_shutter   = 'Unknown'
_lock      = threading.Lock()

app = Flask(__name__)

# ---------------------------------------------------------------------------
# Comunicação com o dispositivo
# ---------------------------------------------------------------------------

def conectar():
    d = tinytuya.Device(dev_id=COB_ID, address=COB_IP,
                        local_key=COB_KEY, version=VERSION)
    d.set_socketTimeout(5)
    return d

def ler_status():
    global _shutter, _connected
    try:
        d = conectar()
        s = d.status()
        if 'dps' in s:
            aberta = s['dps'].get('3', False)
            with _lock:
                _shutter   = 'Open' if aberta else 'Closed'
                _connected = True
        else:
            with _lock:
                _shutter   = 'Error'
                _connected = False
    except Exception:
        with _lock:
            _shutter   = 'Error'
            _connected = False

def poll_status():
    while True:
        ler_status()
        time.sleep(30)

# ---------------------------------------------------------------------------
# Alpaca discovery (UDP)
# ---------------------------------------------------------------------------

def alpaca_discovery():
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sock.bind(('', 32227))
    print("Alpaca Discovery rodando na porta 32227")
    while True:
        try:
            data, addr = sock.recvfrom(1024)
            if b'alpacadiscovery' in data.lower():
                response = json.dumps({'AlpacaPort': 11111}).encode()
                sock.sendto(response, addr)
        except Exception:
            pass

# ---------------------------------------------------------------------------
# Management endpoints
# ---------------------------------------------------------------------------

@app.route('/management/apiversions', methods=['GET'])
def api_versions2():
    return jsonify({'Value': [1]})

@app.route('/management/v1/apiversions', methods=['GET'])
def api_versions():
    return jsonify({'Value': [1]})

@app.route('/management/v1/description', methods=['GET'])
def management_description():
    return jsonify({
        'Value': {
            'ServerName':          'Pier 1 Tuya Dome',
            'Manufacturer':        'Observatorio Munhoz',
            'ManufacturerVersion': '1.0',
            'Location':            'Munhoz MG'
        },
        'ErrorNumber':  0,
        'ErrorMessage': ''
    })

@app.route('/management/v1/configureddevices', methods=['GET'])
def configured_devices():
    return jsonify({'Value': [{
        'DeviceName':   'Pier 1 Tuya Dome',
        'DeviceType':   'Dome',
        'DeviceNumber': 0,
        'UniqueID':     'pier1-tuya-dome-001'
    }]})

# ---------------------------------------------------------------------------
# Dome endpoints
# ---------------------------------------------------------------------------

@app.route('/api/v1/dome/0/connected', methods=['GET'])
def get_connected():
    return jsonify({'Value': _connected, 'ErrorNumber': 0, 'ErrorMessage': ''})

@app.route('/api/v1/dome/0/connected', methods=['PUT'])
def put_connected():
    global _connected
    val = request.form.get('Connected', 'false').lower() == 'true'
    if val:
        ler_status()
    else:
        with _lock:
            _connected = False
    return jsonify({'ErrorNumber': 0, 'ErrorMessage': ''})

@app.route('/api/v1/dome/0/shutterstatus', methods=['GET'])
def get_shutter_status():
    status_map = {'Open': 0, 'Closed': 1, 'Opening': 2, 'Closing': 3, 'Error': 4}
    with _lock:
        val = status_map.get(_shutter, 4)
    return jsonify({'Value': val, 'ErrorNumber': 0, 'ErrorMessage': ''})

@app.route('/api/v1/dome/0/openshutter', methods=['PUT'])
def open_shutter():
    global _shutter
    with _lock:
        _shutter = 'Opening'

    def executar():
        global _shutter
        try:
            d     = conectar()
            s     = d.status()
            aberta = s.get('dps', {}).get('3', False) if 'dps' in s else False
            if not aberta:
                d.set_value(1, True)
            time.sleep(15)
            ler_status()
        except Exception:
            with _lock:
                _shutter = 'Error'

    threading.Thread(target=executar).start()
    return jsonify({'ErrorNumber': 0, 'ErrorMessage': ''})

@app.route('/api/v1/dome/0/closeshutter', methods=['PUT'])
def close_shutter():
    global _shutter
    with _lock:
        _shutter = 'Closing'

    def executar():
        global _shutter
        try:
            d     = conectar()
            s     = d.status()
            aberta = s.get('dps', {}).get('3', False) if 'dps' in s else True
            if aberta:
                d.set_value(1, False)
            time.sleep(15)
            ler_status()
        except Exception:
            with _lock:
                _shutter = 'Error'

    threading.Thread(target=executar).start()
    return jsonify({'ErrorNumber': 0, 'ErrorMessage': ''})

@app.route('/api/v1/dome/0/cansetshutter',  methods=['GET'])
def can_set_shutter():  return jsonify({'Value': True,  'ErrorNumber': 0, 'ErrorMessage': ''})

@app.route('/api/v1/dome/0/canpark',        methods=['GET'])
def can_park():         return jsonify({'Value': False, 'ErrorNumber': 0, 'ErrorMessage': ''})

@app.route('/api/v1/dome/0/canslave',       methods=['GET'])
def can_slave():        return jsonify({'Value': False, 'ErrorNumber': 0, 'ErrorMessage': ''})

@app.route('/api/v1/dome/0/cansetazimuth',  methods=['GET'])
def can_set_azimuth():  return jsonify({'Value': False, 'ErrorNumber': 0, 'ErrorMessage': ''})

@app.route('/api/v1/dome/0/cansyncazimuth', methods=['GET'])
def can_sync_azimuth(): return jsonify({'Value': False, 'ErrorNumber': 0, 'ErrorMessage': ''})

@app.route('/api/v1/dome/0/canfindhome',    methods=['GET'])
def can_find_home():    return jsonify({'Value': False, 'ErrorNumber': 0, 'ErrorMessage': ''})

@app.route('/api/v1/dome/0/slaved',         methods=['GET'])
def get_slaved():       return jsonify({'Value': False, 'ErrorNumber': 0, 'ErrorMessage': ''})

@app.route('/api/v1/dome/0/slaved',         methods=['PUT'])
def put_slaved():       return jsonify({'ErrorNumber': 0, 'ErrorMessage': ''})

@app.route('/api/v1/dome/0/atpark',         methods=['GET'])
def at_park():          return jsonify({'Value': False, 'ErrorNumber': 0, 'ErrorMessage': ''})

@app.route('/api/v1/dome/0/athome',         methods=['GET'])
def at_home():          return jsonify({'Value': False, 'ErrorNumber': 0, 'ErrorMessage': ''})

@app.route('/api/v1/dome/0/altitude',       methods=['GET'])
def get_altitude():     return jsonify({'Value': 0.0,  'ErrorNumber': 0, 'ErrorMessage': ''})

@app.route('/api/v1/dome/0/azimuth',        methods=['GET'])
def get_azimuth():      return jsonify({'Value': 0.0,  'ErrorNumber': 0, 'ErrorMessage': ''})

@app.route('/api/v1/dome/0/ismoving',       methods=['GET'])
def is_moving():
    with _lock:
        moving = _shutter in ('Opening', 'Closing')
    return jsonify({'Value': moving, 'ErrorNumber': 0, 'ErrorMessage': ''})

@app.route('/api/v1/dome/0/name',            methods=['GET'])
def get_name():
    return jsonify({'Value': 'Pier 1 Tuya Dome', 'ErrorNumber': 0, 'ErrorMessage': ''})

@app.route('/api/v1/dome/0/description',     methods=['GET'])
def get_description():
    return jsonify({'Value': 'Driver Alpaca para cobertura MCP1001 via tinytuya',
                    'ErrorNumber': 0, 'ErrorMessage': ''})

@app.route('/api/v1/dome/0/driverinfo',      methods=['GET'])
def get_driver_info():
    return jsonify({'Value': 'Pier 1 Tuya Dome Driver v1.0',
                    'ErrorNumber': 0, 'ErrorMessage': ''})

@app.route('/api/v1/dome/0/driverversion',   methods=['GET'])
def get_driver_version():
    return jsonify({'Value': '1.0', 'ErrorNumber': 0, 'ErrorMessage': ''})

@app.route('/api/v1/dome/0/interfaceversion', methods=['GET'])
def get_interface_version():
    return jsonify({'Value': 2, 'ErrorNumber': 0, 'ErrorMessage': ''})

@app.route('/api/v1/dome/0/supportedactions', methods=['GET'])
def supported_actions():
    return jsonify({'Value': [], 'ErrorNumber': 0, 'ErrorMessage': ''})

# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

if __name__ == '__main__':
    print("Pier 1 Tuya Dome Driver — Alpaca")
    print("Rodando em http://localhost:11111")
    print("Conectando ao dispositivo...")
    ler_status()
    print(f"Status inicial: {_shutter}")

    threading.Thread(target=poll_status,       daemon=True).start()
    threading.Thread(target=alpaca_discovery,  daemon=True).start()

    app.run(host='0.0.0.0', port=11111, debug=False)