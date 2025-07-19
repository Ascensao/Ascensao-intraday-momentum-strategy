# 📁 Polygon_Vs_Alpaca_Market_Data

This directory contains scripts to compare intraday market data for the SPY ETF from two different sources: Polygon and Alpaca.

### 🔍 compare_datasets.py
Performs a comparison between spy_intra_data_polygon.csv and spy_intra_data_alpaca.csv.
It includes:

- Total row count per dataset
- Row count per day
- Unique and shared timestamps
- OHLCV value differences on shared timestamps
- Duplicate timestamp check

### 🔄 convert_data_from_alpaca.py

#### Processes SPY_1min_adjusted_alpaca.csv exported from Alpaca and generates:

- spy_intra_data.csv: filtered intraday data (09:30 to 15:59)

- spy_daily_data.csv: daily aggregated OHLCV data

The user is prompted to input a date range for the conversion.

