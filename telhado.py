import tinytuya
import sys

DEVICE_ID = 'eb73c49f845500b95bvc9n'
IP_LOCAL  = '10.1.3.19'
LOCAL_KEY = 'QaWZ_t$!=d1GRJO]'
VERSION   = 3.4

def conectar():
    d = tinytuya.Device(
        dev_id=DEVICE_ID,
        address=IP_LOCAL,
        local_key=LOCAL_KEY,
        version=VERSION
    )
    d.set_socketTimeout(5)
    return d

def status():
    d = conectar()
    s = d.status()
    if 'dps' in s:
        aberta = s['dps'].get('3', False)
        print(f"Cobertura: {'ABERTA' if aberta else 'FECHADA'}")
        return aberta
    else:
        print("Erro ao ler status:", s)
        return None

def abrir():
    aberta = status()
    if aberta is None:
        print("Não foi possível verificar o status. Abortando.")
        return
    if aberta:
        print("Cobertura já está aberta. Nenhuma ação necessária.")
        return
    print("Abrindo cobertura...")
    d = conectar()
    d.set_value(1, True)
    print("Comando enviado.")

def fechar():
    aberta = status()
    if aberta is None:
        print("Não foi possível verificar o status. Abortando.")
        return
    if not aberta:
        print("Cobertura já está fechada. Nenhuma ação necessária.")
        return
    print("Fechando cobertura...")
    d = conectar()
    d.set_value(1, False)
    print("Comando enviado.")

if __name__ == '__main__':
    # Se passou argumento direto (usado pelo agendador)
    if len(sys.argv) > 1:
        comando = sys.argv[1].lower()
        if comando == 'abrir':
            abrir()
        elif comando == 'fechar':
            fechar()
        elif comando == 'status':
            status()
        else:
            print("Argumento inválido. Use: abrir, fechar ou status")
    else:
        # Menu interativo normal
        print("=== Controle Cobertura Pier 1 ===")
        print("1 - Ver status")
        print("2 - Abrir")
        print("3 - Fechar")
        opcao = input("Escolha: ")

        if opcao == '1':
            status()
        elif opcao == '2':
            abrir()
        elif opcao == '3':
            fechar()
        else:
            print("Opção inválida.")