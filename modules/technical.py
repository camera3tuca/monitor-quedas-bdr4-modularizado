import streamlit as st
import pandas as pd
import numpy as np

from modules.yf_session import baixar as _yf_baixar

import matplotlib.pyplot as plt
import seaborn as sns
import requests
from datetime import datetime
import pytz
import warnings
import xml.etree.ElementTree as ET
import html as html_lib
import re
import time
import random

PERIODO = "1y"  # 1 ano para ter dados suficientes para EMA200 (~252 dias úteis)
_LOTE = 40           # tickers por lote — lotes menores reduzem o rate limit do Yahoo
_PAUSA_LOTE = 2.0    # pausa-base (s) entre lotes; jitter aleatório é somado
_MAX_RODADAS = 3     # rodadas extras p/ tickers que faltaram (provável rate limit)
_COOLDOWN_RODADA = 20.0  # cooldown-base (s) entre rodadas; cresce a cada rodada


def _tickers_presentes(parte, lote):
    """Conjunto de tickers (.SA) efetivamente retornados num DataFrame do yfinance."""
    cols = parte.columns
    if isinstance(cols, pd.MultiIndex):
        return {c[1] for c in cols}
    # Download de 1 ticker volta com colunas simples (sem o símbolo): se veio
    # algo, esse único ticker foi obtido.
    return {lote[0]} if len(lote) == 1 else set()


def _baixar_em_lotes(sa_tickers):
    """Baixa uma lista de tickers .SA em lotes sequenciais.

    Retorna (partes, obtidos): a lista de DataFrames baixados e o conjunto de
    tickers .SA que de fato retornaram dados. ``yf.download`` em lote não lança
    exceção em rate limit — ele só devolve um DataFrame parcial — por isso a
    detecção de faltantes é feita comparando o que voltou com o que foi pedido.
    """
    partes, obtidos = [], set()
    for i in range(0, len(sa_tickers), _LOTE):
        lote = sa_tickers[i:i + _LOTE]
        try:
            parte = _yf_baixar(
                lote, period=PERIODO, auto_adjust=True,
                progress=False, timeout=60, threads=False,
            )
            if parte is not None and not parte.empty:
                parte = parte.dropna(axis=1, how='all')
                if not parte.empty:
                    # Normaliza download de 1 ticker para MultiIndex (field, TICKER)
                    # para concatenar de forma consistente com os lotes maiores.
                    if len(lote) == 1 and not isinstance(parte.columns, pd.MultiIndex):
                        parte.columns = pd.MultiIndex.from_product([parte.columns, [lote[0]]])
                    partes.append(parte)
                    obtidos |= _tickers_presentes(parte, lote)
        except Exception:
            pass
        if i + _LOTE < len(sa_tickers):
            time.sleep(_PAUSA_LOTE + random.uniform(0, 1))
    return partes, obtidos


@st.cache_data(ttl=1800)
def buscar_dados(tickers):
    if not tickers: return pd.DataFrame()
    sa_tickers = [f"{t}.SA" for t in tickers]
    try:
        partes = []
        pendentes = list(sa_tickers)
        for rodada in range(_MAX_RODADAS + 1):
            novas, obtidos = _baixar_em_lotes(pendentes)
            partes.extend(novas)
            pendentes = [t for t in pendentes if t not in obtidos]
            if not pendentes or rodada == _MAX_RODADAS:
                break
            # O que faltou é quase sempre rate limit (o Yahoo throttla os lotes
            # finais). Espera o limite "esfriar" antes de tentar só os faltantes,
            # com cooldown crescente a cada rodada.
            time.sleep(_COOLDOWN_RODADA * (rodada + 1) + random.uniform(0, 3))

        if not partes:
            return pd.DataFrame()

        df = pd.concat(partes, axis=1) if len(partes) > 1 else partes[0]
        # Remove colunas duplicadas que podem surgir do concat
        df = df.loc[:, ~df.columns.duplicated()]

        if isinstance(df.columns, pd.MultiIndex):
            df.columns = pd.MultiIndex.from_tuples([(c[0], c[1].replace(".SA", "")) for c in df.columns])

        df = df.dropna(axis=1, how='all')

        # Preencher dados faltantes para BDRs ilíquidas
        idx = pd.IndexSlice
        if isinstance(df.columns, pd.MultiIndex):
            for col in ['Close', 'High', 'Low', 'Open']:
                if col in df.columns.levels[0]:
                    df.loc[:, idx[col, :]] = df.loc[:, idx[col, :]].ffill()
            if 'Volume' in df.columns.levels[0]:
                df.loc[:, idx['Volume', :]] = df.loc[:, idx['Volume', :]].fillna(0)
        else:
            for col in ['Close', 'High', 'Low', 'Open']:
                if col in df.columns:
                    df[col] = df[col].ffill()
            if 'Volume' in df.columns:
                df['Volume'] = df['Volume'].fillna(0)

        return df
    except Exception: return pd.DataFrame()


