# core/strategies/macd_strategy.py

# core/strategies/macd_crossover.py

import pandas as pd
from core.strategy_registry import register_strategy

@register_strategy
def macd_crossover(df: pd.DataFrame, atr_mult: float = 1.5, max_bars: int = 20):
    df = df.copy()
    df = df.sort_index()

    df['EMA12'] = df['Close'].ewm(span=12, adjust=False).mean()
    df['EMA26'] = df['Close'].ewm(span=26, adjust=False).mean()
    df['MACD'] = df['EMA12'] - df['EMA26']
    df['Signal'] = df['MACD'].ewm(span=9, adjust=False).mean()
    df['ATR'] = (df['High'] - df['Low']).rolling(window=14).mean()

    trades = []
    in_position = False
    bars_in_trade = 0
    direction = None

    for i in range(1, len(df)):
        row = df.iloc[i]
        prev = df.iloc[i - 1]

        # Long entry condition: MACD crosses above Signal, and MACD < 0
        if not in_position:
            if prev['MACD'] < prev['Signal'] and row['MACD'] > row['Signal'] and row['MACD'] < 0:
                entry_price = row['Close']
                atr = row['ATR']
                sl = entry_price - atr * atr_mult
                tp = entry_price + atr * atr_mult
                entry_time = df.index[i]
                reason = "MACD Bull Crossover"
                direction = 'long'
                in_position = True
                bars_in_trade = 0

            # Short entry condition: MACD crosses below Signal, and MACD > 0
            elif prev['MACD'] > prev['Signal'] and row['MACD'] < row['Signal'] and row['MACD'] > 0:
                entry_price = row['Close']
                atr = row['ATR']
                sl = entry_price + atr * atr_mult
                tp = entry_price - atr * atr_mult
                entry_time = df.index[i]
                reason = "MACD Bear Crossover"
                direction = 'short'
                in_position = True
                bars_in_trade = 0

        elif in_position:
            bars_in_trade += 1

            if direction == 'long':
                if row['Low'] <= sl:
                    trades.append({"Entry_Date": entry_time, "Entry_Price": entry_price, "SL": sl, "TP": tp,
                                   "Exit_Date": df.index[i], "Exit_Price": sl, "Result": "Loss", "Reason": reason})
                    in_position = False
                elif row['High'] >= tp:
                    trades.append({"Entry_Date": entry_time, "Entry_Price": entry_price, "SL": sl, "TP": tp,
                                   "Exit_Date": df.index[i], "Exit_Price": tp, "Result": "Win", "Reason": reason})
                    in_position = False

            elif direction == 'short':
                if row['High'] >= sl:
                    trades.append({"Entry_Date": entry_time, "Entry_Price": entry_price, "SL": sl, "TP": tp,
                                   "Exit_Date": df.index[i], "Exit_Price": sl, "Result": "Loss", "Reason": reason})
                    in_position = False
                elif row['Low'] <= tp:
                    trades.append({"Entry_Date": entry_time, "Entry_Price": entry_price, "SL": sl, "TP": tp,
                                   "Exit_Date": df.index[i], "Exit_Price": tp, "Result": "Win", "Reason": reason})
                    in_position = False

            if in_position and bars_in_trade >= max_bars:
                trades.append({"Entry_Date": entry_time, "Entry_Price": entry_price, "SL": sl, "TP": tp,
                               "Exit_Date": df.index[i], "Exit_Price": row['Close'], "Result": "Timeout", "Reason": reason})
                in_position = False

    return trades
