import streamlit as st
import pandas as pd
import numpy as np
import yfinance as yf
import matplotlib.pyplot as plt
import requests
from datetime import datetime
import pytz
import warnings
import re

from modules.fundamentals import mapear_ticker_us, NOMES_BDRS


def eh_etf(ticker_bdr):
    """
    Identifica se um ticker BDR corresponde a um ETF.
    Regra: BDRs de ETF na B3 terminam em '39'.
    """
    return str(ticker_bdr).strip().upper().endswith('39')


# ──────────────────────────────────────────────────────────────────────────
# MAPA DE CORREÇÃO — BDR de ETF -> ticker REAL do fundo no Yahoo Finance
# ──────────────────────────────────────────────────────────────────────────
# O BDR_TO_US_MAP em fundamentals.py foi gerado de forma heurística e, para
# vários ETFs (terminação 39), o ticker resultante não corresponde ao
# símbolo real do fundo no Yahoo (ex.: BUSM39 -> 'BUSM', que não existe;
# o fundo correto é o iShares MSCI USA Min Vol Factor ETF = 'USMV').
#
# Este mapa cobre os casos conhecidos de divergência. Quando o ticker BDR
# não estiver aqui, o código tenta o mapeamento padrão e, em seguida,
# busca pelo NOME do fundo via yf.Search como fallback.
ETF_TICKER_CORRECAO = {
    'AADA39': 'EZA',     # 21Shares / South Africa ETP (aprox.)
    'ABGD39': 'AGGY',    # abrdn Gold ETF Trust (aprox. — pode variar)
    'ACWX39': 'ACWX',
    'ARGT39': 'ARGT',
    'BACW39': 'ACWI',
    'BAER39': 'ITA',
    'BAGG39': 'AGG',
    'BAOR39': 'AOR',
    'BARY39': 'IRBO',
    'BASK39': 'BASK',
    'BBJP39': 'BBJP',
    'BBUG39': 'BUG',
    'BCAT39': 'SPCX',
    'BCHI39': 'MCHI',
    'BCIR39': 'CIBR',
    'BCLO39': 'CLOU',
    'BCNY39': 'CNYA',
    'BCOM39': 'COMB',
    'BCPX39': 'COPX',
    'BCTE39': 'CTEC',
    'BCWV39': 'ACWV',
    'BDVD39': 'SDIV',
    'BDVE39': 'DVYE',
    'BDVY39': 'DVY',
    'BECH39': 'ECH',
    'BEEM39': 'EEM',
    'BEFA39': 'EFA',
    'BEFG39': 'EFG',
    'BEFV39': 'EFV',
    'BEGD39': 'ESGD',
    'BEGE39': 'ESGE',
    'BEGU39': 'ESGU',
    'BEIS39': 'EIS',
    'BEMV39': 'EEMV',
    'BEPP39': 'IPAC',
    'BEPU39': 'EPU',
    'BEWA39': 'EWA',
    'BEWC39': 'EWC',
    'BEWD39': 'EWD',
    'BEWG39': 'EWG',
    'BEWH39': 'EWH',
    'BEWJ39': 'EWJ',
    'BEWL39': 'EWL',
    'BEWP39': 'EWP',
    'BEWS39': 'EWS',
    'BEWW39': 'EWW',
    'BEWY39': 'EWY',
    'BEWZ39': 'EWZ',
    'BEZA39': 'EZA',
    'BEZU39': 'EZU',
    'BFAV39': 'EFAV',
    'BFLO39': 'FLOT',
    'BFXI39': 'FXI',
    'BGLC39': 'IOO',
    'BGOV39': 'GOVT',
    'BGOZ39': 'GOVZ',
    'BGRT39': 'REET',
    'BGWH39': 'DGRO',
    'BHEF39': 'HEFA',
    'BHER39': 'HERO',
    'BHYC39': 'SHYG',
    'BHYG39': 'HYG',
    'BIAI39': 'IAI',
    'BIAU39': 'IAU',
    'BIBB39': 'IBB',
    'BICL39': 'ICLN',
    'BICI39': 'IBIT',
    'BIEF39': 'IEFA',
    'BIEI39': 'IEI',
    'BIEM39': 'IEMG',
    'BIEO39': 'IEO',
    'BIEU39': 'IEUR',
    'BIEV39': 'IEV',
    'BIGF39': 'IGF',
    'BIGS39': 'IGSB',
    'BIHE39': 'IHE',
    'BIHF39': 'IHF',
    'BIHI39': 'IHI',
    'BIJH39': 'IJH',
    'BIJR39': 'IJR',
    'BIJS39': 'IJS',
    'BIJT39': 'IJT',
    'BILF39': 'ILF',
    'BIPC39': 'IPAC',
    'BITB39': 'ITB',
    'BITO39': 'ITOT',
    'BIUS39': 'IUSB',
    'BIVB39': 'IVV',
    'BIVE39': 'IVE',
    'BIVW39': 'IVW',
    'BIWF39': 'IWF',
    'BIWM39': 'IWM',
    'BIXG39': 'IXG',
    'BIXJ39': 'IXJ',
    'BIXN39': 'IXN',
    'BIXU39': 'IXUS',
    'BIYE39': 'IYE',
    'BIYF39': 'IYF',
    'BIYJ39': 'IYJ',
    'BIYT39': 'IEF',
    'BIYW39': 'IYW',
    'BIYZ39': 'IYZ',
    'BJQU39': 'JQUA',
    'BKCH39': 'BLOK',
    'BKWB39': 'KWEB',
    'BKXI39': 'KXI',
    'BLBT39': 'LIT',
    'BLPX39': 'MLPA',
    'BLQD39': 'LQD',
    'BMTU39': 'MTUM',
    'BNDA39': 'INDA',
    'BOEF39': 'OEF',
    'BOTZ39': 'BOTZ',
    'BPIC39': 'PICK',
    'BPVE39': 'PAVE',
    'BQQW39': 'QQEW',
    'BQUA39': 'QUAL',
    'BQYL39': 'QYLD',
    'BSCZ39': 'SCZ',
    'BSDV39': 'DIV',
    'BSHV39': 'SHV',
    'BSHY39': 'SHY',
    'BSIL39': 'SIL',
    'BSIZ39': 'SIZE',
    'BSLV39': 'SLV',
    'BSOC39': 'SOCL',
    'BSOX39': 'SOXX',
    'BSRE39': 'SRET',
    'BTFL39': 'TFLO',
    'BTIP39': 'TIP',
    'BTLT39': 'TLT',
    'BURA39': 'URA',
    'BURT39': 'URTH',
    'BUSM39': 'USMV',
    'BUSR39': 'USRT',
    'BUTL39': 'IDU',
    'CRYP39': 'BLOK',
    'DOLL39': 'BIL',
    'DTCR39': 'IDGT',
    'EIDO39': 'EIDO',
    'EPHE39': 'EPHE',
    'ETHA39': 'ETHA',
    'EWJV39': 'EWJV',
    'GDXB39': 'GDX',
    'HYEM39': 'HYEM',
    'RSSL39': 'IWM',
    'SIVR39': 'SIVR',
    'SLXB39': 'SLX',
    'SMIN39': 'SMIN',
    'SOLN39': 'SGOL',
    'TBIL39': 'BIL',
    'TOPB39': 'OEF',
    'AETH39': 'ETHA',
    'ANGV39': 'ANGL',
    'AXRP39': 'XRP',
}


