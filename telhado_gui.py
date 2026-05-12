import tkinter as tk
import tinytuya
import threading
import schedule
import time
import json
import os

COB_ID  = 'eb73c49f845500b95bvc9n'
COB_IP  = '10.1.3.19'
COB_KEY = 'QaWZ_t$!=d1GRJO]'

REG_ID  = 'ebea13ea79c3067008wnci'
REG_IP  = '10.1.3.12'
REG_KEY = "*w$Fl)a'I7-sfY~8"

SWITCHES = {1: 'Switch 1', 2: 'PC', 3: 'Montagem', 4: 'Switch 4'}

CONFIG_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'config.json')

BG        = '#1a1a2e'
BG_CARD   = '#16213e'
BG_BTN    = '#0f3460'
BG_ENTRY  = '#0a1628'
AZUL      = '#4a9eff'
VERDE     = '#4ade80'
VERMELHO  = '#f87171'
AMARELO   = '#fbbf24'
CINZA     = '#6b7280'
TEXTO     = '#e2e8f0'
TEXTO_MUT = '#94a3b8'
SEPARADOR = '#1e3a5f'

def carregar_config():
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, 'r') as f:
            return json.load(f)
    return {'abrir': '', 'fechar': '05:00'}

def salvar_config(cfg):
    with open(CONFIG_FILE, 'w') as f:
        json.dump(cfg, f)

config = carregar_config()

def conectar_cobertura():
    d = tinytuya.Device(dev_id=COB_ID, address=COB_IP, local_key=COB_KEY, version=3.4)
    d.set_socketTimeout(5)
    return d

def conectar_regua():
    d = tinytuya.Device(dev_id=REG_ID, address=REG_IP, local_key=REG_KEY, version=3.4)
    d.set_socketTimeout(5)
    return d

def acao_cobertura(comando):
    btn_abrir.config(state='disabled')
    btn_fechar.config(state='disabled')
    label_cob.config(text='...', fg=CINZA)

    def executar():
        try:
            d = conectar_cobertura()
            s = d.status()
            aberta = s.get('dps', {}).get('3', False) if 'dps' in s else None
            if aberta is None:
                label_cob.config(text='ERRO', fg=VERMELHO)
            elif comando == 'status':
                label_cob.config(text='ABERTA' if aberta else 'FECHADA',
                                 fg=VERDE if aberta else AZUL)
            elif comando == 'abrir':
                if not aberta:
                    d.set_value(1, True)
                label_cob.config(text='ABERTA', fg=VERDE)
            elif comando == 'fechar':
                if aberta:
                    d.set_value(1, False)
                label_cob.config(text='FECHADA', fg=AZUL)
        except:
            label_cob.config(text='ERRO', fg=VERMELHO)
        btn_abrir.config(state='normal')
        btn_fechar.config(state='normal')

    threading.Thread(target=executar).start()

def abrir_agendado():
    try:
        d = conectar_cobertura()
        s = d.status()
        aberta = s.get('dps', {}).get('3', False) if 'dps' in s else None
        if aberta is False:
            d.set_value(1, True)
        label_cob.config(text='ABERTA', fg=VERDE)
    except:
        pass

def fechar_agendado():
    try:
        d = conectar_cobertura()
        s = d.status()
        aberta = s.get('dps', {}).get('3', False) if 'dps' in s else None
        if aberta is True:
            d.set_value(1, False)
        label_cob.config(text='FECHADA', fg=AZUL)
    except:
        pass

def acao_regua(switch_num, comando):
    if comando in botoes_regua[switch_num]:
        botoes_regua[switch_num][comando].config(state='disabled')
    labels_regua[switch_num].config(text='...', fg=CINZA)

    def executar():
        try:
            d = conectar_regua()
            s = d.status()
            dps = s.get('dps', {}) if 'dps' in s else {}
            ligado = dps.get(str(switch_num), False)
            if comando == 'status':
                labels_regua[switch_num].config(
                    text='ON' if ligado else 'OFF',
                    fg=VERDE if ligado else CINZA)
            elif comando == 'ligar':
                d.set_value(switch_num, True)
                labels_regua[switch_num].config(text='ON', fg=VERDE)
            elif comando == 'desligar':
                d.set_value(switch_num, False)
                labels_regua[switch_num].config(text='OFF', fg=CINZA)
        except:
            labels_regua[switch_num].config(text='ERRO', fg=VERMELHO)
        if comando in botoes_regua[switch_num]:
            botoes_regua[switch_num][comando].config(state='normal')

    threading.Thread(target=executar).start()

