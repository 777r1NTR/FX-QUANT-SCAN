import yfinance as yf
import pandas as pd
import os
from datetime import datetime, timezone

# === CONFIG ===
LOOKBACK_DAYS = 10
STD_THRESHOLD = 1.5
EXT_LOG_FILE = "reports/extension_alert_log.csv"
TICKERS = [
    'USDCAD=X', 'USDGBP=X', 'USDNOK=X', 'USDPLN=X', 'USDAUD=X', 'USDSGD=X',
    'USDJPY=X', 'USDZAR=X', 'USDBRL=X', 'EURUSD=X', 'EURGBP=X', 'EURCHF=X',
    'EURPLN=X', 'EURCZK=X', 'EURNZD=X', 'EURSEK=X', 'EURZAR=X', 'EURSGD=X',
    'GBPNOK=X', 'GBPJPY=X', 'GBPAUD=X', 'GBPCAD=X', 'SEKNOK=X', 'SEKJPY=X',
    'CHFNOK=X', 'CADNOK=X', 'AUDNZD=X', 'AUDJPY=X', 'AUDSEK=X', 'AUDCAD=X',
    'NZDSGD=X', 'NZDCHF=X', 'NZDNOK=X', 'SGDJPY=X', 'SGDHKD=X', 'EURCAD=X',
    'USDCHF=X', 'GBPCHF=X', 'EURNOK=X'
]


def get_unusual_movers(tickers, lookback_days, std_threshold):
    unusual_movers = []
    for ticker in tickers:
        try:
            data = yf.download(ticker, period=f"{lookback_days + 2}d", interval='1d', progress=False, auto_adjust=False)
            data['Pct Change'] = data['Close'].pct_change() * 100

            if len(data) < lookback_days + 1 or data['Pct Change'].isna().all():
                print(f"[⚠️] Not enough data for {ticker} — skipping.")
                continue

            last_date = data.index[-1].date()
            if last_date < datetime.now().date():
                print(f"[ℹ️] {ticker} has no new daily candle today — skipping.")
                continue

            recent_changes = data['Pct Change'].iloc[-(lookback_days+1):-1]  # Exclude today
            today_change = data['Pct Change'].iloc[-1]

            avg = recent_changes.mean()
            std = recent_changes.std()

            if abs(today_change) > avg + std_threshold * std:
                unusual_movers.append({
                    'Ticker': ticker,
                    'Today % Change': round(today_change, 2),
                    'Avg % Change': round(avg, 2),
                    'Std Dev': round(std, 2),
                    'Z-Score': round((today_change - avg)/std, 2)
                })
        except Exception as e:
            print(f"[⚠️] Failed to fetch data for {ticker}: {e}")

    return pd.DataFrame(unusual_movers)

def run_overextension_scan():
    today = datetime.now().date()
    if today.weekday() >= 5:
        print("⏸ Market closed (Weekend) — skipping mover scan")
        return pd.DataFrame()

    df_extensions = get_unusual_movers(TICKERS, LOOKBACK_DAYS, STD_THRESHOLD)
    df_extensions["Timestamp"] = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")

    os.makedirs("reports", exist_ok=True)
    df_extensions.to_csv(EXT_LOG_FILE, mode="a", index=False, header=not os.path.exists(EXT_LOG_FILE))

    if df_extensions.empty:
        print("[✅] No unusual extension movers found today.")
    else:
        print("[✅] Unusual Extension Movers:")
        print(df_extensions.sort_values(by='Z-Score', ascending=False).to_string(index=False))

    return df_extensions

if __name__ == "__main__":
    run_overextension_scan()