@st.cache_data(ttl=1800)
def buscar_dados_horario(ticker):
    """
    Baixa dados de 60 minutos reais do yfinance para um único ticker.
    Limite do yfinance: até 60 dias para interval='60m'.
    Calcula indicadores básicos no índice horário.
    Retorna DataFrame com DatetimeIndex horário ou None se falhar.
    """
    try:
        df = _yf_baixar(
            f"{ticker}.SA",
            period='60d',
            interval='60m',
            auto_adjust=True,
            progress=False,
            timeout=30
        )
        if df is None or df.empty:
            return None
        # Remove MultiIndex se existir
        if isinstance(df.columns, pd.MultiIndex):
            df.columns = df.columns.get_level_values(0)
        df = df.dropna(subset=['Close'])
        df = df.sort_index()
        # Calcula indicadores básicos no timeframe horário
        close = df['Close']
        df['EMA20']    = close.ewm(span=20).mean()
        df['EMA50']    = close.ewm(span=50).mean()
        df['EMA200']   = close.ewm(span=200).mean()
        delta          = close.diff()
        ganho          = delta.clip(lower=0).rolling(14).mean()
        perda          = -delta.clip(upper=0).rolling(14).mean()
        rs             = ganho / perda.replace(0, float('nan'))
        df['RSI14']    = 100 - (100 / (1 + rs))
        sma            = close.rolling(20).mean()
        std            = close.rolling(20).std()
        df['BB_Lower'] = sma - std * 2
        df['BB_Upper'] = sma + std * 2
        low14          = df['Low'].rolling(14).min()
        high14         = df['High'].rolling(14).max()
        rng            = (high14 - low14).replace(0, float('nan'))
        df['Stoch_K']  = 100 * (close - low14) / rng
        ema12          = close.ewm(span=12).mean()
        ema26          = close.ewm(span=26).mean()
        macd           = ema12 - ema26
        df['MACD_Hist']= macd - macd.ewm(span=9).mean()
        return df
    except Exception:
        return None


def buscar_nomes_yahoo(tickers):
    """Busca os nomes das empresas diretamente do Yahoo Finance"""
    mapa_nomes = {}

    # Processar em lotes pequenos para não sobrecarregar
    total = len(tickers)

    if total > 0:
        progresso_nomes = st.progress(0, text="Buscando nomes das empresas...")

        for i, ticker in enumerate(tickers):
            try:
                # Atualizar progresso a cada 5 tickers
                if i % 5 == 0:
                    progresso_nomes.progress(min((i + 1) / total, 1.0),
                                            text=f"Buscando nomes... {i+1}/{total}")

                from modules.yf_session import criar_ticker
                ticker_yf = criar_ticker(f"{ticker}.SA")
                info = ticker_yf.info

                # Tentar pegar o nome na ordem de preferência
                nome = (info.get('longName') or
                       info.get('shortName') or
                       ticker)

                mapa_nomes[ticker] = nome
            except:
                # Se falhar, usar o ticker mesmo
                mapa_nomes[ticker] = ticker

        progresso_nomes.empty()

    return mapa_nomes


def calcular_indicadores(df):
    df_calc = df.copy()
    tickers = df_calc.columns.get_level_values(1).unique()

    progresso = st.progress(0)
    total = len(tickers)

    for i, ticker in enumerate(tickers):
        progresso.progress((i + 1) / total)
        try:
            close = df_calc[('Close', ticker)]
            high = df_calc[('High', ticker)]
            low = df_calc[('Low', ticker)]

            # RSI 14
            delta = close.diff()
            ganho = delta.clip(lower=0).rolling(14).mean()
            perda = -delta.clip(upper=0).rolling(14).mean()
            rs = ganho / perda
            df_calc[('RSI14', ticker)] = 100 - (100 / (1 + rs))

            # ESTOCÁSTICO 14 (%K)
            lowest_low = low.rolling(window=14).min()
            highest_high = high.rolling(window=14).max()
            stoch_k = 100 * ((close - lowest_low) / (highest_high - lowest_low))
            df_calc[('Stoch_K', ticker)] = stoch_k

            # Médias e Bollinger
            df_calc[('EMA20', ticker)] = close.ewm(span=20).mean()
            df_calc[('EMA50', ticker)] = close.ewm(span=50).mean()
            df_calc[('EMA200', ticker)] = close.ewm(span=200).mean()
            sma = close.rolling(20).mean()
            std = close.rolling(20).std()
            df_calc[('BB_Lower', ticker)] = sma - (std * 2)
            df_calc[('BB_Upper', ticker)] = sma + (std * 2)

            # MACD
            ema_12 = close.ewm(span=12).mean()
            ema_26 = close.ewm(span=26).mean()
            macd = ema_12 - ema_26
            signal = macd.ewm(span=9).mean()
            df_calc[('MACD_Hist', ticker)] = macd - signal
        except: continue

    progresso.empty()
    return df_calc


def calcular_fibonacci(df_ticker):
    try:
        if len(df_ticker) < 50: return None
        high = df_ticker['High'].max()
        low = df_ticker['Low'].min()
        diff = high - low
        return {'61.8%': low + (diff * 0.618)}
    except: return None


