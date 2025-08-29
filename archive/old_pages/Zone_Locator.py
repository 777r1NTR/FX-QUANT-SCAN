# File: pages/Zone_Locator.py
import streamlit as st
import pandas as pd
from core.zone_locator import generate_current_zone_snapshot

st.set_page_config(page_title="Zone Locator", layout="wide")
st.title("📍 Zone Locator")

with st.spinner("Computing current zones..."):
    df_zones = generate_current_zone_snapshot()

if df_zones.empty:
    st.warning("No zone data available. Check data sources.")
else:
    st.success("Zone snapshot generated!")
    st.dataframe(df_zones, use_container_width=True)

    zone_counts = df_zones['Current Zone'].value_counts().reset_index()
    zone_counts.columns = ['Zone', 'Tickers in Zone']

    st.subheader("📊 Zone Distribution")
    st.bar_chart(zone_counts.set_index('Zone'))