@st.cache_data(ttl=3600, show_spinner=False)
def buscar_dados_etf(ticker_bdr):
    """
    Busca dados detalhados do ETF correspondente via yfinance.

    Estratégia de fallback em cascata:
      1. Ticker corrigido manualmente (ETF_TICKER_CORRECAO), quando existe.
      2. Ticker US mapeado (BDR_TO_US_MAP) via mapear_ticker_us.
      3. Ticker BDR sem o sufixo numérico (fallback genérico).
      4. Busca pelo NOME do fundo (NOMES_BDRS) via yf.Search — útil quando
         nenhum dos tickers acima é válido no Yahoo.

    Retorna dict com:
        erro
        ticker_fonte
        nome
        categoria
        familia_fundo
        patrimonio (totalAssets)
        expense_ratio
        ytd_return
        yield_div
        nav
        preco
        variacao_dia
        volume
        beta
        max_52s, min_52s
        top_holdings: list[{'symbol','name','pct'}]
        setores: list[{'setor','pct'}]
        descricao
    """
    ticker_bdr = str(ticker_bdr).strip().upper()
    ticker_us  = mapear_ticker_us(ticker_bdr)

    candidatos = []

    # 1. Correção manual conhecida
    if ticker_bdr in ETF_TICKER_CORRECAO:
        candidatos.append(ETF_TICKER_CORRECAO[ticker_bdr])

    # 2. Mapeamento padrão (BDR_TO_US_MAP)
    if ticker_us and ticker_us != ticker_bdr:
        candidatos.append(ticker_us)

    # 3. Fallback genérico — remove sufixo numérico
    stripped = ticker_bdr.rstrip('0123456789')
    if stripped:
        candidatos.append(stripped)

    # remove duplicados preservando ordem
    vistos = set()
    candidatos = [c for c in candidatos if c and not (c in vistos or vistos.add(c))]

    def _tentar_ticker(tk):
        """Tenta buscar dados de fundo para um ticker específico."""
        try:
            t = yf.Ticker(tk)
            info = t.info or {}
            if not info or len(info) < 3:
                return None

            quote_type = (info.get('quoteType') or '').upper()
            tem_campos_fundo = any([
                info.get('totalAssets'),
                info.get('fundFamily'),
                info.get('category'),
                info.get('navPrice'),
            ])
            if quote_type != 'ETF' and not tem_campos_fundo:
                return None

            return _montar_resultado(t, info, tk)
        except Exception:
            return None

    # ── Tentativas 1-3: tickers candidatos diretos ──────────────────────────
    for tk in candidatos:
        resultado = _tentar_ticker(tk)
        if resultado:
            return resultado

    # ── Tentativa 4: busca pelo nome do fundo via yf.Search ─────────────────
    try:
        nome_fundo = NOMES_BDRS.get(ticker_bdr, '')
        if nome_fundo:
            # Remove sufixos genéricos que poluem a busca
            nome_busca = re.sub(
                r'\b(ETF|ETP|Trust|Fund|Shares?|Sponsored|ADR|ADS)\b',
                '', nome_fundo, flags=re.IGNORECASE
            ).strip()
            if nome_busca:
                resultado_busca = yf.Search(nome_busca, max_results=8)
                quotes = resultado_busca.quotes if hasattr(resultado_busca, 'quotes') else []
                for q in quotes:
                    tipo = (q.get('quoteType') or '').upper()
                    symbol = q.get('symbol', '')
                    if tipo == 'ETF' and symbol and '.' not in symbol:
                        resultado = _tentar_ticker(symbol)
                        if resultado:
                            return resultado
    except Exception:
        pass

    return {'erro': f'Não foi possível obter dados de ETF para {ticker_bdr} (US: {ticker_us}).'}


