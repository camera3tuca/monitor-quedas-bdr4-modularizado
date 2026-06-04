# monitor-quedas-bdr4-modularizado
Monitor quedas de BDRs modularizado.

Este projeto é uma aplicação [Streamlit](https://streamlit.io/) avançada para monitoramento, análise e predição de BDRs (Brazilian Depositary Receipts) listados na B3, focada em Swing Trade.

## 📂 Estrutura do Projeto (Módulos)

O projeto foi refatorado em vários módulos independentes dentro da pasta `modules/`, visando facilitar a manutenção, documentação e evolução do código. Cada módulo é responsável por um domínio específico da aplicação:

### 1. `technical.py` (Análise Técnica & Sinais)
Responsável por baixar os dados de mercado (`yfinance`) em variados timeframes (diário, horário) e calcular os indicadores técnicos principais.
- **Indicadores Calculados:** RSI, Estocástico, Bandas de Bollinger, MACD, EMAs (20, 50, 200).
- **Funções de Análise:** Identificação de Sinais de Reversão, zonas de ouro de Fibonacci e cálculos do Índice de Sobrevenda (IS).
- **Gráficos:** Contém a função de renderização gráfica em múltiplos painéis (`plotar_grafico`) usando Matplotlib.

### 2. `fundamentals.py` (Análise Fundamentalista)
Busca, processa e pontua os dados fundamentalistas das empresas (P/E Ratio, Dividend Yield, Market Cap, etc.).
- Utiliza diversas fontes com fallback automático: Yahoo Finance, OpenBB / FMP e BRAPI.
- Calcula um "Score Fundamentalista" (0 a 100) refletindo a saúde financeira e valuation da companhia.

### 3. `minervini.py` (Análise de Fase Minervini / Stan Weinstein)
Implementa o *Trend Template* desenvolvido por Mark Minervini e a análise de 4 Fases de Stan Weinstein.
- Identifica se o ativo está em fase de acumulação, uptrend (Fase 2), distribuição ou downtrend.
- Avalia Relative Strength (Força Relativa) contra o índice IBOV e calcula zonas ótimas para alocação de Stop Loss e Risk/Reward.

### 4. `triple_screen.py` (Estratégia Triple Screen - Alexander Elder)
Implementa o sistema de três telas (A Maré, A Onda, A Execução).
- Analisa tendências de longo/médio prazo para validar pontos de entrada no curto prazo, operando sempre a favor da "maré" do mercado.

### 5. `ml.py` (Previsão via Machine Learning - Ensemble)
Aplica técnicas clássicas de Machine Learning para predição direcional e variação do preço nos próximos dias úteis.
- **Modelos treinados em tempo real:** Gradient Boosting, Random Forest, Extra Trees, Elastic Net, e Regressão Linear.
- Engenharia de features: retornos multi-período (1d, 5d, 15d), volatilidade realizada, e distâncias das EMAs.
- O modelo com o melhor R² no conjunto de teste é automaticamente selecionado para a predição.

### 6. `rl.py` (Agente de Reinforcement Learning - Deep Q-Learning)
Implementa um agente autônomo baseado em Deep Q-Learning (DQN) que simula compras e vendas.
- O agente aprende uma política de trading maximizando os lucros (PnL) baseando-se em diferenças de preços em uma janela deslizante.
- Inclui uma interface (painel) para visualizar os sinais do agente (Buy / Hold / Sell) no conjunto de teste recente.

### 7. `tradingview.py` (TradingView Screener & Dados ao Vivo)
Integra-se com a API oficial do TradingView Screener (sem web scraping) para capturar dezenas de indicadores técnicos simultâneos.
- Gera sinais agregados de "Compra Forte", "Venda", etc., baseados na ponderação do TV para RSI, MACD, EMAs.
- Coleta também informações dos principais pares/concorrentes (peers) do mesmo setor.

### 8. `news.py` (Agregador de Notícias & Análise de Sentimento com IA)
Busca, filtra e traduz notícias em tempo real de várias fontes globais.
- **Fontes Suportadas:** Yahoo Finance, Google News, Seeking Alpha, GuruFocus, MarketWatch e Finviz.
- **Tradução:** As notícias são automaticamente traduzidas para português.
- **Sentimento com IA (Claude):** Através de prompts para a API da Anthropic, gera um sumário executivo, destacando fatores de alta, fatores de baixa e dando um "score" geral para o sentimento do mercado sobre a empresa.

### 9. `styles.py` (Estilos & UI)
Isola as configurações de formatação visual (CSS in-line ou helpers Streamlit) e esquemas de cores.
- Contém funções que colorem tabelas e métricas baseadas no Índice de Sobrevenda, Pontuação Fundamentalista e níveis de liquidez.

## 🚀 Como Executar o App

Para inicializar a aplicação principal, certifique-se de instalar as dependências e então execute:

```bash
pip install -r requirements.txt
streamlit run app.py
```