def gerar_sinal(row_ticker, df_ticker):
    sinais = []
    score = 0
    explicacoes = []  # Nova lista para explicações didáticas

    def classificar(s):
        if s >= 4: return "Muito Alta"
        if s >= 2: return "Alta"
        if s >= 1: return "Média"
        return "Baixa"

    try:
        close = row_ticker.get('Close')
        rsi = row_ticker.get('RSI14')
        stoch = row_ticker.get('Stoch_K')
        macd_hist = row_ticker.get('MACD_Hist')
        bb_lower = row_ticker.get('BB_Lower')

        # Sinais de Reversão
        if pd.notna(rsi):
            if rsi < 30:
                sinais.append("RSI Oversold")
                explicacoes.append(f"📉 RSI em {rsi:.1f} (< 30): Forte sobrevenda, possível reversão iminente")
                score += 3
            elif rsi < 40:
                sinais.append("RSI Baixo")
                explicacoes.append(f"📊 RSI em {rsi:.1f} (< 40): Sobrevenda moderada")
                score += 1

        if pd.notna(stoch):
            if stoch < 20:
                sinais.append("Stoch. Fundo")
                explicacoes.append(f"📉 Estocástico em {stoch:.1f} (< 20): Muito sobrevendido, reversão provável")
                score += 2

        if pd.notna(macd_hist) and macd_hist > 0:
            sinais.append("MACD Virando")
            explicacoes.append("🔄 MACD positivo: Momentum de alta começando")
            score += 1

        if pd.notna(close) and pd.notna(bb_lower):
            if close < bb_lower:
                sinais.append("Abaixo BB")
                explicacoes.append(f"⚠️ Preço abaixo da Banda de Bollinger: Sobrevenda extrema")
                score += 2
            elif close < bb_lower * 1.02:
                sinais.append("Suporte BB")
                explicacoes.append("🎯 Preço próximo da Banda Inferior: Zona de suporte")
                score += 1

        fibo = calcular_fibonacci(df_ticker)
        if fibo and (fibo['61.8%'] * 0.99 <= close <= fibo['61.8%'] * 1.01):
            sinais.append("Fibo 61.8%")
            explicacoes.append("⭐ Preço na Zona de Ouro do Fibonacci (61.8%): Ponto ideal de reversão!")
            score += 2

        return sinais, score, classificar(score), explicacoes
    except:
        return [], 0, "Indefinida", []


def _eh_etf_ticker(ticker):
    """Identifica se um ticker BDR corresponde a um ETF (terminação '39')."""
    return str(ticker).strip().upper().endswith('39')


def _gerar_nome_curto(ticker, nome_completo):
    """
    Gera um nome curto e diferenciado para exibição na tabela.

    Para ETFs (terminação '39'), o padrão "iShares MSCI X", "iShares Core Y",
    "Global X Z" etc. faz com que cortar para 2 palavras gere nomes
    repetidos e genéricos (ex.: "Ishares Msci" para várias linhas).
    Nesses casos, usamos mais palavras (até 4) para manter a parte
    diferenciadora do nome (país/região/tema do fundo).

    Para ações normais, mantém o comportamento original (2 palavras úteis).
    """
    if nome_completo == ticker:
        return ticker

    ignore_list = ['INC', 'CORP', 'LTD', 'S.A.', 'GMBH', 'PLC', 'GROUP',
                    'HOLDINGS', 'CO', 'LLC']
    palavras = nome_completo.split()
    palavras_uteis = [p for p in palavras
                      if p.upper().replace('.', '').replace(',', '') not in ignore_list]

    if not palavras_uteis:
        return nome_completo.replace(',', '').title()

    if _eh_etf_ticker(ticker):
        # Para ETFs, mantém mais palavras para preservar o diferencial
        # (ex.: "iShares MSCI Brazil ETF" -> "Ishares Msci Brazil")
        n_palavras = min(4, len(palavras_uteis))
        # Remove o sufixo genérico "ETF"/"Fund"/"Trust" do final, se sobrar espaço
        candidatos = [p for p in palavras_uteis
                      if p.upper() not in ('ETF', 'FUND', 'TRUST')]
        if len(candidatos) >= 2:
            palavras_uteis = candidatos
        nome_curto = " ".join(palavras_uteis[:n_palavras])
    else:
        nome_curto = " ".join(palavras_uteis[:2])

    return nome_curto.replace(',', '').title()


