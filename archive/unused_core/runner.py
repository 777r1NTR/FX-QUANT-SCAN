# core/runner.py

import os
import pandas as pd
from core.strategy_engine import run_strategy_on_ticker, plot_equity_curve
from core.metrics import compute_fx_metrics
from data.local_loader import load_local_csv


def run_all_strategies(tickers: list[str], strategy_registry: dict,
                       start_date: str, end_date: str,
                       atr_mult: float = 1.5, max_bars: int = 20,
                       export: bool = True) -> pd.DataFrame:

    all_results = []
    os.makedirs("reports", exist_ok=True)

    for strategy_name, strategy_func in strategy_registry.items():
        print(f"\n[🚀] Running strategy: {strategy_name}")

        for ticker in tickers:
            print(f"  → Ticker: {ticker}")

            df = load_local_csv(ticker, start_date=start_date, end_date=end_date)
            if df.empty:
                print(f"[⚠️] No data for {ticker}, skipping.")
                continue

            trade_log, metrics = run_strategy_on_ticker(
                df, strategy_func, strategy_name + f"_{ticker}",
                atr_mult=atr_mult, max_bars=max_bars
            )

            if trade_log.empty or not metrics:
                continue

            metrics['Strategy_Ticker'] = f"{strategy_name}_{ticker}"
            all_results.append(metrics)

            if export:
                outpath = f"reports/strategy_report_{strategy_name.lower()}_{ticker.lower()}.xlsx"
                chart_path = f"reports/strategy_report_{strategy_name.lower()}_{ticker.lower()}_equity_curve.png"
                plot_equity_curve(trade_log, strategy_name, chart_path)

                with pd.ExcelWriter(outpath, engine='xlsxwriter') as writer:
                    trade_log.to_excel(writer, sheet_name='Trades', index=False)
                    pd.DataFrame([metrics]).to_excel(writer, sheet_name='Metrics', index=False)
                    worksheet = writer.book.add_worksheet('EquityCurve')
                    writer.sheets['EquityCurve'] = worksheet
                    worksheet.insert_image('B2', chart_path)

                print(f"[💾] Exported report: {outpath}")

    summary_df = pd.DataFrame(all_results)
    if export and not summary_df.empty:
        summary_path = "reports/strategy_summary.xlsx"
        summary_df.to_excel(summary_path, index=False)
        print(f"[📊] Summary exported to {summary_path}")

    return summary_df
