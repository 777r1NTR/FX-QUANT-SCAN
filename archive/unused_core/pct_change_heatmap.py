import yfinance as yf
import pandas as pd
import numpy as np
import os
from datetime import datetime, timezone

# === CONFIG ===
EXPORT_TO_EXCEL = True
OUTPUT_FILE = "reports/fx_major_heatmap.xlsx"
CURRENCY_LIST = ['USD','CAD', 'EUR', 'GBP', 'CHF', 'NOK', 'SGD','JPY', 'AUD', 'NZD']
TODAY_DATE = datetime.now(timezone.utc).strftime('%Y-%m-%d')

# === Initialize matrix ===
def get_daily_pct_change(ticker):
    try:
        data = yf.download(ticker, period="2d", interval="1d", progress=False, auto_adjust=False)
        if len(data) < 2:
            return None
        open_val = data['Open'].iloc[-1].item()
        close_val = data['Close'].iloc[-1].item()
        return (close_val - open_val) / open_val * 100
    except Exception as e:
        print(f"[⚠️] Error fetching {ticker}: {e}")
        return None

def generate_fx_change_heatmap():
    matrix = pd.DataFrame(index=CURRENCY_LIST, columns=CURRENCY_LIST, dtype=float)
    for base in CURRENCY_LIST:
        for quote in CURRENCY_LIST:
            if base == quote:
                matrix.at[base, quote] = np.nan
                continue
            pair = f"{base}{quote}=X"
            pct_change = get_daily_pct_change(pair)
            if pct_change is not None:
                matrix.at[base, quote] = round(pct_change, 2)

    print(f"[📊] FX % Change Heatmap for {TODAY_DATE}")
    print(matrix)

    if EXPORT_TO_EXCEL:
        os.makedirs("reports", exist_ok=True)
        with pd.ExcelWriter(OUTPUT_FILE, engine='xlsxwriter') as writer:
            matrix.to_excel(writer, sheet_name='Heatmap')
            workbook  = writer.book
            worksheet = writer.sheets['Heatmap']
            fmt = workbook.add_format({'num_format': '0.00', 'align': 'center'})

            last_row = len(matrix) + 1
            last_col = len(matrix.columns)
            col_letter_start = chr(ord('A') + 1)
            col_letter_end = chr(ord('A') + last_col)
            zone_range = f"{col_letter_start}2:{col_letter_end}{last_row}"

            worksheet.conditional_format(zone_range, {
                'type': '3_color_scale',
                'min_color': "#63BE7B",
                'mid_color': "#FFEB84",
                'max_color': "#F8696B",
            })
        print(f"[💾] Exported FX heatmap to: {OUTPUT_FILE}")
    return matrix

if __name__ == "__main__":
    generate_fx_change_heatmap()
    print("✅ FX Change Heatmap script loaded with no syntax errors.")
    