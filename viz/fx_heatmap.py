# viz/fx_heatmap.py
# viz/fx_heatmap.py
import streamlit as st
import pandas as pd
import numpy as np
import yfinance as yf
from datetime import datetime, timezone
import plotly.express as px
import plotly.graph_objects as go

# === CONFIG ===
CURRENCY_LIST = ['USD','CAD', 'EUR', 'GBP', 'CHF','SGD','JPY', 'AUD', 'NZD']

def get_daily_pct_change(ticker):
    """Get daily percentage change for a currency pair"""
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

def generate_live_heatmap():
    """Generate live FX percentage change heatmap"""
    matrix = pd.DataFrame(index=CURRENCY_LIST, columns=CURRENCY_LIST, dtype=float)
    
    # Progress bar for data fetching
    progress_bar = st.progress(0)
    status_text = st.empty()
    
    total_pairs = len(CURRENCY_LIST) * (len(CURRENCY_LIST) - 1)
    current_pair = 0
    
    for base in CURRENCY_LIST:
        for quote in CURRENCY_LIST:
            if base == quote:
                matrix.at[base, quote] = 0.0  # Same currency = 0%
                continue
                
            pair = f"{base}{quote}=X"
            status_text.text(f"Fetching {pair}...")
            
            pct_change = get_daily_pct_change(pair)
            if pct_change is not None:
                matrix.at[base, quote] = round(pct_change, 2)
            else:
                matrix.at[base, quote] = np.nan
                
            current_pair += 1
            progress_bar.progress(current_pair / total_pairs)
    
    # Clear progress indicators
    progress_bar.empty()
    status_text.empty()
    
    return matrix

def create_beautiful_heatmap(matrix):
    """Create a beautiful plotly heatmap with your preferred styling"""
    
    # Create custom colorscale (Green -> Yellow -> Red)
    colorscale = [
        [0.0, "#63BE7B"],    # Green (negative/good for some pairs)
        [0.5, "#FFEB84"],    # Yellow (neutral)
        [1.0, "#F8696B"]     # Red (positive/bad for some pairs)
    ]
    
    fig = go.Figure(data=go.Heatmap(
        z=matrix.values,
        x=matrix.columns,
        y=matrix.index,
        colorscale=colorscale,
        showscale=True,
        text=matrix.values,
        texttemplate="%{text:.2f}%",
        textfont={"size": 12, "color": "black", "family": "Arial Black"},
        hoverongaps=False,
        hovertemplate='<b>%{y}/%{x}</b><br>Change: %{z:.2f}%<extra></extra>'
    ))
    
    fig.update_layout(
    title={
        'text': f"FX Daily % Change Heatmap - {datetime.now().strftime('%Y-%m-%d')}",
        'x': 0.5,
        'y': 0.95,  # Move title up slightly
        'font': {'size': 18, 'color': 'white', 'family': 'Arial Black'}
    },
    xaxis_title={
        'text': "Quote Currency",
        'font': {'size': 14, 'color': 'white', 'family': 'Arial Black'}
    },
    yaxis_title={
        'text': "Base Currency", 
        'font': {'size': 14, 'color': 'white', 'family': 'Arial Black'}
    },
    font=dict(size=12, color='white'),
    plot_bgcolor='rgba(0,0,0,0)',
    paper_bgcolor='rgba(0,0,0,0)',
    height=650,  # Increased height to give more room
    margin=dict(l=100, r=80, t=120, b=80)  # Increased top and left margins
)

    fig.update_xaxes(
    side="top", 
    tickfont=dict(size=12, color='white', family='Arial Black'),
    title_standoff=20  # Add space between title and ticks
)
    fig.update_yaxes(
    tickfont=dict(size=12, color='white', family='Arial Black'),
    title_standoff=20  # Add space between title and ticks
)
    
    return fig

def fx_heatmap():
    st.title("📊 FX Daily % Change Heatmap")
    
    # Add refresh button and info
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col1:
        refresh_data = st.button("🔄 Refresh Live Data", help="Fetch latest FX data")
    
    with col3:
        st.info(f"🕐 {datetime.now().strftime('%H:%M UTC')}")
    
    # Generate or use cached data
    if refresh_data or 'fx_heatmap_cache' not in st.session_state:
        st.info("🚀 Fetching live FX data...")
        
        with st.spinner("Loading currency data..."):
            matrix = generate_live_heatmap()
            st.session_state.fx_heatmap_cache = matrix
            st.session_state.heatmap_timestamp = datetime.now()
    else:
        matrix = st.session_state.fx_heatmap_cache
        cache_time = st.session_state.get('heatmap_timestamp', datetime.now())
        st.caption(f"📋 Cached data from: {cache_time.strftime('%H:%M:%S')}")
    
    # Create and display beautiful heatmap
    if not matrix.empty:
        fig = create_beautiful_heatmap(matrix)
        st.plotly_chart(fig, use_container_width=True)
        
        # Summary stats
        st.subheader("📈 Market Summary")
        col1, col2, col3, col4 = st.columns(4)
        
        # Calculate stats (excluding NaN and zeros)
        clean_data = matrix.replace([np.inf, -np.inf], np.nan).dropna().values.flatten()
        clean_data = clean_data[clean_data != 0]  # Remove diagonal zeros
        
        if len(clean_data) > 0:
            with col1:
                st.metric("📊 Strongest Move", f"{clean_data.max():.2f}%")
            with col2:
                st.metric("📉 Weakest Move", f"{clean_data.min():.2f}%")
            with col3:
                st.metric("📈 Average Move", f"{clean_data.mean():.2f}%")
            with col4:
                volatility = clean_data.std()
                st.metric("⚡ Volatility", f"{volatility:.2f}%")
        
        # Export functionality
        st.subheader("💾 Export Data")
        col1, col2 = st.columns(2)
        
        with col1:
            csv_data = matrix.to_csv().encode('utf-8')
            st.download_button(
                "📥 Download CSV",
                csv_data,
                file_name=f"fx_heatmap_{datetime.now().strftime('%Y%m%d_%H%M')}.csv",
                mime="text/csv"
            )
        
        with col2:
            # Show data table
            if st.checkbox("📋 Show Raw Data"):
                st.dataframe(
                    matrix.style.background_gradient(
                        cmap="RdYlGn_r", 
                        axis=None
                    ).format("{:.2f}%"),
                    use_container_width=True
                )
    else:
        st.error("❌ Could not generate heatmap - no data available")