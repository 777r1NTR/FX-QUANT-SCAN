import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
import yfinance as yf
from datetime import datetime, timedelta
import sys
import os

# Import your existing zone locator function
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'core'))
from zone_locator import generate_current_zone_snapshot, TICKER_LIST, ZONE_DEFINITIONS

def zone_locator():
    # Custom CSS for enhanced styling
    st.markdown("""
    <style>
    .zone-header {
        background: linear-gradient(90deg, #1e40af 0%, #3b82f6 100%);
        color: white;
        padding: 1.5rem;
        border-radius: 10px;
        margin-bottom: 2rem;
        text-align: center;
    }
    
    .zone-card {
        background: linear-gradient(145deg, #f8fafc 0%, #e2e8f0 100%);
        padding: 1.5rem;
        border-radius: 12px;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
        margin: 1rem 0;
        border-left: 5px solid;
        color: #374151;
    }
    
    .zone-reset { border-left-color: #A9A9A9; background: linear-gradient(145deg, #f8fafc 0%, #f1f5f9 100%); }
    .zone-clearance { border-left-color: #FF5555; background: linear-gradient(145deg, #fef2f2 0%, #fecaca 100%); }
    .zone-discount { border-left-color: #FF9999; background: linear-gradient(145deg, #fff5f5 0%, #fed7d7 100%); }
    .zone-budget { border-left-color: #ADD8E6; background: linear-gradient(145deg, #eff6ff 0%, #dbeafe 100%); }
    .zone-fair { border-left-color: #90EE90; background: linear-gradient(145deg, #f0fdf4 0%, #dcfce7 100%); }
    .zone-plus { border-left-color: #FFA500; background: linear-gradient(145deg, #fffbeb 0%, #fed7aa 100%); }
    .zone-premium { border-left-color: #FFD700; background: linear-gradient(145deg, #fefce8 0%, #fef08a 100%); }
    .zone-premium-plus { border-left-color: #DA70D6; background: linear-gradient(145deg, #faf5ff 0%, #e9d5ff 100%); }
    
    .metric-box {
        background: linear-gradient(145deg, #f8fafc 0%, #e2e8f0 100%);
        padding: 1rem;
        border-radius: 8px;
        text-align: center;
        margin: 0.5rem 0;
        border: 2px solid #e2e8f0;
    }
    
    .zone-legend {
        background: linear-gradient(145deg, #f0f9ff 0%, #e0f2fe 100%);
        padding: 1rem;
        border-radius: 8px;
        margin: 1rem 0;
        color: #374151;
    }
    </style>
    """, unsafe_allow_html=True)
    
    # Header
    st.markdown("""
    <div class="zone-header">
        <h1>🎯 Zone Locator</h1>
        <p>Identify if currency pairs are cheap, fairly priced, or expensive based on historical zones</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Control Panel
    st.markdown("## ⚙️ Analysis Controls")
    
    col1, col2, col3 = st.columns([2, 2, 1])
    
    with col1:
        selected_pair = st.selectbox(
            "🎯 Select Currency Pair",
            TICKER_LIST,
            help="Choose a currency pair to analyze its current zone position"
        )
    
    with col2:
        analysis_period = st.selectbox(
            "📅 Analysis Period",
            ["1 Month", "3 Months", "6 Months", "1 Year"],
            index=2,
            help="Historical period for zone context visualization"
        )
    
    with col3:
        refresh_data = st.button("🔄 Refresh Data", type="primary")
    
    # Zone Legend
    st.markdown("### 📊 Zone Classification Legend")
    
    zone_info = {
        'Premium+': {'color': '#DA70D6', 'desc': 'Extreme highs, very expensive'},
        'Premium': {'color': '#FFD700', 'desc': 'Historical highs, expensive'},
        'Plus+': {'color': '#FFA500', 'desc': 'Above fair value'},
        'Fair': {'color': '#90EE90', 'desc': 'Balanced pricing'},
        'Budget': {'color': '#ADD8E6', 'desc': 'Good value territory'},
        'Discount': {'color': '#FF9999', 'desc': 'Below fair value'},
        'Clearance': {'color': '#FF5555', 'desc': 'Very cheap levels'},
        'Reset': {'color': '#A9A9A9', 'desc': 'Historical lows, extreme'}
    }
    
    cols = st.columns(4)
    for i, (zone, info) in enumerate(zone_info.items()):
        with cols[i % 4]:
            st.markdown(f"""
            <div class="zone-legend">
                <div style="background: {info['color']}; height: 4px; margin-bottom: 8px; border-radius: 2px;"></div>
                <strong>{zone}</strong><br>
                <small>{info['desc']}</small>
            </div>
            """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Get zone data
    try:
        with st.spinner("🔍 Loading zone data..."):
            if refresh_data or 'zone_data' not in st.session_state:
                zone_df = generate_current_zone_snapshot()
                st.session_state.zone_data = zone_df
            else:
                zone_df = st.session_state.zone_data
            
            if zone_df.empty:
                st.warning("⚠️ No zone data available")
                return
                
    except Exception as e:
        st.error(f"❌ Error loading zone data: {str(e)}")
        return
    
    # Find selected pair data
    selected_data = zone_df[zone_df['Ticker'] == selected_pair]
    
    if selected_data.empty:
        st.warning(f"⚠️ No data available for {selected_pair}")
        return
    
    current_zone = selected_data.iloc[0]['Current Zone']
    current_price = selected_data.iloc[0]['Current Price']
    
    # Zone color mapping
    zone_colors = {
        'Premium+': '#DA70D6',
        'Premium': '#FFD700', 
        'Plus+': '#FFA500',
        'Fair': '#90EE90',
        'Budget': '#ADD8E6',
        'Discount': '#FF9999',
        'Clearance': '#FF5555',
        'Reset': '#A9A9A9'
    }
    
    zone_classes = {
        'Premium+': 'zone-premium-plus',
        'Premium': 'zone-premium',
        'Plus+': 'zone-plus',
        'Fair': 'zone-fair',
        'Budget': 'zone-budget',
        'Discount': 'zone-discount',
        'Clearance': 'zone-clearance',
        'Reset': 'zone-reset'
    }
    
    zone_color = zone_colors.get(current_zone, '#6b7280')
    zone_class = zone_classes.get(current_zone, 'zone-neutral')
    
    # Current Zone Analysis
    st.markdown("## 📍 Current Zone Analysis")
    
    col1, col2 = st.columns([1, 2])
    
    with col1:
        st.markdown(f"""
        <div class="zone-card {zone_class}">
            <div style="font-size: 1.2rem; font-weight: 600; margin-bottom: 0.5rem;">Current Zone</div>
            <div style="font-size: 2rem; font-weight: bold; color: {zone_color};">
                {current_zone}
            </div>
            <div style="font-size: 1.5rem; font-weight: bold; color: #1f2937;">{current_price:.5f}</div>
            <div style="color: #6b7280; font-size: 0.9rem;">
                Updated: {datetime.now().strftime('%H:%M:%S')}
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        # Zone distribution chart
        zone_counts = zone_df['Current Zone'].value_counts()
        
        fig_dist = go.Figure(data=[
            go.Bar(
                x=zone_counts.index,
                y=zone_counts.values,
                marker_color=[zone_colors.get(zone, '#6b7280') for zone in zone_counts.index],
                text=zone_counts.values,
                textposition='auto',
            )
        ])
        
        fig_dist.update_layout(
            title="Current Zone Distribution Across All Pairs",
            xaxis_title="Zone",
            yaxis_title="Number of Pairs",
            height=300,
            template="plotly_white"
        )
        
        st.plotly_chart(fig_dist, use_container_width=True)
    
    # Zone interpretation
    zone_interpretations = {
        'Reset': {
            'emoji': '⚪',
            'title': 'RESET Zone - Extreme Oversold',
            'description': 'This currency pair is at historical lows. Maximum risk/reward potential.',
            'strategy': 'Consider: Contrarian plays, small position sizing, wait for confirmation',
            'risk': 'Very High - New lows possible, fundamental deterioration likely'
        },
        'Clearance': {
            'emoji': '🔴',
            'title': 'CLEARANCE Zone - Very Cheap',
            'description': 'Significantly below normal levels. Strong oversold conditions.',
            'strategy': 'Consider: Value plays, gradual accumulation, support levels',
            'risk': 'High - Further decline possible, but good risk/reward'
        },
        'Discount': {
            'emoji': '🟡',
            'title': 'DISCOUNT Zone - Below Fair Value',
            'description': 'Trading below historical average. Good value territory.',
            'strategy': 'Consider: Buying opportunities, normal position sizing',
            'risk': 'Medium - Normal volatility, favorable entry levels'
        },
        'Budget': {
            'emoji': '🔵',
            'title': 'BUDGET Zone - Good Value',
            'description': 'Attractive pricing with room for upside to fair value.',
            'strategy': 'Consider: Long positions, trend following, value plays',
            'risk': 'Low-Medium - Good risk/reward balance'
        },
        'Fair': {
            'emoji': '🟢',
            'title': 'FAIR Zone - Balanced Pricing',
            'description': 'Trading around historical average levels. Neutral valuation.',
            'strategy': 'Consider: Momentum strategies, breakout plays, trend following',
            'risk': 'Medium - Normal volatility expected'
        },
        'Plus+': {
            'emoji': '🟠',
            'title': 'PLUS+ Zone - Above Fair Value',
            'description': 'Trading above normal levels. Momentum or early overvaluation.',
            'strategy': 'Consider: Momentum continuation, reduced position sizing',
            'risk': 'Medium-High - Correction risk increasing'
        },
        'Premium': {
            'emoji': '🟡',
            'title': 'PREMIUM Zone - Expensive Territory',
            'description': 'At historically high levels. Strong momentum or overvaluation.',
            'strategy': 'Consider: Trend continuation, tight stops, take profits',
            'risk': 'High - Significant correction risk'
        },
        'Premium+': {
            'emoji': '🟣',
            'title': 'PREMIUM+ Zone - Extreme Highs',
            'description': 'At extreme historical levels. Maximum overvaluation risk.',
            'strategy': 'Consider: Short opportunities, minimal long exposure',
            'risk': 'Very High - Major correction likely'
        }
    }
    
    interpretation = zone_interpretations.get(current_zone, zone_interpretations['Fair'])
    
    st.markdown(f"""
    <div class="zone-card {zone_class}">
        <h3>{interpretation['emoji']} {interpretation['title']}</h3>
        <p><strong>{interpretation['description']}</strong></p>
        <p><strong>Strategy Considerations:</strong> {interpretation['strategy']}</p>
        <p><strong>Risk Level:</strong> {interpretation['risk']}</p>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Historical Price Chart
    st.markdown("## 📈 Price Chart with Zone Context")
    
    try:
        period_map = {
            "1 Month": "1mo",
            "3 Months": "3mo", 
            "6 Months": "6mo",
            "1 Year": "1y"
        }
        
        ticker = yf.Ticker(selected_pair)
        hist_data = ticker.history(period=period_map[analysis_period])
        
        if not hist_data.empty:
            # Create candlestick chart
            fig = go.Figure()
            
            fig.add_trace(go.Candlestick(
                x=hist_data.index,
                open=hist_data['Open'],
                high=hist_data['High'], 
                low=hist_data['Low'],
                close=hist_data['Close'],
                name=selected_pair,
                increasing_line_color='#059669',
                decreasing_line_color='#dc2626'
            ))
            
            # Add current price line
            fig.add_hline(
                y=current_price,
                line_dash="dash",
                line_color=zone_color,
                annotation_text=f"Current: {current_price:.5f} ({current_zone})"
            )
            
            fig.update_layout(
                title=f"{selected_pair} - Current Zone: {current_zone}",
                xaxis_title="Date",
                yaxis_title="Price",
                height=500,
                template="plotly_white",
                showlegend=False
            )
            
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.warning("⚠️ No historical data available for chart")
            
    except Exception as e:
        st.error(f"❌ Error creating chart: {str(e)}")
    
    # All Zones Summary
    st.markdown("## 📊 All Pairs Zone Summary")
    
    # Style the dataframe
    styled_df = zone_df.copy()
    styled_df['Current Price'] = styled_df['Current Price'].round(5)
    
    st.dataframe(
        styled_df,
        use_container_width=True,
        column_config={
            "Ticker": st.column_config.TextColumn("Currency Pair", width="medium"),
            "Current Zone": st.column_config.TextColumn("Zone", width="medium"), 
            "Current Price": st.column_config.NumberColumn("Price", width="medium", format="%.5f")
        }
    )
    
    # Zone Statistics
    col1, col2, col3 = st.columns(3)
    
    with col1:
        expensive_zones = zone_df[zone_df['Current Zone'].isin(['Premium+', 'Premium', 'Plus+'])].shape[0]
        st.metric("🔴 Expensive Pairs", expensive_zones)
    
    with col2:
        fair_zones = zone_df[zone_df['Current Zone'].isin(['Fair', 'Budget'])].shape[0]
        st.metric("🟢 Fair Value Pairs", fair_zones)
    
    with col3:
        cheap_zones = zone_df[zone_df['Current Zone'].isin(['Discount', 'Clearance', 'Reset'])].shape[0]
        st.metric("🔵 Cheap Pairs", cheap_zones)
    
    # Footer
    st.markdown("---")
    st.markdown("""
    <div style="text-align: center; color: #6b7280; padding: 1rem;">
        <p><strong>Zone Locator</strong> - Historical zone analysis for informed trading decisions</p>
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    zone_locator()