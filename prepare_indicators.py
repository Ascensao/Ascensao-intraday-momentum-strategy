import pandas as pd
import numpy as np

# Carregar os dados exportados anteriormente
spy_intra_data = pd.read_csv("spy_intra_data.csv", parse_dates=["caldt"])
dividends = pd.read_csv("spy_dividends.csv", parse_dates=["caldt"])

# === Etapa 1: Preparar DataFrame ===
df = spy_intra_data.copy()
df['day'] = pd.to_datetime(df['caldt']).dt.date
df.set_index('caldt', inplace=True)

# === Etapa 2: Agrupamento diário ===
daily_groups = df.groupby('day')
all_days = df['day'].unique()

# Inicialização
df['move_open'] = np.nan
df['vwap'] = np.nan
df['spy_dvol'] = np.nan
spy_ret = pd.Series(index=all_days, dtype=float)

# === Etapa 3: Métricas por dia ===
for d in range(1, len(all_days)):
    current_day = all_days[d]
    prev_day = all_days[d - 1]
    
    current_day_data = daily_groups.get_group(current_day)
    prev_day_data = daily_groups.get_group(prev_day)

    hlc = (current_day_data['high'] + current_day_data['low'] + current_day_data['close']) / 3
    vol_x_hlc = current_day_data['volume'] * hlc
    cum_vol_x_hlc = vol_x_hlc.cumsum()
    cum_volume = current_day_data['volume'].cumsum()

    df.loc[current_day_data.index, 'vwap'] = cum_vol_x_hlc / cum_volume

    open_price = current_day_data['open'].iloc[0]
    df.loc[current_day_data.index, 'move_open'] = (current_day_data['close'] / open_price - 1).abs()

    spy_ret.loc[current_day] = current_day_data['close'].iloc[-1] / prev_day_data['close'].iloc[-1] - 1

    if d > 14:
        df.loc[current_day_data.index, 'spy_dvol'] = spy_ret.iloc[d - 15:d - 1].std(skipna=False)

# === Etapa 4: Métricas por minuto ===
df['min_from_open'] = ((df.index - df.index.normalize()) / pd.Timedelta(minutes=1)) - (9 * 60 + 30) + 1
df['minute_of_day'] = df['min_from_open'].round().astype(int)

minute_groups = df.groupby('minute_of_day')
df['move_open_rolling_mean'] = minute_groups['move_open'].transform(lambda x: x.rolling(window=14, min_periods=13).mean())
df['sigma_open'] = minute_groups['move_open_rolling_mean'].transform(lambda x: x.shift(1))

# === Etapa 5: Mesclar dividendos ===
dividends['day'] = pd.to_datetime(dividends['caldt']).dt.date
df = df.merge(dividends[['day', 'dividend']], on='day', how='left')
df['dividend'] = df['dividend'].fillna(0)

# === Salvar resultado ===
df.to_csv("spy_processed_data.csv")

print("[INFO] Calculated indicators and data saved in 'spy_processed_data.csv'")
