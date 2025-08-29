# viz/fx_correlation.py
import streamlit as st
import pandas as pd
import numpy as np
import yfinance as yf
from datetime import datetime, timedelta
import plotly.express as px
import plotly.graph_objects as go
from itertools import combinations

# === CONFIG (Same as your other tools) ===
CURRENCY_LIST = ['USD','CAD', 'EUR', 'GBP', 'CHF', 'NOK', 'SGD','JPY', 'AUD', 'NZD']

def generate_major_pairs():
    """Generate list of major FX pairs that actually exist in YFinance"""
    
    # Start with known working major pairs
    major_pairs = [
        # USD pairs (these definitely work)
        'EURUSD=X', 'GBPUSD=X', 'AUDUSD=X', 'NZDUSD=X', 
        'USDCAD=X', 'USDCHF=X', 'USDJPY=X', 'USDSGD=X',
        
        # Major crosses (tested to work)
        'EURGBP=X', 'EURJPY=X', 'EURCHF=X', 'EURAUD=X',
        'GBPJPY=X', 'GBPCHF=X', 'GBPAUD=X',
        'AUDJPY=X', 'AUDCAD=X', 'AUDCHF=X',
        'NZDJPY=X', 'NZDCAD=X', 'NZDCHF=X',
        'CADJPY=X', 'CADCHF=X',
        'CHFJPY=X'
    ]
    
    return major_pairs

def get_historical_data(ticker, days=30):
    """Get historical price data for correlation calculation"""
    try:
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)
        
        data = yf.download(
            ticker, 
            start=start_date, 
            end=end_date, 
            interval="1d", 
            progress=False, 
            auto_adjust=False
        )
        
        if len(data) < 5:  # Need minimum data points
            return None
            
        # Calculate daily returns (percentage change)
        # Ensure we get a proper Series, not DataFrame
        close_prices = data['Close']
        if isinstance(close_prices, pd.DataFrame):
            close_prices = close_prices.iloc[:, 0]  # Get first column if DataFrame
        
        returns = close_prices.pct_change().dropna()
        
        # Verify we have a proper Series
        if isinstance(returns, pd.DataFrame):
            returns = returns.iloc[:, 0]  # Convert to Series if still DataFrame
            
        return returns
        
    except Exception as e:
        print(f"[⚠️] Error fetching {ticker}: {e}")
        return None

def calculate_correlation_matrix(pairs, time_period=30):
    """Calculate correlation matrix for all FX pairs"""
    
    # Progress tracking
    progress_bar = st.progress(0)
    status_text = st.empty()
    
    # Dictionary to store returns data
    returns_data = {}
    failed_pairs = []
    
    status_text.text("📊 Fetching historical data...")
    
    # Fetch data for all pairs
    for i, pair in enumerate(pairs):
        pair_name = pair.replace('=X', '')
        status_text.text(f"Fetching {pair_name}...")
        
        returns = get_historical_data(pair, time_period)
        if returns is not None and len(returns) >= 5:  # Need minimum 5 data points
            returns_data[pair_name] = returns
            print(f"✅ {pair_name}: {len(returns)} data points")
        else:
            failed_pairs.append(pair_name)
            print(f"❌ {pair_name}: Failed or insufficient data")
            
        progress_bar.progress((i + 1) / len(pairs))
    
    # Clear progress indicators
    progress_bar.empty()
    
    # Debug info
    st.write(f"**Debug:** Successfully fetched {len(returns_data)} pairs, {len(failed_pairs)} failed")
    if failed_pairs:
        st.write(f"**Failed pairs:** {', '.join(failed_pairs[:5])}")
    
    if len(returns_data) < 2:
        st.error("❌ Need at least 2 currency pairs with valid data")
        return None, None
    
    status_text.text("🧮 Calculating correlations...")
    
    # Find common date range across all pairs
    common_dates = None
    for pair_name, returns in returns_data.items():
        if common_dates is None:
            common_dates = returns.index
        else:
            common_dates = common_dates.intersection(returns.index)
    
    st.write(f"**Debug:** Found {len(common_dates)} common trading days")
    
    if len(common_dates) < 5:
        st.error("❌ Not enough common trading days across pairs")
        return None, None
    
    # Align all returns to common dates and verify data structure
    aligned_returns = {}
    for pair_name, returns in returns_data.items():
        aligned_data = returns.loc[common_dates]
        if len(aligned_data) > 0 and not aligned_data.empty:
            aligned_returns[pair_name] = aligned_data
        
    st.write(f"**Debug:** {len(aligned_returns)} pairs aligned successfully")
    
    if len(aligned_returns) < 2:
        st.error("❌ Not enough pairs after alignment")
        return None, None
    
    # Create DataFrame with explicit index
    try:
        returns_df = pd.DataFrame(aligned_returns, index=common_dates)
        st.write(f"**Debug:** DataFrame created: {returns_df.shape}")
        
        # Calculate correlation matrix
        correlation_matrix = returns_df.corr()
        
        # Calculate summary stats
        summary_stats = analyze_correlations(correlation_matrix)
        
        status_text.empty()
        
        return correlation_matrix, summary_stats
        
    except Exception as e:
        st.error(f"❌ Error creating correlation matrix: {e}")
        status_text.empty()
        return None, None

