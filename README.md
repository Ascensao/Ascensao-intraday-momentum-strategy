# 📈 Intraday Momentum Strategy – SPY ETF  
[![SSRN Paper](https://img.shields.io/badge/Paper-SSRN-blue)](https://papers.ssrn.com/sol3/papers.cfm?abstract_id=4824172)

This repository replicates and evaluates the strategy presented in the paper:  
[**“Beat the Market: An Effective Intraday Momentum Strategy for S&P500 ETF (SPY)”**](https://papers.ssrn.com/sol3/papers.cfm?abstract_id=4824172).

It provides an end-to-end pipeline covering data acquisition, preprocessing, feature engineering, backtesting, and performance evaluation using SPY intraday data from Polygon.io.

---

## 🎯 Objective

To replicate and validate an intraday momentum strategy based on VWAP and dynamic volatility bands (σ_open), designed to generate long/short signals on the SPY ETF. Strategy performance is benchmarked against a passive S&P 500 buy-and-hold portfolio.

---

## 🧱 Project Structure (Execution Order)

1. `download_market_data.py`  
   Downloads minute-level and daily OHLCV data from Polygon.io, along with dividend events.  
   ⚠️ _Note: Data files are already included. This repository contains data starting from 2019 due to GitHub’s 100MB file size constraint._

2. `prepare_indicators.py`  
   Computes VWAP, open-relative returns, σ_open, and other required features on a per-minute basis.

3. `backtest_strategy.py`  
   Implements the trading logic, executes backtests, and logs all trades (with timestamps, entry/exit prices, size, P&L, and exit reason) into `trades.csv`.

4. `check_results.py`  
   Performs post-analysis: Sharpe ratio, alpha, beta, drawdowns, win rate, and detailed monthly/yearly return breakdowns.

5. `Polygon_Vs_Alpaca_Market_Data/`  
   _Optional:_ Scripts for comparing Alpaca vs. Polygon data quality. Not required for running the strategy. Included only for transparency and inspection of data discrepancies (timestamp alignment, row count, OHLCV values, etc.).

---

## 📈 Output

- `trades.csv` — Complete trade log (side, size, entry/exit time & price, P&L, reason)
- Strategy vs. S&P 500 (Buy & Hold) performance plot
- Sharpe ratio, alpha, beta, max drawdown, win rate
- Monthly and yearly return tables
- Long/short trade breakdown

---

## 📊 Strategy Results & Replication Accuracy

The following visuals demonstrate the replication’s accuracy when compared with the original paper’s reported results:

### 📈 Strategy vs. Buy & Hold

<img width="937" height="474" alt="strategy" src="https://github.com/user-attachments/assets/34776315-d627-48e0-9b0f-706e78d18a48" />

This chart shows cumulative returns of the replicated intraday strategy versus a passive SPY buy-and-hold.

---

### 📅 Monthly Return Comparison

<img width="1400" height="281" alt="compare_returns" src="https://github.com/user-attachments/assets/d081f357-e727-45b8-b9f2-66cadd5079a1" />

Monthly returns from the original paper (**PDF**) and this repository’s backtest (**TEST**) for 2016–2024.

📌 _The replication aligns closely with the original paper’s yearly returns, reinforcing the reliability of the implementation._

---

## 📎 Additional Resources

- `concretum_bands_pine_code.txt`  
  Pine Script for TradingView to plot VWAP and the upper/lower trading bands (UB/LB) used in the strategy. Useful for visual validation of signal logic.

---

This repository aims to provide a transparent, reproducible, and well-structured implementation of the strategy for further research, analysis, or adaptation.
