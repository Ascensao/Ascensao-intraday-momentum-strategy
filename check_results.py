import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from matplotlib.ticker import FuncFormatter
import statsmodels.api as sm

# === Load data ===
trades = pd.read_csv("trades.csv", parse_dates=["Date"])
spy = pd.read_csv("spy_intra_data.csv", parse_dates=["caldt"])

# === Process SPY data ===
spy['date'] = spy['caldt'].dt.date
spy_daily = spy.groupby('date').agg({'close': 'last'})
spy_daily['ret'] = spy_daily['close'].pct_change()
spy_daily = spy_daily.dropna()

# === Process strategy data ===
trades.sort_values("Date", inplace=True)
daily_balance = trades.groupby("Date").agg({'Account_Balance': 'last'})
daily_balance['ret'] = daily_balance['Account_Balance'].pct_change()
daily_balance = daily_balance.dropna()

# === Align time series ===
combined = pd.merge(daily_balance[['ret']], spy_daily[['ret']], left_index=True, right_index=True, suffixes=('_strategy', '_spy'))

# === Compute performance metrics ===
Y = combined['ret_strategy']
X = sm.add_constant(combined['ret_spy'])
model = sm.OLS(Y, X).fit()

# === Extra metrics: Win Rate & Profit Factor ===
positive_returns = Y[Y > 0]
negative_returns = Y[Y < 0]
win_rate = round(len(positive_returns) / len(Y) * 100, 1)
profit_factor = round(positive_returns.sum() / abs(negative_returns.sum()), 2) if len(negative_returns) > 0 else np.nan

# === Max Drawdown and period ===
cum_balance = daily_balance['Account_Balance']
roll_max = cum_balance.cummax()
drawdown = cum_balance / roll_max - 1
min_drawdown_idx = drawdown.idxmin()
max_dd_pct = round(drawdown.min() * -100, 1)
peak_date = roll_max[:min_drawdown_idx].idxmax()
valley_date = min_drawdown_idx

# === Store performance statistics ===
stats = {
    'Total Return (%)': round((np.prod(1 + Y) - 1) * 100, 1),
    'Annualized Return (%)': round((np.prod(1 + Y) ** (252 / len(Y)) - 1) * 100, 1),
    'Annualized Volatility (%)': round(Y.std() * np.sqrt(252) * 100, 1),
    'Sharpe Ratio': round(Y.mean() / Y.std() * np.sqrt(252), 2),
    'Win Rate (%)': win_rate,
    'Profit Factor': profit_factor,
    'Max Drawdown (%)': f"{max_dd_pct} ({peak_date.date()} → {valley_date.date()})",
    'Alpha (%)': round(model.params['const'] * 100 * 252, 2),
    'Beta': round(model.params['ret_spy'], 2)
}

# === Calculate AUM for Buy & Hold ===
initial_balance = trades['Account_Balance'].iloc[0]
spy_daily['AUM_SPY'] = initial_balance * (1 + spy_daily['ret']).cumprod()
daily_balance['AUM_Strategy'] = daily_balance['Account_Balance']

# === Merge for plot ===
aum_compare = pd.merge(daily_balance[['AUM_Strategy']], spy_daily[['AUM_SPY']], left_index=True, right_index=True)

# === Plot AUM comparison ===
fig, ax = plt.subplots()
ax.plot(aum_compare.index, aum_compare['AUM_Strategy'], label='Momentum Strategy', linewidth=2, color='k')
ax.plot(aum_compare.index, aum_compare['AUM_SPY'], label='S&P 500 (Buy & Hold)', linewidth=1, color='r')

ax.grid(True, linestyle=':')
ax.xaxis.set_major_locator(mdates.YearLocator())
ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y'))
plt.xticks(rotation=45)
ax.yaxis.set_major_formatter(FuncFormatter(lambda x, _: f'${x:,.0f}'))
ax.set_ylabel('Account Balance ($)')
plt.legend(loc='upper left')
plt.title('Strategy vs. Buy & Hold')
plt.tight_layout()
plt.show()

# === Display performance metrics ===
print("\n=== Strategy Performance Metrics ===")
for k, v in stats.items():
    print(f"{k}: {v}")

# === Long/Short Trade Stats ===
trades['P&L'] = pd.to_numeric(trades['P&L'], errors='coerce')
trades['Side'] = trades['Side'].str.lower()

long_trades = trades[trades['Side'] == 'long']
short_trades = trades[trades['Side'] == 'short']

long_count = len(long_trades)
short_count = len(short_trades)

long_profit = long_trades['P&L'].sum()
short_profit = short_trades['P&L'].sum()

print("\n=== Long/Short Breakdown ===")
print(f"Number of long trades: {long_count}")
print(f"Number of short trades: {short_count}")
print(f"Total profit from longs: ${long_profit:,.2f}")
print(f"Total profit from shorts: ${short_profit:,.2f}")

# === Monthly and Yearly Returns Table ===
trades["Year"] = trades["Date"].dt.year
trades["Month"] = trades["Date"].dt.month
trades["Daily_Return"] = trades["Account_Balance"].pct_change() * 100

monthly_returns = (
    trades.groupby(["Year", "Month"])["Account_Balance"]
    .agg(["first", "last"])
    .assign(Monthly_Return=lambda x: (x["last"] / x["first"] - 1) * 100)
)

monthly_table = monthly_returns["Monthly_Return"].unstack(level=1).round(1)
yearly_returns = (
    trades.groupby("Year")["Account_Balance"]
    .agg(["first", "last"])
    .assign(Yearly_Return=lambda x: (x["last"] / x["first"] - 1) * 100)
)

monthly_table = monthly_table.reindex(columns=range(1, 13)).round(1)
monthly_table.columns = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", 
                         "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
monthly_table["Yearly"] = yearly_returns["Yearly_Return"].round(1)

# === Display monthly and yearly return table ===
print("\n=====     Monthly & Yearly Returns Table     =====\n")
print(monthly_table)
print("\n\n")
# monthly_table.to_csv("monthly_returns.csv")
