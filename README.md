# 📈 Intraday Momentum Strategy – SPY ETF
[![SSRN Paper](https://img.shields.io/badge/Paper-SSRN-blue)](https://papers.ssrn.com/sol3/papers.cfm?abstract_id=4824172)

This repository implements and analyzes the strategy described in the paper:
“Beat the Market: An Effective Intraday Momentum Strategy for S&P500 ETF (SPY)”.

It includes end-to-end data acquisition, preprocessing, indicator calculation, strategy backtesting, and performance evaluation, all applied to SPY intraday data from Polygon.io.


## 🎯 Objective

To replicate and evaluate an intraday momentum strategy that uses dynamic volatility bands and VWAP to generate long/short signals on the SPY ETF. The strategy is compared against a passive S&P 500 buy-and-hold benchmark using historical data.


## 🧱 Project Structure and order of execution

1. `download_market_data.py`   -->	 Downloads minute-level and daily OHLCV data from Polygon.io, along with dividend events. (No need to execute, price data files already in folder).
2. `prepare_indicators.py`	   -->   Prepares required features per minute: VWAP, volatility bands (sigma_open), and open-relative returns.
3. `backtest_strategy.py`	   -->   Runs the core backtest logic, simulates trade entries/exits based on band breakouts and VWAP filters, and logs trades to trades.csv.
4. `check_results.py`	       -->   Post-backtest performance analysis, including Sharpe, alpha, beta, win rate, drawdown, and monthly/yearly return tables.

`Polygon_Vs_Alpaca_Market_Data/` --> (Optional) Script-based comparison between Polygon.io and Alpaca market data. This folder is not essential to the main project and serves only to investigate minor timestamp and value discrepancies between the two data providers.



## 📈 Output

- `trades.csv`: All simulated trades, including time, price, size, side (long/short), P&L, and reason for exit.

- Strategy vs. Benchmark plot

- Summary statistics and regression metrics (alpha, beta)

- Monthly & yearly return breakdown

- Long vs. short trade summary


## 📎 Additionally

- `concretum_bands_pine_code.txt`   -->   Pine Script code for TradingView to visualize the upper and lower bands (UB, LB) and VWAP used by the strategy. Useful for visually validating trade signals and price behavior.

- `Beat the Market An Effective Intraday Momentum Strategy for S&P500 ETF (SPY).pdf`  -->  Original research paper detailing the logic and theoretical motivation behind the intraday momentum strategy implemented in this project.


These resources are provided for full transparency and reproducibility of the strategy, and to allow further experimentation or validation in platforms like TradingView.