def analisar_oportunidades(df_calc, mapa_nomes):
    resultados = []
    tickers = df_calc.columns.get_level_values(1).unique()

    for ticker in tickers:
        try:
            df_ticker = df_calc.xs(ticker, axis=1, level=1).dropna()
            if len(df_ticker) < 50: continue

            last = df_ticker.iloc[-1]
            anterior = df_ticker.iloc[-2]

            preco = last.get('Close')
            preco_ant = anterior.get('Close')
            preco_open = last.get('Open')
            volume = last.get('Volume')

            if pd.isna(preco) or pd.isna(preco_ant): continue

            # Variações
            queda_dia = ((preco - preco_ant) / preco_ant) * 100
            gap = ((preco_open - preco_ant) / preco_ant) * 100

            if queda_dia >= 0: continue

            sinais, score, classificacao, explicacoes = gerar_sinal(last, df_ticker)

            # I.S.
            rsi = last.get('RSI14', 50)
            stoch = last.get('Stoch_K', 50)
            is_index = ((100 - rsi) + (100 - stoch)) / 2

            # === RANKING DE LIQUIDEZ (0-10) ===
            try:
                n = min(20, len(df_ticker))
                vol_serie = df_ticker['Volume'].tail(n)
                vol_medio = vol_serie.mean()
                if pd.isna(vol_medio): vol_medio = 0

                # Gaps: dias em que abertura difere >1% do fechamento anterior
                n_gaps = 0
                for i in range(1, min(n + 1, len(df_ticker))):
                    c_ant = df_ticker['Close'].iloc[-i-1]
                    o_at  = df_ticker['Open'].iloc[-i]
                    if c_ant > 0 and abs((o_at - c_ant) / c_ant) * 100 > 1:
                        n_gaps += 1

                # Consistência: proporção de dias com volume ≥ 80% da média
                consist = sum(1 for v in vol_serie if pd.notna(v) and v >= vol_medio * 0.8) / n if n > 0 else 0

                # Score 0-100
                liq = 0
                # Volume (40 pts)
                if   vol_medio > 500000: liq += 40
                elif vol_medio > 100000: liq += 35
                elif vol_medio >  50000: liq += 30
                elif vol_medio >  10000: liq += 25
                elif vol_medio >   5000: liq += 20
                elif vol_medio >   1000: liq += 15
                elif vol_medio >    100: liq += 10
                else:                    liq += 5
                # Gaps (30 pts — menos é melhor)
                if   n_gaps == 0: liq += 30
                elif n_gaps <= 2: liq += 25
                elif n_gaps <= 5: liq += 20
                elif n_gaps <= 8: liq += 15
                elif n_gaps <=12: liq += 10
                else:             liq += 5
                # Consistência (30 pts)
                if   consist >= 0.75: liq += 30
                elif consist >= 0.50: liq += 20
                elif consist >= 0.25: liq += 10
                else:                 liq += 5

                ranking_liq = max(0, min(10, round(liq / 10)))
            except Exception:
                ranking_liq = 1

            # Tratamento de Nome
            nome_completo = mapa_nomes.get(ticker, ticker)
            nome_curto = _gerar_nome_curto(ticker, nome_completo)

            # Volume financeiro (R$/dia) — coerente com o caminho TradingView
            _vol_base = vol_medio if (pd.notna(vol_medio) and vol_medio > 0) else (volume or 0)
            volume_financeiro = float(_vol_base or 0) * float(preco or 0)

            resultados.append({
                'Ticker': ticker,
                'Empresa': nome_curto,
                'Preco': preco,
                'Volume': volume_financeiro,
                'Queda_Dia': queda_dia,
                'Gap': gap,
                'IS': is_index,
                'RSI14': rsi,
                'Stoch': stoch,
                'Potencial': classificacao,
                'Score': score,
                'Sinais': ", ".join(sinais) if sinais else "-",
                'Explicacoes': explicacoes,
                'Liquidez': int(ranking_liq),
                'EMA20': last.get('EMA20'),
                'EMA50': last.get('EMA50'),
                'EMA200': last.get('EMA200'),
            })
        except: continue
    return resultados


# ──────────────────────────────────────────────────────────────────────────────
#  Scanner em massa via TradingView (rápido, sem o bloqueio de IP do Yahoo)
# ──────────────────────────────────────────────────────────────────────────────

# Colunas do TradingView usadas no scanner. O TradingView já entrega os
# indicadores calculados, então uma única requisição substitui o download de
# centenas de tickers no Yahoo.
_TV_CAMPOS = [
    'name', 'description', 'close', 'change', 'gap', 'volume',
    'average_volume_10d_calc', 'RSI', 'Stoch.K',
    'MACD.macd', 'MACD.signal', 'BB.lower',
    'EMA20', 'EMA50', 'EMA200',
]


def _liquidez(vol_medio, preco, volume_hoje=0):
    """Ranking de liquidez 0-10 pelo volume FINANCEIRO médio (R$/dia).

    BDRs negociam poucas ações por dia, então faixas em número de ações quase
    sempre caem no fundo da escala. O volume financeiro (ações × preço) é uma
    medida de liquidez muito mais informativa para BDRs. Usa o volume médio de
    10 dias quando disponível; senão, cai para o volume do dia.
    """
    try:
        vol = float(vol_medio or 0)
        if vol <= 0:
            vol = float(volume_hoje or 0)
        preco = float(preco or 0)
    except (TypeError, ValueError):
        return 1

    financeiro = vol * preco  # R$ negociados por dia (aproximado)
    if financeiro >= 5_000_000: return 10
    if financeiro >= 2_000_000: return 9
    if financeiro >= 1_000_000: return 8
    if financeiro >=   500_000: return 7
    if financeiro >=   200_000: return 6
    if financeiro >=   100_000: return 5
    if financeiro >=    50_000: return 4
    if financeiro >=    20_000: return 3
    if financeiro >=     5_000: return 2
    return 1


def _f(valor, padrao=None):
    """Converte para float com segurança (TradingView pode devolver None)."""
    try:
        if valor is None:
            return padrao
        return float(valor)
    except (TypeError, ValueError):
        return padrao


