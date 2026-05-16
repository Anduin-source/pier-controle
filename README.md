# Pier 1 — Controle de Cobertura e Régua

Sistema de controle para o Observatório Munhoz (MPC X93), Pier 1.
Controla a cobertura motorizada (MCP 1001) e a régua inteligente via protocolo Tuya.

## Funcionalidades

- Abrir e fechar a cobertura do pier
- Controle individual das 4 tomadas da régua
- Agendamento de abertura e fechamento com horário configurável pela interface
- Agendamento salvo nos servidores Tuya (funciona sem o PC ligado)
- Status automático ao iniciar
- Painel web para o administrador gerenciar todas as coberturas (Flask)
- Driver ASCOM Alpaca para integração nativa com o NINA

## Modos de conexão

O sistema tenta conexão **local** primeiro (via rede LAN do observatório).
Se o dispositivo não estiver acessível localmente (ex: acesso remoto via ZeroTier),
faz fallback automático para **conexão via nuvem Tuya**. O ícone 📡 indica modo cloud.

Implicações do modo cloud: requer internet ativa, latência maior (~2-3s), depende dos servidores Tuya.

## Dependências

```
pip install tinytuya flask schedule
```

## Configuração inicial

### 1. Obter as credenciais dos dispositivos

Rode o wizard do tinytuya para descobrir os IDs, IPs e chaves locais dos seus dispositivos:

```
python -m tinytuya wizard
```

Siga as instruções. Você precisará do **Access ID** e **Secret** da sua conta em [iot.tuya.com](https://iot.tuya.com).
O wizard gera um `devices.json` com todos os dispositivos vinculados à sua conta.

### 2. Criar o config.json

Copie o arquivo de exemplo e preencha com seus dados:

```
cp config_exemplo.json config.json
```

Edite o `config.json` com as informações dos seus dispositivos:

```json
{
  "cobertura": {
    "id":  "ID do dispositivo (campo 'id' no devices.json)",
    "ip":  "IP local do dispositivo (campo 'ip' no devices.json)",
    "key": "Chave local (campo 'key' no devices.json)"
  },
  "regua": {
    "id":  "ID do dispositivo",
    "ip":  "IP local do dispositivo",
    "key": "Chave local",
    "switches": {
      "1": "Nome da tomada 1",
      "2": "Nome da tomada 2",
      "3": "Nome da tomada 3",
      "4": "Nome da tomada 4"
    }
  },
  "tuya_cloud": {
    "region":     "us",
    "api_key":    "Access ID da conta Tuya Developer",
    "api_secret": "Secret da conta Tuya Developer",
    "timezone":   "America/Sao_Paulo"
  },
  "agendamento": {
    "abrir":  "",
    "fechar": "05:00"
  }
}
```

> **Atenção:** o `config.json` contém suas credenciais e **não deve ser versionado**.
> Ele já está listado no `.gitignore`.

## Como usar

Interface gráfica:

```
TELHADO_PIER1.bat
```

Painel web (administrador):

```
python servidor.py
```

Acesse em qualquer PC da rede: `http://<IP-do-servidor>:5000`

Driver ASCOM Alpaca (integração NINA):

```
python dome_driver.py
```

No NINA: Equipment → Dome → seleciona `Pier 1 Tuya Dome @ 127.0.0.1 #0`

## Arquivos

| Arquivo | Descrição |
|---|---|
| `telhado_gui.py` | Interface gráfica Tkinter |
| `dome_driver.py` | Driver ASCOM Alpaca para NINA |
| `servidor.py` | Painel web Flask |
| `tuya_cloud.py` | Módulo API Tuya Cloud |
| `telhado.py` | Controle via linha de comando |
| `TELHADO_PIER1.bat` | Atalho para a interface gráfica |
| `config_exemplo.json` | Template de configuração (copiar para config.json) |

## Observações

- `config.json` e `devices.json` não são versionados (dados sensíveis)
- Compatível com dispositivos Tuya protocolo 3.4
- O driver ASCOM precisa estar rodando para o NINA controlar o dome
- Fora da rede local o sistema usa automaticamente a API Tuya Cloud

## Autor

Desenvolvido por **André Brossel** — Observatório Munhoz (MPC X93)

## Licença

MIT License — sinta-se livre para usar, modificar e distribuir,
mantendo os créditos ao autor original.