def status_todos_regua():
    for sw in SWITCHES:
        acao_regua(sw, 'status')

def validar_hora(hora_str):
    if hora_str.strip() == '':
        return True
    try:
        h, m = hora_str.strip().split(':')
        return 0 <= int(h) <= 23 and 0 <= int(m) <= 59
    except:
        return False

def flash_feedback(label, msg, cor, duracao=2000):
    label.config(text=msg, fg=cor)
    janela.after(duracao, lambda: label.config(text=''))

def iniciar_agendamento_salvo():
    schedule.clear()
    h_abrir  = config.get('abrir', '')
    h_fechar = config.get('fechar', '')
    if h_abrir:
        schedule.every().day.at(h_abrir).do(
            lambda: threading.Thread(target=abrir_agendado).start())
    if h_fechar:
        schedule.every().day.at(h_fechar).do(
            lambda: threading.Thread(target=fechar_agendado).start())

def loop_schedule():
    while True:
        schedule.run_pending()
        time.sleep(10)

def formatar_hora(entry, label_feedback, config_key):
    val = entry.get().replace(':', '').strip()

    if val == '':
        config[config_key] = ''
        salvar_config(config)
        iniciar_agendamento_salvo()
        atualizar_labels_agenda()
        flash_feedback(label_feedback, "removido", AMARELO)
        return

    if len(val) == 3:
        val = '0' + val
    if len(val) != 4 or not val.isdigit():
        flash_feedback(label_feedback, "use 4 dígitos: HHMM", VERMELHO)
        return

    hora = val[:2] + ':' + val[2:]
    if not validar_hora(hora):
        flash_feedback(label_feedback, "hora inválida", VERMELHO)
        return

    entry.delete(0, tk.END)
    entry.insert(0, hora)

    config[config_key] = hora
    salvar_config(config)
    iniciar_agendamento_salvo()
    atualizar_labels_agenda()

    def criar_na_nuvem():
        try:
            from tuya_cloud import criar_timer
            acao = 'abrir' if config_key == 'abrir' else 'fechar'
            r = criar_timer(hora, acao)
            if r.get('success'):
                flash_feedback(label_feedback, "salvo na nuvem ✓", VERDE)
            else:
                flash_feedback(label_feedback, "salvo local (nuvem falhou)", AMARELO)
        except:
            flash_feedback(label_feedback, "salvo local", AMARELO)

    threading.Thread(target=criar_na_nuvem).start()

def atualizar_labels_agenda():
    h_a = config.get('abrir', '')
    h_f = config.get('fechar', '')
    label_horario_abrir.config(
        text=h_a if h_a else 'N/A',
        fg=TEXTO if h_a else CINZA)
    label_horario_fechar.config(
        text=h_f if h_f else 'N/A',
        fg=TEXTO if h_f else CINZA)

def btn_estilo(parent, texto, cor_bg, cor_fg, cmd):
    return tk.Button(parent, text=texto, command=cmd,
                     bg=cor_bg, fg=cor_fg, activebackground=cor_bg,
                     font=('Segoe UI', 10, 'bold'), relief='flat',
                     padx=16, pady=7, cursor='hand2', bd=0)

def separador(parent):
    tk.Frame(parent, bg=SEPARADOR, height=1).pack(fill='x', padx=16, pady=8)