@st.cache_data(ttl=900, show_spinner=False)
def buscar_oportunidades_tv(lista_bdrs, mapa_nomes):
    """Scanner em massa via TradingView — substitui o caminho yfinance.

    Faz UMA requisição ao screener do mercado brasileiro, filtrando pelos
    tickers de BDR informados, e devolve a MESMA lista de dicts de
    ``analisar_oportunidades`` (já filtrada para quedas no dia).

    Retorna ``None`` se a lib não existir ou a consulta falhar, para que o
    chamador caia no fallback yfinance.
    """
    if not lista_bdrs:
        return None
    try:
        from tradingview_screener import Query, col
    except Exception:
        return None

    try:
        lista_bdrs = list(lista_bdrs)
        _, df = (
            Query()
            .select(*_TV_CAMPOS)
            .where(col('name').isin(lista_bdrs))
            .set_markets('brazil')
            .limit(len(lista_bdrs) + 100)
            .get_scanner_data()
        )
    except Exception:
        return None

    if df is None or df.empty:
        return None

    resultados = []
    for _, row in df.iterrows():
        try:
            ticker = str(row.get('name', '')).split(':')[-1]
            preco = _f(row.get('close'))
            queda_dia = _f(row.get('change'))
            if preco is None or queda_dia is None:
                continue
            if queda_dia >= 0:        # só quedas, como no caminho original
                continue

            rsi = _f(row.get('RSI'), 50.0)
            stoch = _f(row.get('Stoch.K'), 50.0)
            macd_hist = _f(row.get('MACD.macd'), 0.0) - _f(row.get('MACD.signal'), 0.0)
            bb_lower = _f(row.get('BB.lower'))
            volume = _f(row.get('volume'), 0.0)
            vol_medio = _f(row.get('average_volume_10d_calc'), 0.0)
            gap = _f(row.get('gap'), 0.0)

            # Volume FINANCEIRO (R$/dia): volume médio de 10d (ou do dia) × preço.
            # Mais legível e coerente com o ranking de liquidez do que a contagem
            # de ações, que para BDRs costuma ser baixíssima.
            vol_base = vol_medio if vol_medio > 0 else volume
            volume_financeiro = vol_base * preco

            # Reaproveita gerar_sinal montando a linha com os campos esperados.
            # Sem histórico, o sinal de Fibonacci é ignorado (calcular_fibonacci(None)).
            linha = pd.Series({
                'Close': preco,
                'RSI14': rsi,
                'Stoch_K': stoch,
                'MACD_Hist': macd_hist,
                'BB_Lower': bb_lower,
            })
            sinais, score, classificacao, explicacoes = gerar_sinal(linha, None)

            is_index = ((100 - rsi) + (100 - stoch)) / 2
            ranking_liq = _liquidez(vol_medio, preco, volume)

            nome_completo = (str(row.get('description') or '').strip()
                             or mapa_nomes.get(ticker, ticker))
            nome_curto = _gerar_nome_curto(ticker, nome_completo)

            resultados.append({
                'Ticker': ticker,
                'Empresa': nome_curto,
                'Preco': preco,
                'Volume': volume_financeiro,
                'Queda_Dia': queda_dia,
                'Gap': gap,
                'IS': is_index,
                'RSI14': rsi,
                'Stoch': stoch,
                'Potencial': classificacao,
                'Score': score,
                'Sinais': ", ".join(sinais) if sinais else "-",
                'Explicacoes': explicacoes,
                'Liquidez': int(ranking_liq),
                'EMA20': _f(row.get('EMA20')),
                'EMA50': _f(row.get('EMA50')),
                'EMA200': _f(row.get('EMA200')),
            })
        except Exception:
            continue

    return resultados or None


@st.cache_data(ttl=900, show_spinner=False)
def obter_historico_ticker(ticker):
    """Histórico diário + indicadores de UM ticker (para gráfico/detalhe).

    Substitui o antigo ``df_calc.xs(ticker)``: como o scanner não baixa mais o
    histórico de todos os tickers, o detalhe do ticker selecionado é buscado sob
    demanda (1 ticker = rápido e raramente sofre rate limit). Retorna um
    DataFrame de colunas simples (Close, Open, High, Low, Volume + indicadores)
    ou ``None``.
    """
    try:
        df = _yf_baixar(f"{ticker}.SA", period=PERIODO, auto_adjust=True,
                        progress=False, timeout=30)
        if df is None or df.empty:
            return None
        if isinstance(df.columns, pd.MultiIndex):
            df.columns = df.columns.get_level_values(0)
        df = df.dropna(subset=['Close'])
        if df.empty:
            return None

        close, high, low = df['Close'], df['High'], df['Low']
        delta = close.diff()
        ganho = delta.clip(lower=0).rolling(14).mean()
        perda = -delta.clip(upper=0).rolling(14).mean()
        rs = ganho / perda
        df['RSI14'] = 100 - (100 / (1 + rs))
        lowest_low = low.rolling(window=14).min()
        highest_high = high.rolling(window=14).max()
        df['Stoch_K'] = 100 * ((close - lowest_low) / (highest_high - lowest_low))
        df['EMA20'] = close.ewm(span=20).mean()
        df['EMA50'] = close.ewm(span=50).mean()
        df['EMA200'] = close.ewm(span=200).mean()
        sma = close.rolling(20).mean()
        std = close.rolling(20).std()
        df['BB_Lower'] = sma - (std * 2)
        df['BB_Upper'] = sma + (std * 2)
        ema_12 = close.ewm(span=12).mean()
        ema_26 = close.ewm(span=26).mean()
        macd = ema_12 - ema_26
        df['MACD_Hist'] = macd - macd.ewm(span=9).mean()
        return df
    except Exception:
        return None


