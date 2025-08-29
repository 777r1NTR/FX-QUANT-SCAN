import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta, timezone
from pathlib import Path
import os

# === CONFIG ===
TICKER_LIST = [
    'GBPNZD=X', 'EURCHF=X', 'NZDCAD=X', 'USDZAR=X', 'CADCHF=X',
    'GBPJPY=X', 'AUDNZD=X', 'GBPCHF=X', 'USDCAD=X', 'CADJPY=X',
    'AUDJPY=X', 'EURUSD=X', 'EURGBP=X', 'USDNOK=X', 'NOKSEK=X'
]
KEY_LEVELS_FILE = Path("C:/Users/T460/Documents/Quant_trading_research/key_levels_x_3/Key_levels_1D.xlsx")
PIP_RANGE = 0.001
ZONE_DEFINITIONS = [
    ("Premium+", float("inf"), "Purple upper"),
    ("Premium", "Purple upper", "Red  Upper"),
    ("Plus+", "Red  Upper", "Yellow Upper"),
    ("Fair", "Yellow Upper", "Green"),
    ("Budget", "Green", "Yellow Lower"),
    ("Discount", "Yellow Lower", "Red Lower"),
    ("Clearance", "Red Lower", "Purple lower"),
    ("Reset", "Purple lower", float("-inf"))
]

# === Utility Functions ===
def load_key_levels(filepath):
    df = pd.read_excel(filepath)
    df.set_index("Ticker", inplace=True)
    return df

def check_proximity(level_dict, high, low):
    matches = []
    for level_name, level_value in level_dict.items():
        if pd.isna(level_value):
            continue
        if (low <= level_value + PIP_RANGE) and (high >= level_value - PIP_RANGE):
            matches.append({"Level": round(level_value, 5), "Level Name": level_name})
    return matches

def compute_current_zone(price, zone_definitions, level_dict):
    levels = {}
    for _, a, b in zone_definitions:
        if isinstance(a, str):
            levels[a] = level_dict.get(a, None)
        if isinstance(b, str):
            levels[b] = level_dict.get(b, None)
    levels["Purple upper"] = level_dict.get("Purple upper", float("inf"))
    levels["Purple lower"] = level_dict.get("Purple lower", float("-inf"))

    for zone_name, upper_bound, lower_bound in zone_definitions:
        upper_value = levels.get(upper_bound, float("inf")) if isinstance(upper_bound, str) else upper_bound
        lower_value = levels.get(lower_bound, float("-inf")) if isinstance(lower_bound, str) else lower_bound
        if lower_value < price <= upper_value:
            return zone_name
    return "Unknown"

# === Main Zone Transition Logic ===
def get_zone_transitions_today():
    if datetime.now().weekday() >= 5:
        print("⏸ Weekend detected — skipping transition scan")
        return pd.DataFrame()

    since = datetime.now(timezone.utc) - timedelta(hours=24)
    key_levels_df = load_key_levels(KEY_LEVELS_FILE)
    transitions = []

    for ticker in TICKER_LIST:
        print(f"[→] Checking {ticker}...")
        try:
            data = yf.download(ticker, start=since.strftime('%Y-%m-%d'), interval="1h", progress=False)
            if data.empty:
                print(f"[⚠️] No data for {ticker} — skipping")
                continue
            data = data.dropna()

            short = ticker.split("=")[0] + "=X" if "=X" in ticker else ticker
            levels_series = key_levels_df.loc[short].dropna()
            level_dict = dict(levels_series)

            previous_zone = None
            for ts, row in data.iterrows():
                price = row['Close'].item()
                zone = compute_current_zone(price, ZONE_DEFINITIONS, level_dict)
                if previous_zone is not None and zone != previous_zone:
                    transitions.append({
                        "Timestamp": ts,
                        "Ticker": ticker,
                        "From Zone": previous_zone,
                        "To Zone": zone,
                        "Price": price
                    })
                previous_zone = zone

        except Exception as e:
            print(f"[❌] Failed for {ticker}: {e}")

    df_transitions = pd.DataFrame(transitions)
    if not df_transitions.empty:
        os.makedirs("reports", exist_ok=True)
        log_file = "reports/zone_transition_log.csv"
        
        # Handle existing file with potentially different column names
        if os.path.exists(log_file):
            try:
                # Read existing file to check its structure
                existing_df = pd.read_csv(log_file)
                
                # If existing file has 'Date' instead of 'Timestamp', rename it
                if 'Date' in existing_df.columns and 'Timestamp' not in existing_df.columns:
                    existing_df = existing_df.rename(columns={'Date': 'Timestamp'})
                    # Rewrite the file with standardized column names
                    existing_df.to_csv(log_file, index=False)
                    print("[🔄] Standardized existing CSV column names")
                
                # Now append the new data
                df_transitions.to_csv(log_file, mode="a", index=False, header=False)
                
            except Exception as e:
                print(f"[⚠️] Issue with existing file, creating backup: {e}")
                # Create backup and start fresh
                backup_file = log_file.replace('.csv', '_backup.csv')
                if os.path.exists(log_file):
                    os.rename(log_file, backup_file)
                df_transitions.to_csv(log_file, index=False)
        else:
            # New file
            df_transitions.to_csv(log_file, index=False)
            
        print(f"[💾] Zone transitions saved to: {log_file}")
    else:
        print("[✅] No zone transitions detected today.")

    return df_transitions

if __name__ == "__main__":
    get_zone_transitions_today()