class HorarioEditavel:
    def __init__(self, parent, config_key, label_feedback):
        self.config_key     = config_key
        self.label_feedback = label_feedback
        self.editando       = False

        self.frame = tk.Frame(parent, bg=BG_CARD)

        valor_atual = config.get(config_key, '')
        self.var = tk.StringVar(value=valor_atual)

        cor_inicial = TEXTO if valor_atual else CINZA
        txt_inicial = valor_atual if valor_atual else 'N/A'
        self.label = tk.Label(self.frame, text=txt_inicial,
                              font=('Segoe UI', 16, 'bold'),
                              bg=BG_CARD, fg=cor_inicial, cursor='hand2')
        self.label.pack(anchor='w')
        self.label.bind('<Button-1>', self._entrar_edicao)

        self.entry = tk.Entry(self.frame, textvariable=self.var,
                              font=('Segoe UI', 16, 'bold'), width=6,
                              bg=BG_ENTRY, fg=TEXTO, insertbackground=TEXTO,
                              relief='flat', justify='center',
                              highlightthickness=1,
                              highlightcolor=AZUL,
                              highlightbackground=SEPARADOR)
        self.entry.bind('<Return>', self._salvar)
        self.entry.bind('<Escape>', self._cancelar)
        self.entry.bind('<FocusOut>', self._cancelar)

    def pack(self, **kwargs):
        self.frame.pack(**kwargs)

    def _entrar_edicao(self, event=None):
        if self.editando:
            return
        self.editando = True
        valor = config.get(self.config_key, '')
        self.var.set(valor)
        self.label.pack_forget()
        self.entry.pack(anchor='w')
        self.entry.focus_set()
        self.entry.select_range(0, tk.END)

    def _salvar(self, event=None):
        formatar_hora(self.entry, self.label_feedback, self.config_key)
        valor = config.get(self.config_key, '')
        self._sair_edicao(valor if valor else 'N/A',
                          TEXTO if valor else CINZA)

    def _cancelar(self, event=None):
        if not self.editando:
            return
        valor = config.get(self.config_key, '')
        self._sair_edicao(valor if valor else 'N/A',
                          TEXTO if valor else CINZA)

    def _sair_edicao(self, texto, cor):
        self.editando = False
        self.entry.pack_forget()
        self.label.config(text=texto, fg=cor)
        self.label.pack(anchor='w')


# --- Interface ---
janela = tk.Tk()
janela.title("Pier 1 — Controle")
janela.configure(bg=BG)
janela.geometry("420x640")
janela.resizable(False, False)

# Título
tk.Label(janela, text="🔭  Pier 1", font=('Segoe UI', 15, 'bold'),
         bg=BG, fg=TEXTO).pack(pady=(18, 2))
tk.Label(janela, text="Observatório Munhoz", font=('Segoe UI', 10),
         bg=BG, fg=TEXTO_MUT).pack(pady=(0, 14))

# --- Card Cobertura + Agendamento ---
card_cob = tk.Frame(janela, bg=BG_CARD, bd=0,
                    highlightthickness=1, highlightbackground=BG_BTN)
card_cob.pack(fill='x', padx=20, pady=(0, 12))

tk.Label(card_cob, text="COBERTURA", font=('Segoe UI', 9, 'bold'),
         bg=BG_CARD, fg=TEXTO_MUT).pack(anchor='w', padx=16, pady=(12, 0))

label_cob = tk.Label(card_cob, text="---", font=('Segoe UI', 24, 'bold'),
                     bg=BG_CARD, fg=CINZA)
label_cob.pack(pady=(4, 8))

frame_btn_cob = tk.Frame(card_cob, bg=BG_CARD)
frame_btn_cob.pack(pady=(0, 10))

btn_abrir = btn_estilo(frame_btn_cob, "Abrir", '#166534', VERDE,
                       lambda: acao_cobertura('abrir'))
btn_abrir.grid(row=0, column=0, padx=8)

btn_fechar = btn_estilo(frame_btn_cob, "Fechar", '#1e3a5f', AZUL,
                        lambda: acao_cobertura('fechar'))
btn_fechar.grid(row=0, column=1, padx=8)

separador(card_cob)

