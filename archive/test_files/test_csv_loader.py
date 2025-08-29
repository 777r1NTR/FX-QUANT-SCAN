import pandas as pd
import os

# Path to your CSVs
CSV_FOLDER = r"C:\Users\T460\Documents\Quant_trading_research\Quant_framework\data\csv_data"
TICKER = "CADCHF=X"
START_DATE = "2025-06-01"
END_DATE = "2025-06-15"

filepath = os.path.join(CSV_FOLDER, f"{TICKER}.csv")
print(f"[📄] Loading file: {filepath}")

try:
    df = pd.read_csv(filepath)
    print("[🔍] Raw columns:", df.columns.tolist())
    print("[🧪] First raw Date values:", df['Date'].head(5).tolist())


    # Clean column names
    df.columns = df.columns.str.strip().str.replace('\ufeff', '')

    # Parse datetime from MM/DD/YYYY HH:MM format
    df['Date'] = pd.to_datetime(df['Date'], format="%m/%d/%Y %H:%M", errors='raise')
    df.dropna(subset=['Date'], inplace=True)
    df.set_index('Date', inplace=True)

    print("[📅] Index preview:", df.index.min(), "→", df.index.max())

    # Fix comma decimal and cast price columns
    for col in ['Open', 'High', 'Low', 'Close']:
        df[col] = df[col].astype(str).str.replace(',', '.').astype(float)

    # Apply date filter
    df_filtered = df.loc[START_DATE:END_DATE]
    print("[✅] Filtered rows:", df_filtered.shape[0])
    print(df_filtered.head())

except Exception as e:
    print("[⚠️] Strict format failed, falling back to auto detection.")
    df['Date'] = pd.to_datetime(df['Date'], errors='coerce')