def analyze_correlations(corr_matrix):
    """Analyze correlation matrix for trading insights"""
    
    # Get upper triangle (avoid duplicate pairs)
    mask = np.triu(np.ones_like(corr_matrix), k=1).astype(bool)
    upper_triangle = corr_matrix.where(mask)
    
    # Find strongest correlations
    correlations_list = []
    for i in range(len(corr_matrix.columns)):
        for j in range(i+1, len(corr_matrix.columns)):
            pair1 = corr_matrix.columns[i]
            pair2 = corr_matrix.columns[j]
            corr_value = corr_matrix.iloc[i, j]
            
            if not pd.isna(corr_value):
                correlations_list.append({
                    'Pair_1': pair1,
                    'Pair_2': pair2,
                    'Correlation': corr_value,
                    'Abs_Correlation': abs(corr_value)
                })
    
    correlations_df = pd.DataFrame(correlations_list)
    
    if len(correlations_df) == 0:
        return None
    
    # Sort by absolute correlation strength
    correlations_df = correlations_df.sort_values('Abs_Correlation', ascending=False)
    
    return {
        'strongest_positive': correlations_df[correlations_df['Correlation'] > 0].head(5),
        'strongest_negative': correlations_df[correlations_df['Correlation'] < 0].head(5),
        'very_correlated': correlations_df[correlations_df['Abs_Correlation'] >= 0.75],
        'uncorrelated': correlations_df[correlations_df['Abs_Correlation'] <= 0.25].head(5),
        'avg_correlation': correlations_df['Abs_Correlation'].mean()
    }

def create_correlation_heatmap(corr_matrix, time_period):
    """Create beautiful correlation heatmap"""
    
    # Custom colorscale: Red (negative) -> White (neutral) -> Green (positive)
    colorscale = [
        [0.0, "#F8696B"],    # Strong negative (Red)
        [0.25, "#FFB6C1"],   # Weak negative (Light Red)
        [0.5, "#FFFFFF"],    # No correlation (White)
        [0.75, "#90EE90"],   # Weak positive (Light Green)
        [1.0, "#63BE7B"]     # Strong positive (Green)
    ]
    
    # Create annotations for correlation values
    annotations = []
    for i, row in enumerate(corr_matrix.index):
        for j, col in enumerate(corr_matrix.columns):
            value = corr_matrix.iloc[i, j]
            if not pd.isna(value):
                # Color text based on correlation strength for readability
                text_color = "white" if abs(value) > 0.6 else "black"
                annotations.append(
                    dict(
                        x=j, y=i,
                        text=f"{value:.2f}",
                        showarrow=False,
                        font=dict(color=text_color, size=10, family="Arial Black")
                    )
                )
    
    fig = go.Figure(data=go.Heatmap(
        z=corr_matrix.values,
        x=corr_matrix.columns,
        y=corr_matrix.index,
        colorscale=colorscale,
        zmid=0,  # Center the colorscale at 0
        zmin=-1,
        zmax=1,
        showscale=True,
        colorbar=dict(
            title="Correlation",
            title_font=dict(color="white", size=12),  # Updated property name
            tickfont=dict(color="white"),
            tickmode="array",
            tickvals=[-1, -0.75, -0.5, -0.25, 0, 0.25, 0.5, 0.75, 1],
            ticktext=["-1.0", "-0.75", "-0.5", "-0.25", "0", "0.25", "0.5", "0.75", "1.0"]
        ),
        hoverongaps=False,
        hovertemplate='<b>%{y} vs %{x}</b><br>Correlation: %{z:.3f}<br><extra></extra>'
    ))
    
    fig.add_annotation(
        text="",
        showarrow=False,
        x=0, y=0
    )
    
    fig.update_layout(
        annotations=annotations,
        title={
            'text': f"🔗 FX Pair Correlation Matrix - {time_period} Days",
            'x': 0.5,
            'font': {'size': 18, 'color': 'white', 'family': 'Arial Black'}
        },
        xaxis_title="Currency Pairs",
        yaxis_title="Currency Pairs", 
        font=dict(size=10, color='white'),
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        height=800,
        margin=dict(l=100, r=100, t=100, b=100)
    )
    
    # Rotate x-axis labels for better readability
    fig.update_xaxes(
        tickangle=45,
        tickfont=dict(size=10, color='white', family='Arial Black')
    )
    fig.update_yaxes(
        tickfont=dict(size=10, color='white', family='Arial Black')
    )
    
    return fig

