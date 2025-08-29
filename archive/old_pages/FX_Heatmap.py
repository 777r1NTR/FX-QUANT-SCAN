# Quant_framework/app/FX_Heatmap.py
import streamlit as st
import pandas as pd
import numpy as np
import yfinance as yf
from datetime import datetime
import os
from viz.fx_heatmap import fx_heatmap
fx_heatmap()



st.title("📊 FX Heatmap Test Page")
st.write("If you see this, multipage tabs are working.")

CURRENCY_LIST = ['USD','CAD','EUR','GBP','JPY','AUD','NZD','CHF','SGD','NOK']
EXPORT_TO_EXCEL = True
OUTPUT_FILE = "reports/fx_major_heatmap.xlsx"
TODAY_DATE = datetime.utcnow().strftime('%Y-%m-%d')

matrix = pd.DataFrame(index=CURRENCY_LIST, columns=CURRENCY_LIST, dtype=float)

@st.cache_data(show_spinner=False)
def get_daily_pct_change(ticker):
    try:
        data = yf.download(ticker, period="2d", interval="1d", progress=False)
        if len(data) < 2:
            return None
        open_val = data['Open'].iloc[-1].item()
        close_val = data['Close'].iloc[-1].item()
        return (close_val - open_val) / open_val * 100
    except:
        return None

with st.spinner("Fetching data from Yahoo Finance..."):
    for base in CURRENCY_LIST:
        for quote in CURRENCY_LIST:
            if base == quote:
                matrix.at[base, quote] = np.nan
                continue
            pair = f"{base}{quote}=X"
            pct = get_daily_pct_change(pair)
            if pct is not None:
                matrix.at[base, quote] = round(pct, 2)

st.subheader(f"% Change Matrix for {TODAY_DATE}")
st.dataframe(matrix.style.background_gradient(cmap="RdYlGn", axis=None).format("{:.2f}"), use_container_width=True)

# === Compute strength ===
strength_scores = pd.Series(dtype=float)
for ccy in CURRENCY_LIST:
    row_mean = matrix.loc[ccy].mean(skipna=True)
    col_mean = matrix[ccy].mean(skipna=True)
    strength = row_mean - col_mean
    strength_scores[ccy] = round(strength, 2)

st.subheader("⚖️ Currency Strength Meter")
st.bar_chart(strength_scores.sort_values(ascending=True))
