# main.py

# main.py

from core.runner import run_all_strategies
from core.strategy_registry import STRATEGY_REGISTRY

if __name__ == "__main__":
    # Tickers to test
    tickers = [
        "CADCHF=X",
        "GBPNOK=X",
        "NZDUSD=X"
    ]

    # Strategies to run
    STRATEGIES_TO_RUN = ["macd_crossover"]  # Add more names as needed

    # Filter only selected strategies
    filtered_registry = {
        name: func for name, func in STRATEGY_REGISTRY.items()
        if name in STRATEGIES_TO_RUN
    }

    # Date range
    start_date = "2025-05-07"
    end_date = "2025-06-18"

    # Run all
    summary_df = run_all_strategies(
        tickers=tickers,
        strategy_registry=filtered_registry,
        start_date=start_date,
        end_date=end_date,
        atr_mult=1.5,
        max_bars=20,
        export=True
    )

    print("\n=== FINAL SUMMARY ===")
    print(summary_df)
