import streamlit as st
import pandas as pd
from datetime import datetime
from core.zone_transition import get_zone_transitions_today

TAB_NAME = "📈 Zone Transitions"

def render():
    st.header("📈 Zone Transitions (Past 24h)")
    
    # Add a refresh button
    col1, col2 = st.columns([1, 4])
    with col1:
        refresh_data = st.button("🔄 Refresh Data", help="Scan for new zone transitions")
    
    # Check if it's weekend
    if datetime.now().weekday() >= 5:
        st.warning("⏸️ Markets are closed on weekends. Showing cached data if available.")
    
    # Get live data or use cached data
    with st.spinner("Scanning tickers for zone transitions..."):
        if refresh_data or 'zone_transitions_cache' not in st.session_state:
            df_transitions = get_zone_transitions_today()
            st.session_state.zone_transitions_cache = df_transitions
        else:
            df_transitions = st.session_state.zone_transitions_cache

    if df_transitions.empty:
        st.info("No zone transitions detected in the last 24 hours.")
        
        # Optionally show historical data from CSV
        st.subheader("📋 Historical Data")
        show_historical = st.checkbox("Show historical transitions from log file")
        
        if show_historical:
            try:
                import os
                log_file = "reports/zone_transition_log.csv"
                if os.path.exists(log_file):
                    df_historical = pd.read_csv(log_file)
                    
                    # Standardize column names
                    if 'Date' in df_historical.columns and 'Timestamp' not in df_historical.columns:
                        df_historical = df_historical.rename(columns={'Date': 'Timestamp'})
                    
                    if 'Timestamp' in df_historical.columns:
                        df_historical['Timestamp'] = pd.to_datetime(df_historical['Timestamp'])
                        df_historical = df_historical.sort_values(by='Timestamp', ascending=False)
                        
                        # Show last 50 transitions
                        st.dataframe(df_historical.head(50), use_container_width=True)
                        st.caption(f"Showing last 50 of {len(df_historical)} total historical transitions")
                else:
                    st.info("No historical data file found.")
            except Exception as e:
                st.error(f"Could not load historical data: {e}")
    else:
        st.success(f"✅ {len(df_transitions)} transitions found in the last 24 hours!")
        
        # Display the fresh data
        st.dataframe(df_transitions, use_container_width=True)
        
        # Add some analytics
        if len(df_transitions) > 0:
            col1, col2, col3 = st.columns(3)
            
            with col1:
                unique_tickers = df_transitions['Ticker'].nunique()
                st.metric("🏷️ Active Tickers", unique_tickers)
            
            with col2:
                most_active = df_transitions['Ticker'].value_counts().iloc[0] if len(df_transitions) > 0 else 0
                st.metric("🔥 Max Transitions", most_active)
            
            with col3:
                latest_time = df_transitions['Timestamp'].max()
                hours_ago = (datetime.now() - latest_time.replace(tzinfo=None)).total_seconds() / 3600
                st.metric("⏰ Latest Transition", f"{hours_ago:.1f}h ago")
            
            # Ticker breakdown
            st.subheader("📊 Transitions by Ticker")
            ticker_counts = df_transitions['Ticker'].value_counts()
            st.bar_chart(ticker_counts)
        
        # Download button
        csv = df_transitions.to_csv(index=False).encode("utf-8")
        st.download_button(
            "📥 Download Current Transitions", 
            csv, 
            file_name=f"zone_transitions_{datetime.now().strftime('%Y%m%d_%H%M')}.csv", 
            mime="text/csv"
        )
