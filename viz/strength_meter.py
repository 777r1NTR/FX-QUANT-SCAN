# viz/strength_meter.py
# viz/strength_meter.py
import streamlit as st
import pandas as pd
import numpy as np
import yfinance as yf
from datetime import datetime, timezone
import plotly.express as px
import plotly.graph_objects as go

# === CONFIG (Same as your heatmap) ===
CURRENCY_LIST = ['USD','CAD', 'EUR', 'GBP', 'CHF', 'NOK', 'SGD','JPY', 'AUD', 'NZD']

def get_daily_pct_change(ticker):
    """Get daily percentage change for a currency pair (same as heatmap)"""
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

def calculate_currency_strength():
    """Calculate individual currency strength by averaging against all pairs"""
    
    # Dictionary to store each currency's performance against others
    currency_scores = {currency: [] for currency in CURRENCY_LIST}
    
    # Progress bar for data fetching
    progress_bar = st.progress(0)
    status_text = st.empty()
    
    total_pairs = len(CURRENCY_LIST) * (len(CURRENCY_LIST) - 1)
    current_pair = 0
    
    for base in CURRENCY_LIST:
        for quote in CURRENCY_LIST:
            if base == quote:
                continue  # Skip same currency pairs
                
            pair = f"{base}{quote}=X"
            status_text.text(f"Analyzing {pair}...")
            
            pct_change = get_daily_pct_change(pair)
            
            if pct_change is not None:
                # Base currency gains strength when pair goes UP
                currency_scores[base].append(pct_change)
                # Quote currency gains strength when pair goes DOWN
                currency_scores[quote].append(-pct_change)
            
            current_pair += 1
            progress_bar.progress(current_pair / total_pairs)
    
    # Clear progress indicators
    progress_bar.empty()
    status_text.empty()
    
    # Calculate average strength for each currency
    strength_data = []
    for currency, scores in currency_scores.items():
        if scores:  # Only if we have data
            avg_strength = np.mean(scores)
            strength_data.append({
                'Currency': currency,
                'Strength_Score': round(avg_strength, 3),
                'Data_Points': len(scores)
            })
    
    # Convert to DataFrame and sort by strength
    df = pd.DataFrame(strength_data)
    df = df.sort_values('Strength_Score', ascending=False).reset_index(drop=True)
    df['Rank'] = df.index + 1
    
    return df

def create_strength_chart(df):
    """Create beautiful strength meter visualization"""
    
    # Create colors based on strength (Green = Strong, Red = Weak)
    colors = []
    for score in df['Strength_Score']:
        if score > 0.5:
            colors.append('#63BE7B')      # Strong Green
        elif score > 0.1:
            colors.append('#90EE90')      # Light Green
        elif score > -0.1:
            colors.append('#FFEB84')      # Yellow (Neutral)
        elif score > -0.5:
            colors.append('#FFB6C1')      # Light Red
        else:
            colors.append('#F8696B')      # Strong Red
    
    # Create horizontal bar chart
    fig = go.Figure()
    
    fig.add_trace(go.Bar(
        y=df['Currency'],
        x=df['Strength_Score'],
        orientation='h',
        marker=dict(
            color=colors,
            line=dict(color='rgba(0,0,0,0.8)', width=1)
        ),
        text=[f"{score:.2f}%" for score in df['Strength_Score']],
        textposition='outside',
        textfont=dict(size=12, color='white', family='Arial Black'),
        hovertemplate='<b>%{y}</b><br>Strength: %{x:.2f}%<br>Rank: #%{customdata}<extra></extra>',
        customdata=df['Rank']
    ))
    
    fig.update_layout(
        title={
            'text': f"💪 Currency Strength Meter - {datetime.now().strftime('%Y-%m-%d')}",
            'x': 0.5,
            'font': {'size': 20, 'color': 'white', 'family': 'Arial Black'}
        },
        xaxis_title="Strength Score (%)",
        yaxis_title="Currency",
        font=dict(size=12, color='white'),
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        height=600,
        margin=dict(l=80, r=120, t=100, b=80),
        showlegend=False
    )
    
    # Add vertical line at zero
    fig.add_vline(x=0, line_dash="dash", line_color="gray", opacity=0.7)
    
    fig.update_xaxes(tickfont=dict(size=12, color='white'))
    fig.update_yaxes(tickfont=dict(size=12, color='white', family='Arial Black'))
    
    return fig