def plotar_grafico(df_ticker, ticker, empresa, rsi, is_val,
                   timeframe='Diário', zoom_periods=None, tipo_grafico='Linha',
                   df_horario=None, preco_atual=None, emas_atual=None):
    """
    Plota o gráfico técnico principal com suporte a:
      - timeframe  : 'Horário (60min)' | 'Diário' | 'Semanal' | 'Mensal'
      - zoom_periods: número de barras a exibir (None = tudo)
      - tipo_grafico: 'Linha' | 'Candlestick'
      - df_horario : DataFrame com dados reais de 60min (opcional, usado no timeframe horário)
      - preco_atual / emas_atual: preço e EMAs ATUAIS do screener (TradingView). Quando
        informados, o status de tendência no título usa esses valores — a mesma base do
        filtro de EMAs — em vez do último fechamento do yfinance (que para BDRs ilíquidas
        pode estar defasado). As linhas do gráfico continuam vindo do histórico yfinance.
    """
    import matplotlib.dates as mdates
    from matplotlib.patches import Rectangle

    colunas_necessarias = ['Close', 'Open', 'High', 'Low', 'Volume',
                           'EMA20', 'RSI14', 'Stoch_K', 'BB_Lower', 'BB_Upper']
    colunas_opcionais   = ['EMA50', 'EMA200', 'MACD_Hist']

    # ── Seleciona e reamostrar os dados conforme timeframe ───────────────────────
    tf_label = timeframe

    if timeframe == 'Horário (60min)':
        # Usa dados reais de 60min se disponíveis, senão avisa
        if df_horario is not None and not df_horario.empty:
            colunas_pres = [c for c in colunas_necessarias + colunas_opcionais
                            if c in df_horario.columns]
            df = df_horario[colunas_pres].dropna(subset=['Close']).copy()
            tf_label = 'Horário (60min) — últimos 60 dias'
        else:
            # Fallback: dados diários dos últimos 30 pregões
            colunas_pres = [c for c in colunas_necessarias + colunas_opcionais
                            if c in df_ticker.columns]
            df = df_ticker[colunas_pres].dropna(subset=['Close']).copy()
            df = df.iloc[-30:]
            tf_label = 'Horário (60min) — dados diários (fallback)'
    else:
        colunas_pres = [c for c in colunas_necessarias + colunas_opcionais
                        if c in df_ticker.columns]
        df_full = df_ticker[colunas_pres].dropna(subset=['Close', 'EMA20']).copy()
        df_full = df_full.sort_index()

        if timeframe == 'Semanal':
            agg = {c: ('first' if c == 'Open' else 'max' if c == 'High' else
                       'min' if c == 'Low' else 'last' if c == 'Close' else
                       'sum' if c == 'Volume' else 'last') for c in colunas_pres}
            df = df_full.resample('W').agg(agg).dropna(subset=['Close'])
        elif timeframe == 'Mensal':
            agg = {c: ('first' if c == 'Open' else 'max' if c == 'High' else
                       'min' if c == 'Low' else 'last' if c == 'Close' else
                       'sum' if c == 'Volume' else 'last') for c in colunas_pres}
            df = df_full.resample('ME').agg(agg).dropna(subset=['Close'])
        else:   # Diário
            df = df_full.copy()

    # ── Aplicar Zoom ─────────────────────────────────────────────────────────────
    if zoom_periods and zoom_periods < len(df):
        df = df.iloc[-zoom_periods:].copy()

    close  = df['Close']
    ema20  = df['EMA20']  if 'EMA20'  in df.columns else None
    ema50  = df['EMA50']  if 'EMA50'  in df.columns else None
    ema200 = df['EMA200'] if 'EMA200' in df.columns else None
    datas  = df.index

    fig, axes = plt.subplots(3, 1, figsize=(12, 9), sharex=True,
                             gridspec_kw={'height_ratios': [3, 1, 1]})

    # ── Fibonacci ────────────────────────────────────────────────────────────────
    high = df['High'].max() if 'High' in df.columns else close.max()
    low  = df['Low'].min()  if 'Low'  in df.columns else close.min()
    diff = high - low

    fib_levels = {
        '0%':    high,
        '23.6%': high - diff * 0.236,
        '38.2%': high - diff * 0.382,
        '50%':   high - diff * 0.500,
        '61.8%': high - diff * 0.618,
        '78.6%': high - diff * 0.786,
        '100%':  low,
    }
    fib_colors = {
        '0%':    '#e74c3c', '23.6%': '#e67e22', '38.2%': '#f39c12',
        '50%':   '#3498db', '61.8%': '#2ecc71',
        '78.6%': '#1abc9c', '100%':  '#9b59b6',
    }

    # ── Painel 1: Preço + EMAs + Fibonacci + Bollinger ───────────────────────────
    ax1 = axes[0]

    # Bollinger (fundo, discreta)
    if 'BB_Lower' in df.columns and 'BB_Upper' in df.columns:
        ax1.fill_between(datas, df['BB_Lower'], df['BB_Upper'],
                         alpha=0.07, color='#607d8b', zorder=0)

    # Fibonacci
    for nivel, preco_fib in fib_levels.items():
        cor = fib_colors[nivel]
        ax1.axhline(preco_fib, color=cor, linestyle='--', linewidth=0.9,
                    alpha=0.55, zorder=1)
        ax1.text(datas[-1], preco_fib, f' Fib {nivel}',
                 fontsize=7.5, color=cor, va='center',
                 bbox=dict(boxstyle='round,pad=0.2', facecolor='white',
                           edgecolor=cor, alpha=0.75))

    # Zona de ouro (61.8%)
    ax1.axhspan(fib_levels['61.8%'] * 0.99, fib_levels['61.8%'] * 1.01,
                alpha=0.12, color='#2ecc71', zorder=0, label='Zona de Ouro')

    # EMAs — plotadas antes do preço para não sobrepor
    if ema20 is not None:
        ax1.plot(datas, ema20,  label='EMA20',  color='#2962FF',
                 linewidth=1.4, alpha=0.9, zorder=3)
    if ema50 is not None:
        ema50_alinhada = ema50.reindex(datas)
        ax1.plot(datas, ema50_alinhada, label='EMA50', color='#FF6D00',
                 linewidth=1.4, alpha=0.85, zorder=3)
    if ema200 is not None:
        ema200_alinhada = ema200.reindex(datas)
        ax1.plot(datas, ema200_alinhada, label='EMA200', color='#00695C',
                 linewidth=1.8, alpha=0.8, zorder=3)

    # ── Candlestick ou Linha ──────────────────────────────────────────────────
    if tipo_grafico == 'Candlestick' and 'Open' in df.columns and 'High' in df.columns and 'Low' in df.columns:
        # Largura dinâmica das velas conforme número de barras
        n_barras = len(datas)
        if n_barras <= 30:
            largura_vela = 0.6
        elif n_barras <= 60:
            largura_vela = 0.5
        elif n_barras <= 120:
            largura_vela = 0.4
        else:
            largura_vela = 0.3

        # Converter datas para números matplotlib para posicionamento
        import matplotlib.dates as mdates_inner
        datas_num = mdates_inner.date2num(datas.to_pydatetime())
        largura_dias = largura_vela  # em unidades de dias matplotlib

        for i, (data_num, row_c) in enumerate(zip(datas_num, df.itertuples())):
            op  = getattr(row_c, 'Open',  None)
            hi  = getattr(row_c, 'High',  None)
            lo  = getattr(row_c, 'Low',   None)
            cl  = getattr(row_c, 'Close', None)
            if any(v is None or (hasattr(v, '__class__') and v.__class__.__name__ == 'float' and str(v) == 'nan') for v in [op, hi, lo, cl]):
                continue
            import math
            if any(math.isnan(float(v)) for v in [op, hi, lo, cl]):
                continue

            cor_vela   = '#26a69a' if float(cl) >= float(op) else '#ef5350'
            cor_pavio  = '#26a69a' if float(cl) >= float(op) else '#ef5350'
            corpo_min  = min(float(op), float(cl))
            corpo_max  = max(float(op), float(cl))
            corpo_h    = max(corpo_max - corpo_min, 0.0001)

            # Pavio (sombra)
            ax1.plot([data_num, data_num], [float(lo), float(hi)],
                     color=cor_pavio, linewidth=0.8, zorder=4)
            # Corpo
            rect = Rectangle(
                (data_num - largura_dias / 2, corpo_min),
                largura_dias, corpo_h,
                facecolor=cor_vela, edgecolor=cor_pavio,
                linewidth=0.4, zorder=5
            )
            ax1.add_patch(rect)

        # Ponto de fechamento mais recente destacado
        ultimo_num = datas_num[-1]
        ax1.scatter([ultimo_num], [close.iloc[-1]], color='#e74c3c',
                    s=50, zorder=7)
    else:
        # Linha padrão
        ax1.plot(datas, close, label='Close', color='#1a1a2e',
                 linewidth=2.2, zorder=5)
        # Ponto de fechamento mais recente destacado
        ax1.scatter([datas[-1]], [close.iloc[-1]], color='#e74c3c',
                    s=40, zorder=6)

    # Tendência atual — prioriza os valores ATUAIS do screener (TradingView), que
    # são a mesma base do filtro de EMAs; cai para o último valor do yfinance quando
    # não informados (mantém o status coerente com a tabela e o filtro).
    ult_close = close.iloc[-1]
    ult_ema20 = ema20.iloc[-1]
    ult_ema50  = ema50.reindex(datas).iloc[-1]  if ema50  is not None else None
    ult_ema200 = ema200.reindex(datas).iloc[-1] if ema200 is not None else None

    def _ou(valor, alternativa):
        return valor if (valor is not None and pd.notna(valor)) else alternativa

    _em = emas_atual or {}
    pc   = _ou(preco_atual, ult_close)
    e20  = _ou(_em.get('EMA20'),  ult_ema20)
    e50  = _ou(_em.get('EMA50'),  ult_ema50)
    e200 = _ou(_em.get('EMA200'), ult_ema200)

    if e50 is not None and e200 is not None and pd.notna(e50) and pd.notna(e200):
        if pc > e20 > e50 > e200:
            status = "🟢 Tendência Forte de Alta"
        elif pc > e20 and pc > e50 and pc > e200:
            status = "🟢 Acima das 3 EMAs"
        elif pc < e20 and pc < e50 and pc < e200:
            status = "🔴 Abaixo das 3 EMAs"
        elif pc > e200:
            status = "🟡 Mista (acima da EMA200)"
        else:
            status = "🟡 Mista (abaixo da EMA200)"
    else:
        status = "🟢 Acima EMA20" if pc > e20 else "🔴 Abaixo EMA20"

    # Fibonacci mais próximo
    nivel_mais_proximo = min(fib_levels, key=lambda n: abs(ult_close - fib_levels[n]))

    zoom_info = f' | Zoom: {zoom_periods} barras' if zoom_periods else ''
    ax1.set_title(
        f'{ticker} - {empresa} | {tf_label} | I.S.: {is_val:.0f} | {status} | Próx. Fib: {nivel_mais_proximo}{zoom_info}',
        fontweight='bold', fontsize=10, pad=6)
    ax1.legend(loc='upper left', fontsize=7, framealpha=0.92, ncol=3)
    ax1.grid(True, alpha=0.18, zorder=0)
    ax1.set_ylabel('Preço (R$)', fontsize=9)

    # ── Painel 2: RSI ─────────────────────────────────────────────────────────────
    ax2 = axes[1]
    if 'RSI14' in df.columns:
        rsi_vals = df['RSI14'].reindex(datas)
        ax2.plot(datas, rsi_vals, color='#FF6F00', linewidth=1.5, label='RSI14')
        ax2.axhline(30, color='#F44336', linestyle='--', linewidth=1, alpha=0.7)
        ax2.axhline(70, color='#4CAF50', linestyle='--', linewidth=1, alpha=0.7)
        ax2.fill_between(datas, 0,  30, alpha=0.15, color='#F44336')
        ax2.fill_between(datas, 70, 100, alpha=0.15, color='#4CAF50')
    ax2.set_ylabel('RSI', fontsize=9)
    ax2.set_ylim(0, 100)
    ax2.grid(True, alpha=0.18)

    # ── Painel 3: Estocástico ─────────────────────────────────────────────────────
    ax3 = axes[2]
    if 'Stoch_K' in df.columns:
        stoch_vals = df['Stoch_K'].reindex(datas)
        ax3.plot(datas, stoch_vals, color='#9C27B0', linewidth=1.5, label='Stoch %K')
        ax3.axhline(20, color='#F44336', linestyle='--', linewidth=1, alpha=0.7)
        ax3.axhline(80, color='#4CAF50', linestyle='--', linewidth=1, alpha=0.7)
        ax3.fill_between(datas, 0,  20, alpha=0.15, color='#F44336')
        ax3.fill_between(datas, 80, 100, alpha=0.15, color='#4CAF50')
    ax3.set_ylabel('Stoch', fontsize=9)
    ax3.set_ylim(0, 100)
    ax3.grid(True, alpha=0.18)

    # ── Eixo X — formatação exata por timeframe ──────────────────────────────────
    ax3 = axes[2]
    n_barras = len(df)

    if timeframe == 'Horário (60min)':
        # Horas: "10h", "11h", "12h" — major = cada hora, minor = nada
        ax3.xaxis.set_major_formatter(mdates.DateFormatter('%d/%b %Hh'))
        # Intervalo adaptativo: 1h se poucos dados, senão a cada 4h ou 8h
        if n_barras <= 48:
            ax3.xaxis.set_major_locator(mdates.HourLocator(interval=2))
        elif n_barras <= 200:
            ax3.xaxis.set_major_locator(mdates.HourLocator(interval=4))
        else:
            ax3.xaxis.set_major_locator(mdates.HourLocator(interval=8))

    elif timeframe == 'Diário':
        # Dias: "11/Mai", "12/Mai", etc.
        ax3.xaxis.set_major_formatter(mdates.DateFormatter('%d/%b'))
        # Intervalo adaptativo por quantidade de barras visíveis
        if n_barras <= 30:
            ax3.xaxis.set_major_locator(mdates.DayLocator(interval=1))
        elif n_barras <= 90:
            ax3.xaxis.set_major_locator(mdates.DayLocator(interval=5))
        elif n_barras <= 180:
            ax3.xaxis.set_major_locator(mdates.DayLocator(interval=10))
        else:
            ax3.xaxis.set_major_locator(mdates.MonthLocator(interval=1))
            ax3.xaxis.set_major_formatter(mdates.DateFormatter('%b/%y'))

    elif timeframe == 'Semanal':
        # Semanas: "W19/Mai", início de cada semana
        ax3.xaxis.set_major_formatter(mdates.DateFormatter('%d/%b/%y'))
        if n_barras <= 26:
            ax3.xaxis.set_major_locator(mdates.WeekdayLocator(byweekday=0, interval=1))
        else:
            ax3.xaxis.set_major_locator(mdates.WeekdayLocator(byweekday=0, interval=2))

    elif timeframe == 'Mensal':
        # Meses: "Jan/25", "Fev/25", etc. — um rótulo por mês
        ax3.xaxis.set_major_formatter(mdates.DateFormatter('%b/%y'))
        ax3.xaxis.set_major_locator(mdates.MonthLocator(interval=1))

    plt.setp(ax3.xaxis.get_majorticklabels(),
             rotation=40, ha='right', fontsize=9, fontweight='600', color='#334155')
    ax3.tick_params(axis='x', which='major', pad=6, length=4, color='#94a3b8')
    ax3.set_xlabel('', fontsize=0)   # sem label redundante; o formato já é autoexplicativo

    # Grade vertical suave em todos os painéis
    for ax in axes:
        ax.xaxis.grid(True, alpha=0.10, color='#94a3b8', linestyle='-')

    plt.tight_layout(rect=[0, 0, 1, 1])
    fig.subplots_adjust(bottom=0.13)
    return fig
