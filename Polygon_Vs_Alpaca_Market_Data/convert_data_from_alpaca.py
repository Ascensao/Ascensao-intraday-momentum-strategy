import pandas as pd
from datetime import datetime

# Ask the user for the date range
start_date_str = input("Enter the start date (YYYY-MM-DD): ")
end_date_str = input("Enter the end date (YYYY-MM-DD): ")

# Convert strings to datetime
start_date = pd.to_datetime(start_date_str)
end_date = pd.to_datetime(end_date_str + ' 23:59:59')  # include the entire end day

# Load the original CSV data
df = pd.read_csv("SPY_1min_adjusted_alpaca.csv")

# Combine 'date' and 'time' into a single datetime column
df['datetime'] = pd.to_datetime(df['date'] + ' ' + df['time'])

# Reorder and rename columns as needed
df = df[['datetime', 'open', 'high', 'low', 'close', 'volume']].copy()
df.rename(columns={'datetime': 'caldt'}, inplace=True)

# Filter the selected date range (inclusive)
df = df[(df['caldt'] >= start_date) & (df['caldt'] <= end_date)]

# ========== CREATE spy_intra_data_2.csv ==========
# Filter only between 09:30 and 15:59
df_intra = df[
    (df['caldt'].dt.time >= datetime.strptime("09:30", "%H:%M").time()) &
    (df['caldt'].dt.time <= datetime.strptime("15:59", "%H:%M").time())
].copy()

df_intra.to_csv("spy_intra_data.csv", index=False)
print("[INFO] File spy_intra_data.csv saved successfully.")

# ========== CREATE spy_daily_data_2.csv ==========
# Create a column with just the date
df['date'] = df['caldt'].dt.date

# Aggregate by date
df_daily = df.groupby('date').agg({
    'open': 'first',
    'high': 'max',
    'low': 'min',
    'close': 'last',
    'volume': 'sum'
}).reset_index()

df_daily.rename(columns={'date': 'caldt'}, inplace=True)

df_daily.to_csv("spy_daily_data.csv", index=False)
print("[INFO] File spy_daily_data.csv saved successfully.")
