import pandas as pd

# Load both files
df_polygon = pd.read_csv("spy_intra_data_polygon.csv")
df_alpaca = pd.read_csv("spy_intra_data_alpaca.csv")

# Convert 'caldt' to datetime
df_polygon['caldt'] = pd.to_datetime(df_polygon['caldt'])
df_alpaca['caldt'] = pd.to_datetime(df_alpaca['caldt'])

print("\n========== ROW COUNT ==========")
print(f"[Polygon] Total rows: {len(df_polygon)}")
print(f"[Alpaca ] Total rows: {len(df_alpaca)}")

# ========== PART 1: Row count per day ==========
polygon_counts = df_polygon['caldt'].dt.date.value_counts().sort_index()
alpaca_counts = df_alpaca['caldt'].dt.date.value_counts().sort_index()

comparison_df = pd.DataFrame({
    'polygon_count': polygon_counts,
    'alpaca_count': alpaca_counts
})
comparison_df['difference'] = comparison_df['polygon_count'] - comparison_df['alpaca_count']

print("\n========== ROW COUNT PER DAY DIFFERENCES ==========")
diff_days = comparison_df[comparison_df['difference'] != 0]
if diff_days.empty:
    print("[✓] No differences in row counts per day.")
else:
    print(diff_days)

# ========== PART 2: Unique timestamps ==========
polygon_timestamps = set(df_polygon['caldt'])
alpaca_timestamps = set(df_alpaca['caldt'])

only_in_polygon = polygon_timestamps - alpaca_timestamps
only_in_alpaca = alpaca_timestamps - polygon_timestamps
shared_timestamps = polygon_timestamps & alpaca_timestamps

print("\n========== TIMESTAMP COMPARISON ==========")
print(f"[✓] Shared timestamps: {len(shared_timestamps)}")
print(f"[!] Timestamps only in Polygon: {len(only_in_polygon)}")
print(f"[!] Timestamps only in Alpaca:  {len(only_in_alpaca)}")

# Save missing timestamps for manual review
#if only_in_polygon:
   # pd.DataFrame(sorted(only_in_polygon), columns=["missing_in_alpaca"]).to_csv("missing_in_alpaca.csv", index=False)
#if only_in_alpaca:
   #  pd.DataFrame(sorted(only_in_alpaca), columns=["missing_in_polygon"]).to_csv("missing_in_polygon.csv", index=False)

# ========== PART 3: Compare OHLCV values on shared timestamps ==========
print("\n========== OHLCV VALUE DIFFERENCES ON SHARED TIMESTAMPS ==========")
# Merge both dataframes on 'caldt'
df_shared = pd.merge(df_polygon, df_alpaca, on='caldt', suffixes=('_polygon', '_alpaca'))

# Check for differences in OHLCV columns
ohlcv_cols = ['open', 'high', 'low', 'close', 'volume']
for col in ohlcv_cols:
    diff_mask = df_shared[f'{col}_polygon'] != df_shared[f'{col}_alpaca']
    num_diffs = diff_mask.sum()
    print(f"[{col.upper()}] Differences: {num_diffs}")

# ========== PART 4: Analyze extra Alpaca timestamps ==========
if only_in_alpaca:
    df_extra_alpaca = df_alpaca[df_alpaca['caldt'].isin(only_in_alpaca)].copy()
    df_extra_alpaca['hour'] = df_extra_alpaca['caldt'].dt.hour

    #print("\n========== HOUR DISTRIBUTION OF EXTRA ALPACA TIMESTAMPS ==========")
    #print(df_extra_alpaca['hour'].value_counts().sort_index())

    # Save for review
    # df_extra_alpaca.to_csv("extra_alpaca_rows.csv", index=False)

# ========== PART 5: Check for duplicate timestamps ==========
print("\n========== DUPLICATE TIMESTAMPS CHECK ==========")
dups_polygon = df_polygon['caldt'].duplicated().sum()
dups_alpaca = df_alpaca['caldt'].duplicated().sum()
print(f"[Polygon] Duplicate timestamps: {dups_polygon}")
print(f"[Alpaca ] Duplicate timestamps: {dups_alpaca}\n\n")
