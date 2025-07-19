## `fetch_data.py`

#### Este script conecta-se à API da Polygon.io para obter dados históricos do ETF SPY. Ele coleta:

- Dados intradiários (1 minuto) durante o horário regular do mercado (09:30–15:59)
- Dados diários (OHLCV)
- Histórico de dividendos

##### Os dados são salvos localmente em arquivos CSV:

- `spy_intra_data.csv`

- `spy_daily_data.csv`

- `spy_dividends.csv`

---

## `prepare_indicators.py`

Este script processa os dados intradiários do SPY (1 minuto) e calcula os principais indicadores necessários para o backtest da estratégia.

#### ✅ O que o script faz:

1. Carrega os dados salvos:

- spy_intra_data.csv (dados intradiários)
- spy_dividends.csv (dados de dividendos)


2. Prepara o DataFrame:

- Converte a coluna de data/hora (caldt)
- Extrai apenas a data (day) para análise diária
- Define o índice como datetime para facilitar operações temporais


3. Agrupa os dados por dia:

- Para calcular métricas diárias como VWAP, volatilidade, etc.
- Calcula os indicadores:
- vwap: Volume Weighted Average Price diário
- move_open: Variação percentual absoluta em relação à abertura
- spy_dvol: Volatilidade móvel de 15 dias (baseada nos fechamentos diários)
- sigma_open: Desvio padrão (σ) da variação da abertura, por minuto do dia


4. Adiciona métricas por minuto:

- Calcula o número de minutos desde a abertura (09:30)
- Agrupa por minute_of_day e calcula médias móveis e sigma_open


5. Integra os dividendos:

- Mescla os dividendos com base nas datas de ex-dividendo
- Preenche valores ausentes com 0


6. Salva o resultado final:

- Exporta o DataFrame processado como spy_processed_data.csv