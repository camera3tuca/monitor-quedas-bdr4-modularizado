"""Sessão compartilhada e downloads resilientes para o yfinance.

Centraliza, num único lugar, a estratégia para evitar o erro
``YFRateLimitError: Too Many Requests`` do Yahoo Finance:

  * Uma sessão HTTP com impersonação de navegador via ``curl_cffi`` (forma
    recomendada pelo yfinance para não ser bloqueado), criada **uma por thread**
    (thread-local) — sessões do curl_cffi não são thread-safe e o app faz
    downloads em paralelo.
  * Um wrapper ``baixar()`` em volta de ``yf.download`` com retry e backoff
    exponencial + jitter especificamente nos erros de rate limit.

Tudo com degradação graciosa: se ``curl_cffi`` não existir, ou se a versão do
yfinance não aceitar o parâmetro ``session=``, o código cai de volta no
comportamento padrão sem quebrar.
"""

import time
import random
import threading

import yfinance as yf

# Sessão por thread: sessões do curl_cffi não são thread-safe, então cada
# thread (ThreadPoolExecutor das notícias, threads internas do yf.download...)
# recebe a sua. Valor por thread: None = não inicializado; um Session = ok;
# False = curl_cffi indisponível (usar comportamento padrão do yfinance).
_local = threading.local()


def get_session():
    """Retorna (e memoiza por thread) uma sessão curl_cffi com impersonação.

    Retorna ``False`` se ``curl_cffi`` não estiver disponível, sinalizando que
    os downloads devem usar o comportamento padrão do yfinance.
    """
    sess = getattr(_local, 'session', None)
    if sess is not None:
        return sess
    try:
        from curl_cffi import requests as cffi_requests
        sess = cffi_requests.Session(impersonate="chrome")
    except Exception:
        sess = False
    _local.session = sess
    return sess


def criar_ticker(symbol):
    """Retorna um ``yf.Ticker`` usando a sessão com impersonação quando possível."""
    sess = get_session()
    if sess:
        try:
            return yf.Ticker(symbol, session=sess)
        except TypeError as exc:
            # Só cai no fallback se o erro for sobre o parâmetro `session=`;
            # outros TypeError (kwarg inválido) devem subir.
            if 'session' not in str(exc):
                raise
            return yf.Ticker(symbol)
    return yf.Ticker(symbol)


def _eh_rate_limit(exc):
    """Heurística para detectar erro de rate limit independente da versão do yfinance."""
    nome = type(exc).__name__.lower()
    msg = str(exc).lower()
    return (
        "ratelimit" in nome
        or "too many requests" in msg
        or "rate limit" in msg
        or "429" in msg
    )


def _download_once(tickers, **kwargs):
    """Chama yf.download usando a sessão custom quando possível."""
    sess = get_session()
    if sess:
        try:
            return yf.download(tickers, session=sess, **kwargs)
        except TypeError as exc:
            # Versão do yfinance que não aceita `session=` (usa curl_cffi interno).
            # Outros TypeError (kwarg inválido) devem subir, não ser mascarados.
            if 'session' not in str(exc):
                raise
            return yf.download(tickers, **kwargs)
    return yf.download(tickers, **kwargs)


def baixar(tickers, *, max_tentativas=4, base_sleep=2.0, **kwargs):
    """yf.download resiliente: retry com backoff exponencial em rate limit.

    Aceita os mesmos kwargs de ``yf.download`` (period, interval, auto_adjust,
    progress, timeout, threads, ...). Retorna o DataFrame baixado, ou um
    DataFrame vazio se todas as tentativas falharem.

    Apenas erros de rate limit são repetidos; demais exceções sobem para o
    chamador tratar (ex.: ticker delisted).
    """
    import pandas as pd

    for tentativa in range(max_tentativas):
        try:
            return _download_once(tickers, **kwargs)
        except Exception as exc:  # noqa: BLE001
            if not _eh_rate_limit(exc) or tentativa == max_tentativas - 1:
                if _eh_rate_limit(exc):
                    return pd.DataFrame()
                raise
            # Backoff exponencial com jitter: 2s, 4s, 8s (+/- aleatório).
            espera = base_sleep * (2 ** tentativa) + random.uniform(0, 1)
            time.sleep(espera)
    # Só alcançável se max_tentativas <= 0 (o loop sempre retorna ou levanta).
    return pd.DataFrame()
