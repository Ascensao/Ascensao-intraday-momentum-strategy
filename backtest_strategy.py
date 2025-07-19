import pandas as pd
import numpy as np
import math
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from matplotlib.ticker import FuncFormatter
import statsmodels.api as sm
from datetime import datetime, timedelta, time

def minute_to_time(minute_offset):
    base = datetime.combine(datetime.today(), time(9, 30))
    return (base + timedelta(minutes=int(minute_offset))).time().strftime("%H:%M:%S")

# === Load processed data ===
df = pd.read_csv("spy_processed_data.csv", parse_dates=['day'])
spy_daily_data = pd.read_csv("spy_daily_data.csv", parse_dates=['caldt'])

# === Parameters ===
AUM_0 = 100000.0
commission = 0.0035
min_comm_per_order = 0.35
band_mult = 1
trade_freq = 30
sizing_type = "vol_target"
target_vol = 0.02
max_leverage = 4

# === Prepare data ===
df['day'] = df['day'].dt.date
spy_daily_data['caldt'] = spy_daily_data['caldt'].dt.date
spy_daily_data.set_index('caldt', inplace=True)
spy_daily_data['ret'] = spy_daily_data['close'].diff() / spy_daily_data['close'].shift()

all_days = df['day'].unique()
daily_groups = df.groupby('day')

# === Initialize strategy ===
strat = pd.DataFrame(index=all_days)
strat['ret'] = np.nan
strat['AUM'] = AUM_0
strat['ret_spy'] = np.nan
trades = []

# === Backtest loop ===
for d in range(1, len(all_days)):
    current_day = all_days[d]
    prev_day = all_days[d - 1]

    if prev_day not in daily_groups.groups or current_day not in daily_groups.groups:
        continue

    prev_day_data = daily_groups.get_group(prev_day)
    current_day_data = daily_groups.get_group(current_day)

    if current_day_data['sigma_open'].isna().all():
        continue

    prev_close = prev_day_data['close'].iloc[-1]
    dividend = current_day_data['dividend'].iloc[-1]
    prev_close_adjusted = prev_close - dividend

    open_price = current_day_data['open'].iloc[0]
    close_prices = current_day_data['close']
    spx_vol = current_day_data['spy_dvol'].iloc[0]
    vwap = current_day_data['vwap']
    sigma_open = current_day_data['sigma_open']

    # === Bands ===
    UB = np.maximum(open_price, prev_close_adjusted) * (1 + band_mult * sigma_open)
    LB = np.minimum(open_price, prev_close_adjusted) * (1 - band_mult * sigma_open)

    # === Trading Signals
    signals = np.zeros(len(current_day_data))
    signals[(close_prices > UB) & (close_prices > vwap)] = 1
    signals[(close_prices < LB) & (close_prices < vwap)] = -1

    # === Position sizing
    prev_aum = strat.loc[prev_day, 'AUM']
    if sizing_type == "vol_target":
        if math.isnan(spx_vol) or spx_vol == 0:
            shares = round(prev_aum / open_price * max_leverage)
        else:
            shares = round(prev_aum / open_price * min(target_vol / spx_vol, max_leverage))
    else:
        shares = round(prev_aum / open_price)

    # === Apply signals only at trade_freq
    trade_indices = np.where(current_day_data["min_from_open"] % trade_freq == 0)[0]
    exposure = np.full(len(current_day_data), np.nan)
    exposure[trade_indices] = signals[trade_indices]

    # === Forward fill (custom)
    last_valid = np.nan
    filled = []
    for val in exposure:
        if not np.isnan(val):
            last_valid = val
        if last_valid == 0:
            last_valid = np.nan
        filled.append(last_valid)
    exposure = pd.Series(filled, index=current_day_data.index).shift(1).fillna(0)

    # === Track trades
    current_position = 0
    entry_price = None
    i_entry = None

    for i in range(len(current_day_data)):
        price = close_prices.iloc[i]
        signal = exposure.iloc[i]

        if current_position == 0 and signal != 0:
            current_position = signal
            entry_price = price
            i_entry = i

        elif current_position != 0 and signal != current_position:
            exit_price = price
            pnl = (exit_price - entry_price) * shares * current_position
            pnl_pct = (exit_price / entry_price - 1) * 100 * current_position
            account_balance = prev_aum + pnl

            # === Exit reason detalhado
            sig_now = signals[i]
            price_now = close_prices.iloc[i]
            vwap_now = vwap.iloc[i]
            ub_now = UB.iloc[i]
            lb_now = LB.iloc[i]

            if sig_now == 1:
                if price_now > ub_now and price_now > vwap_now:
                    exit_reason = "signal_change_ub_vwap"
                elif price_now > ub_now:
                    exit_reason = "signal_change_ub"
                elif price_now > vwap_now:
                    exit_reason = "signal_change_vwap"
                else:
                    raise ValueError(f"[ERROR] Unclassified signal_change (long) on {current_day} @ {i}")
            elif sig_now == -1:
                if price_now < lb_now and price_now < vwap_now:
                    exit_reason = "signal_change_lb_vwap"
                elif price_now < lb_now:
                    exit_reason = "signal_change_lb"
                elif price_now < vwap_now:
                    exit_reason = "signal_change_vwap"
                else:
                    raise ValueError(f"[ERROR] Unclassified signal_change (short) on {current_day} @ {i}")
            else:
                exit_reason = "signal_change_no_new_signal"

            side = "long" if current_position == 1 else "short"

            trades.append({
                "Date": current_day,
                "Open_Time": minute_to_time(current_day_data["min_from_open"].iloc[i_entry]),
                "Open_Price": round(entry_price, 2),
                "Exit_Time": minute_to_time(current_day_data["min_from_open"].iloc[i]),
                "Exit_Price": round(exit_price, 2),
                "Shares": shares * current_position,
                "Profit%": round(pnl_pct, 2),
                "P&L": round(pnl, 2),
                "Account_Balance": round(account_balance, 2),
                "Side": side,
                "exit_reason": exit_reason
            })

            current_position = 0

    # === Force exit at end of day
    if current_position != 0 and entry_price is not None:
        exit_price = close_prices.iloc[-1]
        pnl = (exit_price - entry_price) * shares * current_position
        pnl_pct = (exit_price / entry_price - 1) * 100 * current_position
        account_balance = prev_aum + pnl
        side = "long" if current_position == 1 else "short"

        trades.append({
            "Date": current_day,
            "Open_Time": minute_to_time(current_day_data["min_from_open"].iloc[i_entry]),
            "Open_Price": round(entry_price, 2),
            "Exit_Time": "16:00:00",
            "Exit_Price": round(exit_price, 2),
            "Shares": shares * current_position,
            "Profit%": round(pnl_pct, 2),
            "P&L": round(pnl, 2),
            "Account_Balance": round(account_balance, 2),
            "Side": side,
            "exit_reason": "end_of_day"
        })

    # === PnL
    trades_count = np.sum(np.abs(np.diff(np.append(exposure.values, 0))))
    gross_pnl = np.sum(exposure.values * close_prices.diff().fillna(0).values) * shares
    commission_paid = trades_count * max(min_comm_per_order, commission * shares)
    net_pnl = gross_pnl - commission_paid

    # === Update strategy dataframe
    strat.loc[current_day, 'AUM'] = prev_aum + net_pnl
    strat.loc[current_day, 'ret'] = net_pnl / prev_aum
    strat.loc[current_day, 'ret_spy'] = spy_daily_data.loc[current_day, 'ret'] if current_day in spy_daily_data.index else np.nan

