# core/metrics.py

import pandas as pd
import numpy as np

def compute_fx_metrics(results_df: pd.DataFrame) -> dict:
    if results_df.empty:
        return {}

    results_df['Return_%'] = (results_df['Exit_Price'] - results_df['Entry_Price']) / results_df['Entry_Price'] * 100
    results_df['Pips'] = (results_df['Exit_Price'] - results_df['Entry_Price']) * 10000

    equity = results_df['Return_%'].cumsum()
    peak = equity.cummax()
    drawdown = peak - equity
    max_dd = drawdown.max()

    win_trades = results_df[results_df['Result'] == 'Win']
    loss_trades = results_df[results_df['Result'] == 'Loss']

    total_return = results_df['Return_%'].sum()
    avg_return = results_df['Return_%'].mean()
    std_return = results_df['Return_%'].std()
    sharpe = (avg_return / std_return) * np.sqrt(252) if std_return else 0
    win_rate = len(win_trades) / len(results_df) if len(results_df) else 0
    expectancy = (win_rate * win_trades['Return_%'].mean()) + ((1 - win_rate) * loss_trades['Return_%'].mean()) if not win_trades.empty and not loss_trades.empty else 0
    profit_factor = win_trades['Return_%'].sum() / abs(loss_trades['Return_%'].sum()) if not loss_trades.empty else np.inf

    return {
        "Total Trades": len(results_df),
        "Total Return %": round(total_return, 2),
        "Avg Return %": round(avg_return, 2),
        "Sharpe Ratio": round(sharpe, 2),
        "Max Drawdown %": round(max_dd, 2),
        "Profit Factor": round(profit_factor, 2),
        "Expectancy": round(expectancy, 2),
        "Win Rate": f"{win_rate:.2%}"
    }
