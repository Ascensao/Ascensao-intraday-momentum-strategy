import requests
import time
import pandas as pd
from datetime import datetime
import pytz

# ===== CONFIGURATION =====
API_KEY = 'YOUR_API'  # Replace with your actual Polygon.io API key
BASE_URL = 'https://api.polygon.io'
ENFORCE_RATE_LIMIT = True
eastern = pytz.timezone('America/New_York')

# ===== FUNCTIONS =====

def fetch_polygon_data(ticker, start_date, end_date, period, enforce_rate_limit=ENFORCE_RATE_LIMIT):
    """Fetch stock data from Polygon.io based on the given period (minute or day)."""
    multiplier = '1'
    timespan = period
    limit = '50000'

    url = f'{BASE_URL}/v2/aggs/ticker/{ticker}/range/{multiplier}/{timespan}/{start_date}/{end_date}?adjusted=false&sort=asc&limit={limit}&apiKey={API_KEY}'
    
    data_list = []
    request_count = 0
    first_request_time = None

    while True:
        if enforce_rate_limit and request_count == 5:
            elapsed_time = time.time() - first_request_time
            if elapsed_time < 60:
                wait_time = 60 - elapsed_time
                print(f"[INFO] Rate limit reached. Waiting {wait_time:.2f} seconds...")
                time.sleep(wait_time)
            request_count = 0
            first_request_time = time.time()

        if first_request_time is None and enforce_rate_limit:
            first_request_time = time.time()

        response = requests.get(url)
        if response.status_code != 200:
            error_message = response.json().get('error', 'No error message provided.')
            print(f"[ERROR] API response error: {error_message}")
            break

        data = response.json()
        request_count += 1
        print(f"[INFO] Fetched {len(data.get('results', []))} entries.")

        if 'results' in data:
            for entry in data['results']:
                utc_time = datetime.fromtimestamp(entry['t'] / 1000, pytz.utc)
                eastern_time = utc_time.astimezone(eastern)

                data_entry = {
                    'caldt': eastern_time.replace(tzinfo=None),
                    'open': entry['o'],
                    'high': entry['h'],
                    'low': entry['l'],
                    'close': entry['c'],
                    'volume': entry['v'],
                }

                if period == 'minute':
                    if eastern_time.time() >= datetime.strptime('09:30', '%H:%M').time() and eastern_time.time() <= datetime.strptime('15:59', '%H:%M').time():
                        data_list.append(data_entry)
                else:
                    data_list.append(data_entry)

        if 'next_url' in data and data['next_url']:
            url = data['next_url'] + '&apiKey=' + API_KEY
        else:
            break

    df = pd.DataFrame(data_list)
    print("[INFO] Data fetching complete.")
    return df


def fetch_polygon_dividends(ticker):
    """Fetches dividend data from Polygon.io."""
    url = f'{BASE_URL}/v3/reference/dividends?ticker={ticker}&limit=1000&apiKey={API_KEY}'
    
    dividends_list = []
    while True:
        response = requests.get(url)
        data = response.json()
        if 'results' in data:
            for entry in data['results']:
                dividends_list.append({
                    'caldt': datetime.strptime(entry['ex_dividend_date'], '%Y-%m-%d'),
                    'dividend': entry['cash_amount']
                })

        if 'next_url' in data and data['next_url']:
            url = data['next_url'] + '&apiKey=' + API_KEY
        else:
            break

    df = pd.DataFrame(dividends_list)
    print("[INFO] Dividend data fetching complete.")
    return df

# ===== EXECUTION =====

if __name__ == "__main__":
    ticker = 'SPY'
    from_date = '2016-01-02'
    until_date = '2025-07-14'

    spy_intra_data = fetch_polygon_data(ticker, from_date, until_date, 'minute')
    spy_daily_data = fetch_polygon_data(ticker, from_date, until_date, 'day')
    dividends = fetch_polygon_dividends(ticker)

    # ===== SAVE DATA TO CSV =====
    spy_intra_data.to_csv('spy_intra_data.csv', index=False)
    spy_daily_data.to_csv('spy_daily_data.csv', index=False)
    dividends.to_csv('spy_dividends.csv', index=False)

    print("[INFO] All data has been saved successfully.")
