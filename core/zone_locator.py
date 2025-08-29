import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta, timezone
from pathlib import Path
from collections import defaultdict
import pytz
import smtplib
import os
import json

from pathlib import Path
BASE_DIR = Path(__file__).resolve().parents[1]  # adjust as needed
DATA_DIR = BASE_DIR / "data"
REPORTS_DIR = BASE_DIR / "reports"
REPORTS_DIR.mkdir(exist_ok=True)

# === CONFIG ===
ZONE_STATE_FILE = REPORTS_DIR / "last_known_zone.json"
KEY_LEVELS_FILE = DATA_DIR / "Key_levels_1D.xlsx"  
TICKER_LIST = [
    'GBPNZD=X', 'EURCHF=X', 'NZDCAD=X', 'USDZAR=X', 'CADCHF=X',
    'GBPJPY=X', 'AUDNZD=X', 'GBPCHF=X', 'USDCAD=X', 'CADJPY=X',
    'AUDJPY=X', 'EURUSD=X', 'EURGBP=X', 'USDNOK=X', 'NOKSEK=X'
]
PIP_RANGE = 0.001
LOOKBACK_HOURS = 24
since = datetime.now(timezone.utc) - timedelta(hours=LOOKBACK_HOURS)

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

if os.path.exists(ZONE_STATE_FILE):
    with open(ZONE_STATE_FILE, "r") as f:
        last_known_zone = json.load(f)
else:
    last_known_zone = {}

def load_key_levels(filepath):
    df = pd.read_excel(filepath)
    df.set_index("Ticker", inplace=True)
    return df

def compute_current_zone(price, zone_definitions, level_dict):
    levels = {}
    for _, upper_bound, lower_bound in zone_definitions:
        if isinstance(upper_bound, str):
            levels[upper_bound] = float(level_dict.get(upper_bound, float("inf")))
        if isinstance(lower_bound, str):
            levels[lower_bound] = float(level_dict.get(lower_bound, float("-inf")))

    levels["Purple upper"] = float(level_dict.get("Purple upper", float("inf")))
    levels["Purple lower"] = float(level_dict.get("Purple lower", float("-inf")))

    for zone_name, upper_bound, lower_bound in zone_definitions:
        upper_value = levels.get(upper_bound, float("inf")) if isinstance(upper_bound, str) else upper_bound
        lower_value = levels.get(lower_bound, float("-inf")) if isinstance(lower_bound, str) else lower_bound
        if lower_value < price <= upper_value:
            return zone_name
    return "Unknown"

def generate_current_zone_snapshot():
    key_levels_df = load_key_levels(KEY_LEVELS_FILE)
    current_zone_results = []

    for ticker in TICKER_LIST:
        print(f"[→] Checking {ticker} current zone...")
        try:
            data = yf.download(ticker, period="1d", interval="1h", progress=False)
            if data.empty:
                print(f"[⚠️] No data for {ticker}")
                continue

            latest_close = data["Close"].iloc[-1].item()
            short = ticker.split("=")[0] + "=X" if "=X" in ticker else ticker
            levels_series = key_levels_df.loc[short].dropna()
            level_dict = {k: float(v) for k, v in levels_series.items()}
            zone = compute_current_zone(latest_close, ZONE_DEFINITIONS, level_dict)

            history_row = {
                "Date": pd.Timestamp.utcnow().strftime("%Y-%m-%d"),
                "Ticker": ticker,
                "Zone": zone
            }
            history_file = "reports/zone_history.csv"
            pd.DataFrame([history_row]).to_csv(history_file, mode="a", index=False, header=not os.path.exists(history_file))

            previous_zone = last_known_zone.get(ticker, None)
            if previous_zone != zone and previous_zone is not None:
                transition_row = {
                    "Date": pd.Timestamp.utcnow().strftime("%Y-%m-%d %H:%M:%S"),
                    "Ticker": ticker,
                    "From Zone": previous_zone,
                    "To Zone": zone
                }
                transition_file = "reports/zone_transition_log.csv"
                pd.DataFrame([transition_row]).to_csv(transition_file, mode="a", index=False, header=not os.path.exists(transition_file))
            last_known_zone[ticker] = zone

            print(f"[✓] {ticker} → Zone: {zone} (Price: {latest_close:.4f})")
            current_zone_results.append({
                "Ticker": ticker,
                "Current Zone": zone,
                "Current Price": latest_close
            })
        except Exception as e:
            print(f"[❌] Failed for {ticker}: {e}")

    with open(ZONE_STATE_FILE, "w") as f:
        json.dump(last_known_zone, f)

    df_current_zones = pd.DataFrame(current_zone_results).sort_values(by="Current Zone")
    print("[✅] Current Zone Snapshot:\n")
    print(df_current_zones.to_string(index=False))

    os.makedirs("reports", exist_ok=True)
    outpath = "reports/current_zone_snapshot.xlsx"
    df_current_zones.to_excel(outpath, index=False)
    print(f"[💾] Exported current zone snapshot to: {outpath}")
    return df_current_zones

def export_current_zone_heatmap(df_current_zones, output_path="reports/current_zone_snapshot_heatmap.xlsx"):
    if df_current_zones.empty:
        print("[⚠️] No current zones to export.")
        return

    print("[🎨] Exporting color heatmap version...")
    with pd.ExcelWriter(output_path, engine="xlsxwriter") as writer:
        df_current_zones.to_excel(writer, sheet_name="Current Zones", index=False)
        workbook = writer.book
        worksheet = writer.sheets["Current Zones"]

        format_premium_plus = workbook.add_format({"bg_color": "#DA70D6"})  # Purple-Gold
        format_premium = workbook.add_format({"bg_color": "#FFD700", "bold": True})  # Gold
        format_plus = workbook.add_format({"bg_color": "#FFA500"})  # Orange
        format_fair = workbook.add_format({"bg_color": "#90EE90"})  # LightGreen
        format_budget = workbook.add_format({"bg_color": "#ADD8E6"})  # LightBlue
        format_discount = workbook.add_format({"bg_color": "#FF9999"})  # LightRed
        format_clearance = workbook.add_format({"bg_color": "#FF5555"})  # Deep Red
        format_reset = workbook.add_format({"bg_color": "#A9A9A9"})  # Gray


        zone_col = df_current_zones.columns.get_loc("Current Zone")
        zone_range = f"${chr(65 + zone_col)}2:${chr(65 + zone_col)}{len(df_current_zones)+1}"

        worksheet.conditional_format(zone_range, {"type": "text", "criteria": "containing", "value": "Premium+", "format": format_premium_plus})
        worksheet.conditional_format(zone_range, {"type": "text", "criteria": "containing", "value": "Premium", "format": format_premium})
        worksheet.conditional_format(zone_range, {"type": "text", "criteria": "containing", "value": "Plus+", "format": format_plus})
        worksheet.conditional_format(zone_range, {"type": "text", "criteria": "containing", "value": "Fair", "format": format_fair})
        worksheet.conditional_format(zone_range, {"type": "text", "criteria": "containing", "value": "Budget", "format": format_budget})
        worksheet.conditional_format(zone_range, {"type": "text", "criteria": "containing", "value": "Discount", "format": format_discount})
        worksheet.conditional_format(zone_range, {"type": "text", "criteria": "containing", "value": "Clearance", "format": format_clearance})
        worksheet.conditional_format(zone_range, {"type": "text", "criteria": "containing", "value": "Reset", "format": format_reset})

    print(f"[💾] Exported color heatmap to: {output_path}")

if __name__ == "__main__":
    df_current_zones = generate_current_zone_snapshot()
    export_current_zone_heatmap(df_current_zones)

  