def _montar_resultado(t, info, ticker_fonte):
    """Monta o dicionário padronizado de resposta a partir de um yf.Ticker já validado."""

    # ── Top holdings ──────────────────────────────────────────────────────────
    top_holdings = []
    try:
        hold_df = t.funds_data.top_holdings if hasattr(t, 'funds_data') else None
        if hold_df is not None and not hold_df.empty:
            for idx, row in hold_df.head(10).iterrows():
                top_holdings.append({
                    'symbol': str(idx),
                    'name': str(row.get('Name', idx)),
                    'pct': float(row.get('Holding Percent', 0)) * 100,
                })
    except Exception:
        pass

    # ── Setores ───────────────────────────────────────────────────────────────
    setores = []
    try:
        sec_weights = t.funds_data.sector_weightings if hasattr(t, 'funds_data') else None
        if sec_weights:
            nomes_pt = {
                'realestate': 'Imóveis', 'consumer_cyclical': 'Consumo Cíclico',
                'basic_materials': 'Materiais Básicos', 'consumer_defensive': 'Consumo Defensivo',
                'technology': 'Tecnologia', 'communication_services': 'Comunicação',
                'financial_services': 'Serviços Financeiros', 'utilities': 'Utilidades',
                'industrials': 'Industrial', 'energy': 'Energia', 'healthcare': 'Saúde',
            }
            for setor, peso in sec_weights.items():
                if peso and peso > 0:
                    setores.append({
                        'setor': nomes_pt.get(setor, setor.replace('_', ' ').title()),
                        'pct': float(peso) * 100,
                    })
            setores.sort(key=lambda x: x['pct'], reverse=True)
    except Exception:
        pass

    # ── Preço / variação ──────────────────────────────────────────────────────
    preco = info.get('regularMarketPrice') or info.get('previousClose')
    preco_ant = info.get('regularMarketPreviousClose') or info.get('previousClose')
    variacao_dia = None
    if preco and preco_ant and preco_ant != 0:
        variacao_dia = (preco - preco_ant) / preco_ant * 100

    # ── Expense ratio ─────────────────────────────────────────────────────────
    expense_ratio = info.get('netExpenseRatio') or info.get('annualReportExpenseRatio')
    if expense_ratio and expense_ratio < 1:
        expense_ratio = expense_ratio * 100

    # ── YTD return ────────────────────────────────────────────────────────────
    ytd = info.get('ytdReturn')
    if ytd is not None:
        ytd = ytd * 100

    return {
        'erro': None,
        'ticker_fonte': ticker_fonte,
        'nome': info.get('longName') or info.get('shortName') or ticker_fonte,
        'categoria': info.get('category', 'N/A'),
        'familia_fundo': info.get('fundFamily', 'N/A'),
        'patrimonio': info.get('totalAssets'),
        'expense_ratio': expense_ratio,
        'ytd_return': ytd,
        'yield_div': (info.get('yield') * 100) if info.get('yield') else None,
        'nav': info.get('navPrice'),
        'preco': preco,
        'variacao_dia': variacao_dia,
        'volume': info.get('regularMarketVolume') or info.get('volume'),
        'beta': info.get('beta3Year') or info.get('beta'),
        'max_52s': info.get('fiftyTwoWeekHigh'),
        'min_52s': info.get('fiftyTwoWeekLow'),
        'top_holdings': top_holdings,
        'setores': setores,
        'descricao': info.get('longBusinessSummary', ''),
    }


