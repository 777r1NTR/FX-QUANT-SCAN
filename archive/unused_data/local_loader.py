# data/local_loader.py

import pandas as pd # data/local_loader.py

import pandas as pd
import os

CSV_FOLDER = r"C:\Users\T460\Documents\Quant_trading_research\Quant_framework\data\csv_data"

def load_local_csv(ticker, start_date=None, end_date=None):
    try:
        filepath = os.path.join(CSV_FOLDER, f"{ticker}.csv")
        print(f"[📄] Loading CSV: {filepath}")

        df = pd.read_csv(filepath, parse_dates=['Date'], decimal=',')

        df.columns = df.columns.str.strip()
        df['Date'] = pd.to_datetime(df['Date'], errors='coerce')
        df.dropna(subset=['Date'], inplace=True)
        df.set_index('Date', inplace=True)

        for col in ['Open', 'High', 'Low', 'Close']:
            df[col] = df[col].astype(str).str.replace(',', '.').astype(float)

        print(f"[📥] Loaded {ticker}: full range {df.index.min()} to {df.index.max()}")

        if start_date and end_date:
            print(f"[📆] Filtering from {start_date} to {end_date}")
            df = df.loc[start_date:end_date]
            print(f"[✅] After filter: {df.shape[0]} rows")

        return df

    except Exception as e:
        print(f"[❌] Failed to load {ticker}.csv: {e}")
        return pd.DataFrame()
