"""Funções de estilo (CSS inline) para colorir as colunas da tabela via
pandas Styler. Puras — recebem o valor da célula e devolvem uma string CSS."""


# Cor por setor (rótulos em português vindos de technical._SETOR_PT).
_CORES_SETOR = {
    'Tecnologia':         ('#e0e7ff', '#3730a3'),
    'Financeiro':         ('#dcfce7', '#166534'),
    'Saúde':              ('#fee2e2', '#991b1b'),
    'Consumo Cíclico':    ('#ffedd5', '#9a3412'),
    'Consumo Defensivo':  ('#fef9c3', '#854d0e'),
    'Comunicação':        ('#cffafe', '#155e75'),
    'Energia':            ('#fef3c7', '#92400e'),
    'Industrial':         ('#e2e8f0', '#334155'),
    'Utilidades':         ('#ecfccb', '#3f6212'),
    'Materiais Básicos':  ('#f5f5f4', '#57534e'),
    'Imóveis':            ('#fae8ff', '#86198f'),
    'Outros':             ('#f1f5f9', '#475569'),
}


def estilizar_setor(val):
    """Colore a célula de setor com uma cor consistente por setor."""
    bg, fg = _CORES_SETOR.get(str(val).strip(), ('#f1f5f9', '#475569'))
    return f'background-color: {bg}; color: {fg}; font-weight: 600; text-align: center;'


def estilizar_is(val):
    # Robusto a None/NaN/não-numérico (a coluna I.S. pode vir vazia).
    try:
        v = float(val)
    except (TypeError, ValueError):
        return ''
    if v >= 75: return 'background-color: #d32f2f; color: white; font-weight: bold'
    elif v >= 60: return 'background-color: #ffa726; color: black'
    else: return 'color: #888888'


def estilizar_potencial(val):
    if val == 'Muito Alta': return 'background-color: #2e7d32; color: white; font-weight: bold'
    elif val == 'Alta': return 'background-color: #66bb6a; color: black; font-weight: bold'
    elif val == 'Média': return 'background-color: #ffa726; color: black'
    elif val == 'Baixa': return 'background-color: #e0e0e0; color: black'
    return ''


def estilizar_liquidez(val):
    """Degradê vermelho→amarelo→verde para ranking 0-10"""
    paleta = {
        0:  ('#7f0000', 'white'),
        1:  ('#c62828', 'white'),
        2:  ('#ef5350', 'white'),
        3:  ('#ff7043', 'white'),
        4:  ('#ffa726', 'black'),
        5:  ('#fdd835', 'black'),
        6:  ('#d4e157', 'black'),
        7:  ('#9ccc65', 'black'),
        8:  ('#66bb6a', 'black'),
        9:  ('#2e7d32', 'white'),
        10: ('#1b5e20', 'white'),
    }
    try:
        v = int(val)
    except Exception:
        v = 0
    bg, fg = paleta.get(v, ('#9e9e9e', 'white'))
    return (f'background-color: {bg}; color: {fg}; '
            f'font-weight: 900; font-size: 1.1em; text-align: center;')


def estilizar_fundamentalista(val):
    """Estilo para classificação fundamentalista"""
    cores = {
        '🌟': ('#1b5e20', 'white'),  # Excelente
        '✅': ('#2e7d32', 'white'),   # Bom
        '⚖️': ('#fdd835', 'black'),   # Neutro
        '⚠️': ('#ff7043', 'white'),   # Atenção
        '🔴': ('#c62828', 'white'),   # Evitar
        '—': ('#e0e0e0', 'black'),   # N/A
    }
    bg, fg = cores.get(val, ('#e0e0e0', 'black'))
    return (f'background-color: {bg}; color: {fg}; '
            f'font-weight: 900; font-size: 1.2em; text-align: center;')