def renderizar_painel_etf(dados, ticker_bdr, empresa):
    """Renderiza o painel detalhado da ETF dentro de um st.expander."""
    with st.expander("🧺 Detalhes da ETF — Composição, Setores & Métricas de Fundo", expanded=True):

        if dados.get('erro'):
            st.warning(f"⚠️ {dados['erro']}")
            st.caption("Algumas ETFs não disponibilizam dados completos via Yahoo Finance.")
            return

        nome          = dados.get('nome', ticker_bdr)
        ticker_fonte  = dados.get('ticker_fonte', ticker_bdr)
        categoria     = dados.get('categoria') or 'N/A'
        familia       = dados.get('familia_fundo') or 'N/A'
        patrimonio    = dados.get('patrimonio')
        expense_ratio = dados.get('expense_ratio')
        ytd           = dados.get('ytd_return')
        yield_div     = dados.get('yield_div')
        nav           = dados.get('nav')
        preco         = dados.get('preco')
        variacao_dia  = dados.get('variacao_dia')
        volume        = dados.get('volume')
        beta          = dados.get('beta')
        max_52s       = dados.get('max_52s')
        min_52s       = dados.get('min_52s')
        top_holdings  = dados.get('top_holdings') or []
        setores       = dados.get('setores') or []
        descricao     = dados.get('descricao', '')

        # ── Cabeçalho ─────────────────────────────────────────────────────────
        st.markdown(f"""
        <div style='background:linear-gradient(135deg,#0f172a 0%,#1e3a5f 100%);
                    padding:1rem 1.4rem;border-radius:12px;margin-bottom:1rem;'>
            <div style='display:flex;align-items:center;gap:0.8rem;margin-bottom:0.4rem;'>
                <span style='font-size:1.8rem;'>🧺</span>
                <div>
                    <div style='color:#93c5fd;font-weight:800;font-size:1rem;'>
                        {nome}</div>
                    <div style='color:#bfdbfe;font-size:0.78rem;'>
                        {ticker_bdr} (B3) · {ticker_fonte} (Fundo) · {familia}</div>
                </div>
            </div>
            <p style='margin:0;color:#bfdbfe;font-size:0.78rem;'>
                📂 <strong style='color:#93c5fd;'>Categoria:</strong> {categoria}
            </p>
        </div>""", unsafe_allow_html=True)

        # ── Cards principais ─────────────────────────────────────────────────
        c1, c2, c3, c4 = st.columns(4)

        with c1:
            if preco:
                sinal = '+' if (variacao_dia or 0) >= 0 else ''
                cor_v = '#15803d' if (variacao_dia or 0) >= 0 else '#b91c1c'
                var_str = f"{sinal}{variacao_dia:.2f}%" if variacao_dia is not None else 'N/A'
                st.markdown(f"""
                <div style='background:#f8fafc;border:1px solid #e2e8f0;border-radius:10px;
                            padding:0.85rem;text-align:center;min-height:105px;
                            display:flex;flex-direction:column;justify-content:center;'>
                    <div style='font-size:0.65rem;font-weight:700;color:#94a3b8;
                                text-transform:uppercase;'>Preço (Fundo)</div>
                    <div style='font-size:1.3rem;font-weight:900;color:#1e293b;'>
                        ${preco:.2f}</div>
                    <div style='font-size:0.85rem;font-weight:700;color:{cor_v};'>{var_str}</div>
                </div>""", unsafe_allow_html=True)
            else:
                st.markdown("<div style='text-align:center;color:#94a3b8;'>Preço N/A</div>",
                            unsafe_allow_html=True)

        with c2:
            patrimonio_str = 'N/A'
            if patrimonio:
                if patrimonio >= 1e9:
                    patrimonio_str = f"${patrimonio/1e9:.2f}B"
                else:
                    patrimonio_str = f"${patrimonio/1e6:.1f}M"
            st.markdown(f"""
            <div style='background:#f8fafc;border:1px solid #e2e8f0;border-radius:10px;
                        padding:0.85rem;text-align:center;min-height:105px;
                        display:flex;flex-direction:column;justify-content:center;'>
                <div style='font-size:0.65rem;font-weight:700;color:#94a3b8;
                            text-transform:uppercase;'>Patrimônio (AUM)</div>
                <div style='font-size:1.3rem;font-weight:900;color:#1e293b;'>
                    {patrimonio_str}</div>
                <div style='font-size:0.7rem;color:#94a3b8;'>Total Assets</div>
            </div>""", unsafe_allow_html=True)

        with c3:
            er_str = f"{expense_ratio:.2f}%" if expense_ratio is not None else 'N/A'
            cor_er = '#15803d' if (expense_ratio or 0) < 0.3 else '#b45309' if (expense_ratio or 0) < 0.7 else '#b91c1c'
            st.markdown(f"""
            <div style='background:#f8fafc;border:1px solid #e2e8f0;border-radius:10px;
                        padding:0.85rem;text-align:center;min-height:105px;
                        display:flex;flex-direction:column;justify-content:center;'>
                <div style='font-size:0.65rem;font-weight:700;color:#94a3b8;
                            text-transform:uppercase;'>Taxa de Administração</div>
                <div style='font-size:1.3rem;font-weight:900;color:{cor_er};'>
                    {er_str}</div>
                <div style='font-size:0.7rem;color:#94a3b8;'>Expense Ratio (a.a.)</div>
            </div>""", unsafe_allow_html=True)

        with c4:
            yield_str = f"{yield_div:.2f}%" if yield_div is not None else 'N/A'
            ytd_str   = f"{ytd:+.2f}%" if ytd is not None else 'N/A'
            cor_ytd = '#15803d' if (ytd or 0) >= 0 else '#b91c1c'
            st.markdown(f"""
            <div style='background:#f8fafc;border:1px solid #e2e8f0;border-radius:10px;
                        padding:0.85rem;text-align:center;min-height:105px;
                        display:flex;flex-direction:column;justify-content:center;'>
                <div style='font-size:0.65rem;font-weight:700;color:#94a3b8;
                            text-transform:uppercase;'>Yield / YTD</div>
                <div style='font-size:1.1rem;font-weight:900;color:#1e293b;'>
                    Yield: {yield_str}</div>
                <div style='font-size:0.95rem;font-weight:800;color:{cor_ytd};'>
                    YTD: {ytd_str}</div>
            </div>""", unsafe_allow_html=True)

        st.markdown("<div style='height:0.8rem'></div>", unsafe_allow_html=True)

        # ── Linha 2: NAV, Volume, Beta, 52 semanas ─────────────────────────────
        c5, c6, c7, c8 = st.columns(4)
        with c5:
            nav_str = f"${nav:.2f}" if nav else 'N/A'
            st.markdown(f"""
            <div style='background:#fff;border:1px solid #e2e8f0;border-radius:8px;
                        padding:0.6rem;text-align:center;'>
                <div style='font-size:0.6rem;color:#94a3b8;font-weight:700;
                            text-transform:uppercase;'>NAV</div>
                <div style='font-size:0.95rem;font-weight:800;color:#1e293b;'>{nav_str}</div>
            </div>""", unsafe_allow_html=True)

        with c6:
            vol_str = f"{volume:,.0f}" if volume else 'N/A'
            st.markdown(f"""
            <div style='background:#fff;border:1px solid #e2e8f0;border-radius:8px;
                        padding:0.6rem;text-align:center;'>
                <div style='font-size:0.6rem;color:#94a3b8;font-weight:700;
                            text-transform:uppercase;'>Volume</div>
                <div style='font-size:0.95rem;font-weight:800;color:#1e293b;'>{vol_str}</div>
            </div>""", unsafe_allow_html=True)

        with c7:
            beta_str = f"{beta:.2f}" if beta else 'N/A'
            st.markdown(f"""
            <div style='background:#fff;border:1px solid #e2e8f0;border-radius:8px;
                        padding:0.6rem;text-align:center;'>
                <div style='font-size:0.6rem;color:#94a3b8;font-weight:700;
                            text-transform:uppercase;'>Beta (3Y)</div>
                <div style='font-size:0.95rem;font-weight:800;color:#1e293b;'>{beta_str}</div>
            </div>""", unsafe_allow_html=True)

        with c8:
            faixa_str = 'N/A'
            if max_52s and min_52s:
                faixa_str = f"${min_52s:.2f} – ${max_52s:.2f}"
            st.markdown(f"""
            <div style='background:#fff;border:1px solid #e2e8f0;border-radius:8px;
                        padding:0.6rem;text-align:center;'>
                <div style='font-size:0.6rem;color:#94a3b8;font-weight:700;
                            text-transform:uppercase;'>Faixa 52 Semanas</div>
                <div style='font-size:0.85rem;font-weight:800;color:#1e293b;'>{faixa_str}</div>
            </div>""", unsafe_allow_html=True)

        st.markdown("<div style='height:1rem'></div>", unsafe_allow_html=True)

        # ── Top Holdings + Setores ────────────────────────────────────────────
        col_h, col_s = st.columns(2)

        with col_h:
            st.markdown("**📋 Principais Posições (Top Holdings):**")
            if top_holdings:
                df_hold = pd.DataFrame(top_holdings)
                df_hold = df_hold.rename(columns={'symbol': 'Ticker', 'name': 'Nome', 'pct': '% Carteira'})
                st.dataframe(
                    df_hold.style.format({'% Carteira': '{:.2f}%'}),
                    width="stretch", hide_index=True,
                    column_config={
                        "Ticker": st.column_config.TextColumn("Ticker", width="small"),
                        "Nome": st.column_config.TextColumn("Nome", width="medium"),
                        "% Carteira": st.column_config.ProgressColumn(
                            "% Carteira", format="%.2f%%", min_value=0,
                            max_value=max(h['pct'] for h in top_holdings) if top_holdings else 100),
                    }
                )
            else:
                st.info("Composição de holdings não disponível para este fundo.")

        with col_s:
            st.markdown("**🏭 Distribuição por Setor:**")
            if setores:
                fig, ax = plt.subplots(figsize=(5, 3.5))
                setores_top = setores[:8]
                labels = [s['setor'] for s in setores_top]
                vals   = [s['pct'] for s in setores_top]
                cores  = plt.cm.tab20.colors[:len(labels)]
                ax.barh(labels, vals, color=cores)
                ax.invert_yaxis()
                ax.set_xlabel('% da carteira', fontsize=8)
                for i, v in enumerate(vals):
                    ax.text(v + 0.3, i, f'{v:.1f}%', va='center', fontsize=7.5)
                ax.spines['top'].set_visible(False)
                ax.spines['right'].set_visible(False)
                plt.tight_layout()
                st.pyplot(fig)
                plt.close(fig)
            else:
                st.info("Distribuição setorial não disponível para este fundo.")

        # ── Descrição ────────────────────────────────────────────────────────
        if descricao:
            with st.expander("📖 Descrição do Fundo", expanded=False):
                # Limita tamanho para não poluir
                st.write(descricao[:1500] + ('...' if len(descricao) > 1500 else ''))

        st.markdown("""
        <div style='margin-top:0.8rem;padding:0.7rem 1rem;background:#f1f5f9;
                    border-radius:8px;font-size:0.74rem;color:#64748b;line-height:1.6;'>
            ℹ️ <strong>Sobre estes dados:</strong> Informações do fundo subjacente (ETF nos EUA)
            obtidas via Yahoo Finance. O BDR negociado na B3 (terminação 39) replica a cota deste
            fundo, sujeito a variações de câmbio (USD/BRL). Taxa de administração, AUM e composição
            referem-se ao fundo original — não à BDR.
        </div>""", unsafe_allow_html=True)