tk.Label(card_cob, text="AGENDAMENTO", font=('Segoe UI', 9, 'bold'),
         bg=BG_CARD, fg=TEXTO_MUT).pack(anchor='w', padx=16, pady=(0, 10))

frame_ag = tk.Frame(card_cob, bg=BG_CARD)
frame_ag.pack(padx=16, fill='x')

# Coluna Abrir
col_abrir = tk.Frame(frame_ag, bg=BG_CARD)
col_abrir.pack(side='left', padx=(0, 50))

tk.Label(col_abrir, text="Abrir", font=('Segoe UI', 9),
         bg=BG_CARD, fg=TEXTO_MUT).pack(anchor='w')

label_feedback_abrir = tk.Label(col_abrir, text="", font=('Segoe UI', 8),
                                 bg=BG_CARD, fg=VERDE)

label_horario_abrir = tk.Label(col_abrir, text="", bg=BG_CARD)  # placeholder
label_horario_abrir.pack_forget()

campo_abrir = HorarioEditavel(col_abrir, 'abrir', label_feedback_abrir)
campo_abrir.pack(anchor='w', pady=(2, 2))
label_feedback_abrir.pack(anchor='w')

# Coluna Fechar
col_fechar = tk.Frame(frame_ag, bg=BG_CARD)
col_fechar.pack(side='left')

tk.Label(col_fechar, text="Fechar", font=('Segoe UI', 9),
         bg=BG_CARD, fg=TEXTO_MUT).pack(anchor='w')

label_feedback_fechar = tk.Label(col_fechar, text="", font=('Segoe UI', 8),
                                  bg=BG_CARD, fg=VERDE)

label_horario_fechar = tk.Label(col_fechar, text="", bg=BG_CARD)  # placeholder
label_horario_fechar.pack_forget()

campo_fechar = HorarioEditavel(col_fechar, 'fechar', label_feedback_fechar)
campo_fechar.pack(anchor='w', pady=(2, 2))
label_feedback_fechar.pack(anchor='w')

tk.Label(card_cob, text="Clique no horário para editar  ·  Enter para salvar",
         font=('Segoe UI', 8), bg=BG_CARD, fg=CINZA).pack(
         anchor='w', padx=16, pady=(8, 14))

# --- Card Régua ---
card_reg = tk.Frame(janela, bg=BG_CARD, bd=0,
                    highlightthickness=1, highlightbackground=BG_BTN)
card_reg.pack(fill='x', padx=20, pady=(0, 12))

tk.Label(card_reg, text="RÉGUA", font=('Segoe UI', 9, 'bold'),
         bg=BG_CARD, fg=TEXTO_MUT).pack(anchor='w', padx=16, pady=(12, 8))

labels_regua = {}
botoes_regua = {}

for sw, nome in SWITCHES.items():
    row = tk.Frame(card_reg, bg=BG_CARD)
    row.pack(fill='x', padx=16, pady=3)

    tk.Label(row, text=nome, font=('Segoe UI', 10),
             bg=BG_CARD, fg=TEXTO, width=10, anchor='w').pack(side='left')

    lbl = tk.Label(row, text="---", font=('Segoe UI', 10, 'bold'),
                   bg=BG_CARD, fg=CINZA, width=5)
    lbl.pack(side='left', padx=8)
    labels_regua[sw] = lbl

    btn_off = btn_estilo(row, "OFF", '#3b1a1a', VERMELHO,
                         lambda s=sw: acao_regua(s, 'desligar'))
    btn_off.pack(side='right', padx=(4, 0))

    btn_on = btn_estilo(row, "ON", '#14532d', VERDE,
                        lambda s=sw: acao_regua(s, 'ligar'))
    btn_on.pack(side='right', padx=(4, 0))

    botoes_regua[sw] = {'ligar': btn_on, 'desligar': btn_off}

tk.Frame(card_reg, bg=BG_CARD, height=10).pack()

# Inicia
iniciar_agendamento_salvo()
threading.Thread(target=loop_schedule, daemon=True).start()

janela.after(500, lambda: acao_cobertura('status'))
janela.after(800, status_todos_regua)

janela.mainloop()