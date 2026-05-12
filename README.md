# Pier 1 — Controle de Cobertura e Régua

Sistema de controle local para o Observatório Munhoz (MPC X93), Pier 1.
Controla a cobertura motorizada e a régua inteligente via protocolo Tuya local (sem nuvem).

## Funcionalidades

- Abrir e fechar a cobertura do Pier 1
- Controle individual das 4 tomadas da régua
- Agendamento de abertura e fechamento com horário configurável pela interface
- Status automático ao iniciar
- Painel web acessível pela rede local (Flask)

## Dependências

```bash
pip install tinytuya flask schedule
```

## Configuração inicial

1. Instale as dependências acima
2. Rode o wizard do tinytuya para gerar o `devices.json`:
```bash
python -m tinytuya wizard
```
3. Siga as instruções do wizard (necessário Access ID e Secret da conta Tuya Developer)

## Como usar

**Interface gráfica:**