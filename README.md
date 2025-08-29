# FX-QUANT-SCAN
Access Link:
https://fx-quant-scan-3wvacmjpkn9zkybjmfhbvg.streamlit.app/

Reduce decision fatigue, use FX Quant Scan
Professional FX Analytics & Zone-Based Market Analysis Platform
A comprehensive Streamlit-based web application for foreign exchange market analysis, featuring real-time data visualization, currency strength analysis, and innovative zone-based price evaluation.

Run locally with:
streamlit run scan_x.py

✨ Features
🏠 Dashboard Overview

Professional landing page with platform explanation
Quick stats and feature overview
Zone analysis methodology explanation

📊 FX Heatmap

Real-time percentage changes across 28 major currency pairs
Interactive visualization using Plotly
Market overview for daily trading preparation
Currency strength comparison at a glance

💪 Currency Strength Meter

Individual currency rankings with strength scores
Beautiful interactive charts showing momentum
Strength-based trading insights
Historical strength trends

🎯 Zone Locator ⭐ Unique Feature

Zone-based price analysis using historical support/resistance levels
Fair value assessment - determine if currencies are cheap, fairly priced, or expensive
Historical zone visualization with interactive charts
Risk assessment based on zone positioning
Three main zones: RESET (oversold), BUDGET (fair value), PREMIUM+ (expensive)

🔗 FX Correlation Matrix

Comprehensive 24x24 correlation matrix
Multiple timeframes (7-90 days)
Risk management insights for portfolio diversification
Pair trading opportunities identification

🎯 Zone Analysis Methodology
What Are Trading Zones?
Zones are price ranges defined by historically significant support and resistance levels. Think of them as "neighborhoods" where currency pairs prefer to trade.
Key Concepts:

Historical Analysis: Years of price data identify significant levels
Zone Classification: Price ranges between levels become named zones
Fair Value Discovery: Track which zones pairs spend most time in
Market Positioning: Current location indicates if currency is cheap/expensive

Zone Categories
ZoneIndicatorMeaningStrategy🔴 RESETHistorical LowsPotential oversold conditionsContrarian plays, small positions🟢 BUDGETFair ValueNormal/average pricingMomentum strategies, normal sizing🟠 PREMIUM+Historical HighsExpensive territoryTrend continuation, reduced sizing
🛠️ Technical Stack

Frontend: Streamlit with custom CSS styling
Data Sources: Yahoo Finance API (yfinance)
Visualizations: Plotly (interactive charts)
Zone Data: Excel-based historical level definitions
Architecture: Modular design with separated concerns

📁 Project Structure
QUANT_FRAMEWORK/
├── 📁 viz/                    # Streamlit pages
│   ├── home.py               # Enhanced dashboard  
│   ├── fx_heatmap.py         # Real-time heatmap
│   ├── strength_meter.py     # Currency strength
│   ├── zone_locator.py       # Zone analysis (enhanced)
│   ├── fx_correlation.py     # Correlation matrix
│   └── zone_transitions.py   # [Coming Soon]
├── 📁 core/                   # Business logic
│   └── zone_locator.py       # Zone calculation engine
├── 📁 reports/                # Data exports
│   ├── current_zone_snapshot.csv
│   ├── zone_history.csv
│   └── zone_transition_log.csv
├── 📁 archive/                # Legacy code (archived)
├── 📄 scan_x.py              # Main Streamlit app
└── 📄 requirements.txt       # Dependencies
🚀 Quick Start
Prerequisites

Python 3.8+
pip package manager

Installation

Clone the repository
bashgit clone https://github.com/yourusername/fx-quant-scan.git
cd fx-quant-scan

Install dependencies
bashpip install -r requirements.txt

Run the application
bashstreamlit run scan_x.py

Open your browser
Local URL: http://localhost:8501


📊 Usage Guide
Daily Workflow

📊 Start with FX Heatmap - Get overall market view
💪 Check Currency Strength - Identify moving currencies
🎯 Use Zone Locator - Assess if targets are cheap/expensive
🔗 Verify with Correlations - Risk management check

Pro Tips

Combine zone + strength: Look for strong currencies in budget zones
Use correlation matrix: Avoid highly correlated trades
Monitor zone transitions: Track when pairs move between zones
Historical context: Always consider longer-term zone positioning

🔧 Configuration
Zone Data Setup
Zone definitions are stored in Excel files with historical support/resistance levels:

Each currency pair has defined zone boundaries
Zones are calculated from years of historical price data
Manual updates possible for major market structure changes

Customization

Colors: Modify CSS in individual page files
Timeframes: Adjust in correlation and heatmap modules
Currency Pairs: Add new pairs to zone definition files

📈 Features in Development

🔄 Zone Transitions: Advanced zone change tracking (coming soon)
📱 Mobile Optimization: Improved mobile responsiveness
💾 Data Persistence: Database integration for faster loading
🤖 Strategy Integration: Backtesting capabilities
📧 Alerts: Zone breakout notifications

🤝 Contributing
This is a personal trading tool developed for educational and analysis purposes. Feel free to fork and adapt for your own use.
Development Guidelines

Follow existing code structure in viz/ and core/
Maintain Streamlit best practices
Keep visualizations interactive and professional
Test with multiple currency pairs before committing

⚠️ Disclaimer
This tool is for educational and analysis purposes only.

Not financial advice
Past performance doesn't guarantee future results
Always do your own research
Consider risk management in all trading decisions