# === Save trades
trades_df = pd.DataFrame(trades)
trades_df.to_csv("trades.csv", index=False)
print("[INFO] trades.csv gerado com", len(trades_df), "registos.")

# === Performance stats
strat['AUM_SPX'] = AUM_0 * (1 + strat['ret_spy']).cumprod(skipna=True)

fig, ax = plt.subplots()
ax.plot(strat.index, strat['AUM'], label='Momentum Strategy', linewidth=2, color='k')
ax.plot(strat.index, strat['AUM_SPX'], label='S&P 500 (Buy & Hold)', linewidth=1, color='r')

ax.grid(True, linestyle=':')
ax.xaxis.set_major_locator(mdates.MonthLocator())
ax.xaxis.set_major_formatter(mdates.DateFormatter('%b %y'))
plt.xticks(rotation=90)
ax.yaxis.set_major_formatter(FuncFormatter(lambda x, _: f'${x:,.0f}'))
ax.set_ylabel('AUM ($)')
plt.legend(loc='upper left')
plt.title('Intraday Momentum Strategy vs. S&P 500')
plt.suptitle(f'Commission = ${commission}/share', fontsize=9)
plt.show()

# === Regression stats
Y = strat['ret'].dropna()
X = sm.add_constant(strat['ret_spy'].dropna())
model = sm.OLS(Y, X.loc[Y.index]).fit()

stats = {
    'Total Return (%)': round((np.prod(1 + Y) - 1) * 100, 1),
    'Annualized Return (%)': round((np.prod(1 + Y) ** (252 / len(Y)) - 1) * 100, 1),
    'Annualized Volatility (%)': round(Y.std() * np.sqrt(252) * 100, 1),
    'Sharpe Ratio': round(Y.mean() / Y.std() * np.sqrt(252), 2),
    'Hit Ratio (%)': round((Y > 0).sum() / (Y.abs() > 0).sum() * 100, 1),
    'Max Drawdown (%)': round(strat['AUM'].div(strat['AUM'].cummax()).sub(1).min() * -100, 1),
    'Alpha (%)': round(model.params['const'] * 100 * 252, 2),
    'Beta': round(model.params['ret_spy'], 2)
}

print("\n=== Strategy Performance Metrics ===")
for k, v in stats.items():
    print(f"{k}: {v}")