def create_strength_table(df):
    """Create a formatted strength ranking table"""
    
    # Add visual indicators
    df_display = df.copy()
    
    # Add emoji indicators based on strength
    def get_strength_emoji(score):
        if score > 0.5:
            return "🚀"
        elif score > 0.1:
            return "📈"
        elif score > -0.1:
            return "➡️"
        elif score > -0.5:
            return "📉"
        else:
            return "🔻"
    
    df_display['Status'] = df_display['Strength_Score'].apply(get_strength_emoji)
    df_display['Strength %'] = df_display['Strength_Score'].apply(lambda x: f"{x:.2f}%")
    
    # Select columns for display
    display_df = df_display[['Rank', 'Currency', 'Status', 'Strength %', 'Data_Points']]
    
    return display_df

def strength_meter():
    st.title("💪 Currency Strength Meter")
    
    # Add refresh button and info (same pattern as heatmap)
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col1:
        refresh_data = st.button("🔄 Refresh Live Data", help="Calculate latest currency strength")
    
    with col3:
        st.info(f"🕐 {datetime.now().strftime('%H:%M UTC')}")
    
    # Generate or use cached data
    if refresh_data or 'strength_meter_cache' not in st.session_state:
        st.info("🚀 Calculating currency strength...")
        
        with st.spinner("Analyzing currency pairs..."):
            strength_df = calculate_currency_strength()
            st.session_state.strength_meter_cache = strength_df
            st.session_state.strength_timestamp = datetime.now()
    else:
        strength_df = st.session_state.strength_meter_cache
        cache_time = st.session_state.get('strength_timestamp', datetime.now())
        st.caption(f"📋 Cached data from: {cache_time.strftime('%H:%M:%S')}")
    
    # Display results
    if not strength_df.empty:
        # Main strength chart
        fig = create_strength_chart(strength_df)
        st.plotly_chart(fig, use_container_width=True)
        
        # Show ranking table
        st.subheader("🏆 Currency Rankings")
        display_df = create_strength_table(strength_df)
        
        # Use columns to make it look nicer
        col1, col2 = st.columns([2, 1])
        
        with col1:
            st.dataframe(
                display_df.style.apply(
                    lambda x: ['background-color: #63BE7B; color: black' if i < 3 
                              else 'background-color: #F8696B; color: white' if i >= len(x) - 3 
                              else '' for i in range(len(x))], 
                    axis=0
                ),
                use_container_width=True,
                hide_index=True
            )
        
        with col2:
            st.info("""
            **💡 How to Read:**
            
            🚀 **Very Strong** (>0.5%)  
            📈 **Strong** (>0.1%)  
            ➡️ **Neutral** (-0.1% to 0.1%)  
            📉 **Weak** (<-0.1%)  
            🔻 **Very Weak** (<-0.5%)
            """)
        
        # Summary stats
        st.subheader("📊 Market Summary")
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            strongest = strength_df.iloc[0]
            st.metric(
                "🥇 Strongest", 
                strongest['Currency'], 
                f"{strongest['Strength_Score']:.2f}%"
            )
        
        with col2:
            weakest = strength_df.iloc[-1]
            st.metric(
                "🥉 Weakest", 
                weakest['Currency'], 
                f"{weakest['Strength_Score']:.2f}%"
            )
        
        with col3:
            avg_strength = strength_df['Strength_Score'].mean()
            st.metric("📈 Average", f"{avg_strength:.2f}%")
        
        with col4:
            strength_range = strength_df['Strength_Score'].max() - strength_df['Strength_Score'].min()
            st.metric("📏 Range", f"{strength_range:.2f}%")
        
        # Export functionality
        st.subheader("💾 Export Data")
        col1, col2 = st.columns(2)
        
        with col1:
            csv_data = strength_df.to_csv(index=False).encode('utf-8')
            st.download_button(
                "📥 Download CSV",
                csv_data,
                file_name=f"currency_strength_{datetime.now().strftime('%Y%m%d_%H%M')}.csv",
                mime="text/csv"
            )
        
        with col2:
            # Show raw data
            if st.checkbox("📋 Show Raw Data"):
                st.dataframe(strength_df, use_container_width=True)
    
    else:
        st.error("❌ Could not calculate currency strength - no data available")
        
    # Additional info
    st.markdown("---")
    st.markdown("""
    **📖 About Currency Strength:**
    
    The strength meter calculates how each currency performs against all other major currencies. 
    A positive score means the currency is gaining strength, while negative means it's weakening.
    
    **📊 Calculation Method:**
    - For each currency pair (e.g., EURUSD), if EUR goes up, EUR gets +points and USD gets -points
    - Each currency's final score is the average of all its pair performances
    - Rankings show relative strength in the current market session
    """)