import streamlit as st
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd

def home():
    # Note: Page config is handled by main app (scan_x.py)
    
    # Custom CSS for professional styling
    st.markdown("""
    <style>
    .main-header {
        font-size: 3rem;
        font-weight: 700;
        color: #1f2937;
        text-align: center;
        margin-bottom: 1rem;
        background: linear-gradient(90deg, #3b82f6 0%, #1e40af 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
    }
    
    .sub-header {
        font-size: 1.2rem;
        color: #6b7280;
        text-align: center;
        margin-bottom: 2rem;
    }
    
    .feature-card {
        background: linear-gradient(145deg, #f1f5f9 0%, #e2e8f0 100%);
        padding: 1.5rem;
        border-radius: 12px;
        border-left: 4px solid #3b82f6;
        margin: 1rem 0;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
        color: #1f2937;
    }
    
    .zone-explanation {
        background: linear-gradient(145deg, #f0f9ff 0%, #e0f2fe 100%);
        padding: 2rem;
        border-radius: 12px;
        border: 2px solid #0ea5e9;
        margin: 2rem 0;
        color: #1f2937;
    }
    
    .zone-explanation h3 {
        color: #1e40af;
        margin-bottom: 1rem;
    }
    
    .zone-explanation p {
        color: #374151;
        font-size: 1.1rem;
        line-height: 1.6;
    }
    
    .zone-category {
        background: #f8fafc;
        padding: 1rem;
        border-radius: 8px;
        margin: 0.5rem 0;
        border-left: 3px solid;
        color: #374151;
    }
    
    .zone-reset { border-left-color: #dc2626; }
    .zone-budget { border-left-color: #059669; }
    .zone-premium { border-left-color: #d97706; }
    
    .metric-card {
        background: linear-gradient(145deg, #f8fafc 0%, #e2e8f0 100%);
        padding: 1rem;
        border-radius: 8px;
        text-align: center;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        color: #374151;
    }
    </style>
    """, unsafe_allow_html=True)
    
    # Header Section
    st.markdown('<h1 class="main-header">FX Quant Scan</h1>', unsafe_allow_html=True)
    st.markdown('<p class="sub-header">Professional FX Analytics & Zone-Based Market Analysis Platform</p>', unsafe_allow_html=True)
    
    # Quick Stats Row
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.markdown('<div class="metric-card"><h3>28</h3><p>Currency Pairs</p></div>', unsafe_allow_html=True)
    with col2:
        st.markdown('<div class="metric-card"><h3>6</h3><p>Analysis Tools</p></div>', unsafe_allow_html=True)
    with col3:
        st.markdown('<div class="metric-card"><h3>Real-time</h3><p>Market Data</p></div>', unsafe_allow_html=True)
    with col4:
        st.markdown('<div class="metric-card"><h3>Zone-Based</h3><p>Price Analysis</p></div>', unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Platform Features
    st.markdown("## 🚀 Platform Features")
    
    features = [
        {
            "title": "📊 FX Heatmap",
            "description": "Real-time percentage change visualization across 28 major currency pairs. Instantly identify market movers and currency strength patterns.",
            "use_case": "Perfect for: Market overview, daily trading preparation, currency strength comparison"
        },
        {
            "title": "💪 Currency Strength Meter", 
            "description": "Individual currency strength rankings with beautiful interactive charts. Track which currencies are gaining or losing momentum.",
            "use_case": "Perfect for: Currency selection, strength-based trading strategies, market sentiment analysis"
        },
        {
            "title": "🎯 Zone Locator",
            "description": "Advanced price analysis using historically significant support/resistance levels. Determine if currencies are cheap, fair-priced, or expensive.",
            "use_case": "Perfect for: Entry/exit timing, risk assessment, mean reversion strategies"
        },
        {
            "title": "🔗 FX Correlation Tool",
            "description": "Comprehensive 24x24 correlation matrix with multiple timeframes (7-90 days). Understand currency pair relationships and portfolio risk.",
            "use_case": "Perfect for: Risk management, portfolio diversification, pair trading strategies"
        }
    ]
    
    for feature in features:
        st.markdown(f"""
        <div class="feature-card">
            <h3>{feature['title']}</h3>
            <p><strong>{feature['description']}</strong></p>
            <p style="color: #059669; font-style: italic;">{feature['use_case']}</p>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Zone Analysis Explanation
    st.markdown("## 🎯 Understanding Zone Analysis")
    
    st.markdown("""
    <div class="zone-explanation">
        <h3>💡 What Are Trading Zones?</h3>
        <p><strong>Zones are price ranges defined by historical key support and resistance levels.</strong> Think of them as "neighborhoods" where currency pairs like to spend time.</p>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("### 🔍 How It Works:")
    st.markdown("""
    - **Historical Analysis:** We analyze years of price data to identify significant support/resistance levels
    - **Zone Classification:** Price ranges between these levels become named zones  
    - **Fair Value Discovery:** By tracking which zones pairs spend most time in, we identify "fair prices"
    - **Market Positioning:** Current price location tells us if a currency is cheap, fairly priced, or expensive
    """)
    
    # Zone Categories
    st.markdown("### 📊 Zone Categories Explained")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("""
        <div class="zone-category zone-reset">
            <h4>🔴 RESET Zone</h4>
            <p><strong>Worst Case Scenario</strong></p>
            <p>Currency pair is seeing new historical lows. Potential oversold conditions, but also possible fundamental deterioration.</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class="zone-category zone-budget">
            <h4>🟢 BUDGET Zone</h4>
            <p><strong>Fair Value Range</strong></p>
            <p>Currency pair is trading around historical average levels. This represents "normal" or "fair" pricing based on historical patterns.</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown("""
        <div class="zone-category zone-premium">
            <h4>🟠 PREMIUM+ Zone</h4>
            <p><strong>Expensive Territory</strong></p>
            <p>Currency pair is at historically high levels. May indicate overbought conditions or strong fundamental drivers.</p>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Quick Start Guide
    st.markdown("## 🚀 Quick Start Guide")
    
    st.markdown("""
    1. **📊 Start with FX Heatmap** - Get overall market view and identify active currency pairs
    2. **💪 Check Currency Strength** - Determine which individual currencies are moving
    3. **🎯 Use Zone Locator** - Assess if your target pairs are cheap, fair, or expensive
    4. **🔗 Verify with Correlations** - Ensure your trades aren't highly correlated (risk management)
    
    **💡 Pro Tip:** Combine zone analysis with currency strength for powerful entry signals - look for strong currencies in budget zones!
    """)
    
    # Footer
    st.markdown("---")
    st.markdown("""
    <div style="text-align: center; color: #6b7280; padding: 2rem;">
        <p><strong>FX Quant Scan</strong> - Professional FX Analytics Platform</p>
        <p>Built for traders who value data-driven decisions and quantitative analysis</p>
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    home()