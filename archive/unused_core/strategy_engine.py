# core/strategy_engine.py

import pandas as pd
import numpy as np
import os
import matplotlib.pyplot as plt
from core.metrics import compute_fx_metrics


def run_strategy_on_ticker(df: pd.DataFrame, strategy_func, strategy_name: str,
                            atr_mult: float = 1.5, max_bars: int = 20) -> tuple[pd.DataFrame, dict]:
    df = df.copy()
    df.sort_index(inplace=True)

    trades = strategy_func(df, atr_mult=atr_mult, max_bars=max_bars)
    if not trades:
        print(f"[⚠️] No trades for {strategy_name}")
        return pd.DataFrame(), {}

    results_df = pd.DataFrame(trades)
    results_df['PnL'] = (results_df['Exit_Price'] - results_df['Entry_Price']) * 10000  # in pips
    results_df['Result'] = results_df['PnL'].apply(lambda x: 'Win' if x > 0 else 'Loss' if x < 0 else 'Timeout')

    metrics = compute_fx_metrics(results_df)

    return results_df, metrics


def plot_equity_curve(results_df: pd.DataFrame, strategy_name: str, output_path: str = None):
    equity = results_df['PnL'].cumsum()
    fig, ax = plt.subplots(figsize=(8, 4))
    ax.plot(equity, color='dodgerblue', linewidth=2)
    ax.set_title(f'Equity Curve – {strategy_name}')
    ax.set_ylabel('Cumulative PnL (Pips)')
    ax.set_xlabel('Trade Index')
    ax.grid(True)

    if output_path:
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        plt.tight_layout()
        fig.savefig(output_path)
        print(f"[📈] Saved equity curve: {output_path}")

    plt.close(fig)
    return fig
