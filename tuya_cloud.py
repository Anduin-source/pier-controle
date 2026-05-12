import tinytuya

API_REGION = 'us'
API_KEY    = 'cdmapnmpr99qu9k4fxsp'
API_SECRET = '65fc894d3db1434a95877c9019db040d'
COB_ID     = 'eb73c49f845500b95bvc9n'
TIMEZONE   = 'America/Sao_Paulo'

def conectar_cloud():
    return tinytuya.Cloud(
        apiRegion=API_REGION,
        apiKey=API_KEY,
        apiSecret=API_SECRET
    )

def listar_timers():
    c = conectar_cloud()
    return c.cloudrequest(f'/v2.0/cloud/timer/device/{COB_ID}')

def deletar_todos_timers():
    c = conectar_cloud()
    return c.cloudrequest(
        f'/v2.0/cloud/timer/device/{COB_ID}/batch',
        action='DELETE'
    )

def criar_timer(hora_str, acao):
    """
    hora_str: 'HH:MM'
    acao: 'abrir' ou 'fechar'
    """
    valor = True if acao == 'abrir' else False
    c = conectar_cloud()
    body = {
        'time': hora_str,
        'loops': '1111111',
        'timezone_id': TIMEZONE,
        'functions': [
            {'code': 'switch_1', 'value': valor}
        ],
        'alias_name': f'pier1_{acao}'
    }
    return c.cloudrequest(
        f'/v2.0/cloud/timer/device/{COB_ID}',
        action='POST',
        post=body
    )

if __name__ == '__main__':
    print("Testando API Cloud Tuya...")
    print("\n--- Timers existentes ---")
    print(listar_timers())