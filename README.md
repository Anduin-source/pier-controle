# Pier 1 — Controle de Cobertura e Régua

Sistema de controle para o Observatório Munhoz (MPC X93), Pier 1.
Controla a cobertura motorizada (MCP 1001) e a régua inteligente via protocolo Tuya.

## Funcionalidades

- Abrir e fechar a cobertura do Pier 1
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

    pip install tinytuya flask schedule

## Configuração inicial

1. Instale as dependências acima
2. Rode o wizard para gerar o devices.json:

        python -m tinytuya wizard

3. Siga as instruções (necessário Access ID e Secret da conta Tuya Developer)
4. Copie o devices.json gerado para esta pasta

## Como usar

Interface gráfica:

    TELHADO_PIER1.bat

Painel web (administrador):

    servidor.bat

Acesse em qualquer PC da rede: http://10.1.3.10:5000

Driver ASCOM Alpaca (integração NINA):

    python dome_driver.py

No NINA: Equipment → Dome → seleciona Pier 1 Tuya Dome @ 127.0.0.1 #0

## Arquivos

| Arquivo | Descrição |
|---|---|
| telhado_gui.py | Interface gráfica Tkinter |
| dome_driver.py | Driver ASCOM Alpaca para NINA |
| servidor.py | Painel web Flask |
| tuya_cloud.py | Módulo API Tuya Cloud |
| telhado.py | Controle via linha de comando |
| TELHADO_PIER1.bat | Atalho interface gráfica |
| servidor.bat | Atalho painel web |

## Observações

- devices.json e config.json não são versionados (dados sensíveis)
- Compatível com dispositivos Tuya protocolo 3.4
- O driver ASCOM precisa estar rodando para o NINA controlar o dome
- Fora da rede local o sistema usa automaticamente a API Tuya Cloud