def display_correlation_insights(summary_stats):
    """Display trading insights from correlation analysis"""
    
    if summary_stats is None:
        return
    
    st.subheader("📈 Correlation Insights")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("**🟢 Strongest Positive Correlations**")
        if len(summary_stats['strongest_positive']) > 0:
            for _, row in summary_stats['strongest_positive'].head(3).iterrows():
                st.write(f"• {row['Pair_1']} ↔ {row['Pair_2']}: **{row['Correlation']:.3f}**")
        else:
            st.write("No strong positive correlations found")
    
    with col2:
        st.markdown("**🔴 Strongest Negative Correlations**")
        if len(summary_stats['strongest_negative']) > 0:
            for _, row in summary_stats['strongest_negative'].head(3).iterrows():
                st.write(f"• {row['Pair_1']} ↔ {row['Pair_2']}: **{row['Correlation']:.3f}**")
        else:
            st.write("No strong negative correlations found")
    
    # Very correlated pairs (±0.75+)
    if len(summary_stats['very_correlated']) > 0:
        st.markdown("**⚡ Very High Correlations (±0.75+)**")
        very_corr_df = summary_stats['very_correlated'].head(5)
        st.dataframe(
            very_corr_df[['Pair_1', 'Pair_2', 'Correlation']].round(3),
            use_container_width=True,
            hide_index=True
        )

def fx_correlation():
    st.title("🔗 FX Pair Correlation Analysis")
    
    # Time period selector
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col1:
        time_period = st.selectbox(
            "📅 Time Period",
            [7, 14, 30, 60, 90],
            index=2,  # Default to 30 days
            help="Number of days for correlation calculation"
        )
    
    with col2:
        refresh_data = st.button("🔄 Refresh Correlation Data", help="Recalculate correlations")
    
    with col3:
        st.info(f"🕐 {datetime.now().strftime('%H:%M UTC')}")
    
    # Generate pairs list
    pairs_list = generate_major_pairs()
    
    # Cache key based on time period
    cache_key = f'correlation_cache_{time_period}d'
    timestamp_key = f'correlation_timestamp_{time_period}d'
    
    # Generate or use cached data
    if refresh_data or cache_key not in st.session_state:
        st.info(f"🚀 Calculating {time_period}-day correlations...")
        
        with st.spinner("Analyzing currency pair relationships..."):
            correlation_matrix, summary_stats = calculate_correlation_matrix(pairs_list, time_period)
            
            if correlation_matrix is not None:
                st.session_state[cache_key] = (correlation_matrix, summary_stats)
                st.session_state[timestamp_key] = datetime.now()
            else:
                st.error("❌ Could not calculate correlations - insufficient data")
                return
    else:
        correlation_matrix, summary_stats = st.session_state[cache_key]
        cache_time = st.session_state.get(timestamp_key, datetime.now())
        st.caption(f"📋 Cached data from: {cache_time.strftime('%H:%M:%S')}")
    
    # Display results
    if correlation_matrix is not None:
        # Main correlation heatmap
        fig = create_correlation_heatmap(correlation_matrix, time_period)
        st.plotly_chart(fig, use_container_width=True)
        
        # Display insights
        display_correlation_insights(summary_stats)
        
        # Summary statistics
        st.subheader("📊 Market Overview")
        col1, col2, col3, col4 = st.columns(4)
        
        if summary_stats:
            with col1:
                avg_corr = summary_stats['avg_correlation']
                st.metric("📈 Avg Correlation", f"{avg_corr:.3f}")
            
            with col2:
                very_corr_count = len(summary_stats['very_correlated'])
                st.metric("⚡ Very Correlated", f"{very_corr_count} pairs")
            
            with col3:
                uncorr_count = len(summary_stats['uncorrelated'])
                st.metric("➡️ Uncorrelated", f"{uncorr_count} pairs")
            
            with col4:
                total_pairs = len(correlation_matrix.columns) * (len(correlation_matrix.columns) - 1) // 2
                st.metric("🔢 Total Pairs", f"{total_pairs}")
        
        # Export functionality
        st.subheader("💾 Export Data")
        col1, col2 = st.columns(2)
        
        with col1:
            csv_data = correlation_matrix.to_csv().encode('utf-8')
            st.download_button(
                "📥 Download Correlation Matrix",
                csv_data,
                file_name=f"fx_correlation_{time_period}d_{datetime.now().strftime('%Y%m%d_%H%M')}.csv",
                mime="text/csv"
            )
        
        with col2:
            if st.checkbox("📋 Show Raw Data"):
                st.dataframe(
                    correlation_matrix.round(3).style.background_gradient(
                        cmap="RdYlGn", 
                        axis=None,
                        vmin=-1,
                        vmax=1
                    ),
                    use_container_width=True
                )
    
    # Educational info
    st.markdown("---")
    st.markdown("""
    **📖 Understanding FX Correlations:**
    
    **🟢 Positive Correlation (+0.75 to +1.0):** Pairs move in same direction
    - *Example: EURUSD & GBPUSD often rise/fall together*
    
    **🔴 Negative Correlation (-0.75 to -1.0):** Pairs move in opposite directions  
    - *Example: EURUSD & USDCHF typically move inversely*
    
    **⚪ No Correlation (±0.25):** Pairs move independently
    - *Good for portfolio diversification*
    
    **💡 Trading Applications:**
    - **Risk Management:** Avoid taking multiple positions in highly correlated pairs
    - **Hedging:** Use negatively correlated pairs to offset risk
    - **Confirmation:** Strong correlations can confirm trade signals
    """)