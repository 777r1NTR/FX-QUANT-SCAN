# viz/zone_transitions.py
import streamlit as st
import pandas as pd
import os
from datetime import datetime, timedelta, timezone

def zone_transitions():
    st.title("🔄 Zone Transitions")

    log_file = "reports/zone_transition_log.csv"
    if not os.path.exists(log_file):
        st.warning("Zone transition log not found.")
        return

    try:
        # Read the CSV file
        df = pd.read_csv(log_file)
        
        # Standardize column names - convert 'Date' to 'Timestamp' if needed
        if 'Date' in df.columns and 'Timestamp' not in df.columns:
            df = df.rename(columns={'Date': 'Timestamp'})
        
        if 'Timestamp' not in df.columns:
            st.error("No valid date column found in the CSV file.")
            return
        
        # Parse the timestamp column with proper format handling
        df['Timestamp'] = pd.to_datetime(df['Timestamp'], format='mixed', utc=True)
        
        # Convert to local timezone for comparison
        df['Timestamp'] = df['Timestamp'].dt.tz_convert(None)  # Remove timezone info
        
        # Filter for last 24 hours only
        cutoff_time = datetime.now() - timedelta(hours=24)
        
        # Filter dataframe for last 24 hours
        df_recent = df[df['Timestamp'] >= cutoff_time].copy()
        
        # Sort by timestamp (most recent first)
        df_recent = df_recent.sort_values(by='Timestamp', ascending=False)
        
        # Display results
        if df_recent.empty:
            st.info("No zone transitions detected in the last 24 hours.")
            
            # Show some info about what was filtered out
            if not df.empty:
                total_transitions = len(df)
                oldest = df['Timestamp'].min()
                newest = df['Timestamp'].max()
                filtered_out = total_transitions - len(df_recent)
                
                st.write(f"📊 **Data Summary:**")
                st.write(f"- Total transitions in file: **{total_transitions}**")
                st.write(f"- Filtered out (older than 24h): **{filtered_out}**")
                st.write(f"- Full data range: {oldest.strftime('%Y-%m-%d %H:%M')} to {newest.strftime('%Y-%m-%d %H:%M')}")
                st.write(f"- Cutoff time: {cutoff_time.strftime('%Y-%m-%d %H:%M')}")
                
                # Debug: show some sample data
                with st.expander("🔍 Debug: Recent vs Old Data"):
                    st.write("**Recent data (should show):**")
                    recent_debug = df[df['Timestamp'] >= cutoff_time].head(3)
                    st.write(recent_debug[['Timestamp', 'Ticker']] if not recent_debug.empty else "None")
                    
                    st.write("**Old data (filtered out):**")
                    old_debug = df[df['Timestamp'] < cutoff_time].head(3)
                    st.write(old_debug[['Timestamp', 'Ticker']] if not old_debug.empty else "None")
        else:
            st.success(f"Found {len(df_recent)} zone transitions in the last 24 hours")
            
            # Show time range of displayed data
            latest_date = df_recent['Timestamp'].max()
            oldest_date = df_recent['Timestamp'].min()
            st.info(f"📅 Showing transitions from: {oldest_date.strftime('%Y-%m-%d %H:%M')} to {latest_date.strftime('%Y-%m-%d %H:%M')}")
            
            # Display the dataframe
            st.dataframe(df_recent, use_container_width=True)
            
            # Add download button for recent data
            csv = df_recent.to_csv(index=False).encode("utf-8")
            st.download_button(
                "📥 Download Recent Transitions CSV", 
                csv, 
                file_name="zone_transitions_24h.csv", 
                mime="text/csv"
            )
            
            # Show breakdown by ticker
            if len(df_recent) > 0:
                st.subheader("📈 Breakdown by Ticker")
                ticker_counts = df_recent['Ticker'].value_counts()
                st.bar_chart(ticker_counts)

    except Exception as e:
        st.error(f"Failed to load zone transitions: {e}")
        st.write("Error details:", str(e))
        
        # Try to show what's actually in the file for debugging
        try:
            df_sample = pd.read_csv(log_file, nrows=5)
            st.write("First few lines of the CSV file:")
            st.write(df_sample)
            st.write("Available columns:", list(df_sample.columns))
        except Exception as debug_e:
            st.write("Could not read CSV file at all:", str(debug_e))