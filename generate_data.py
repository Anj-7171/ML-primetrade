import pandas as pd
import numpy as np

def generate_ohlcv(num_rows=10000, seed=42):
    np.random.seed(seed)
    # Generate some random price data
    base_price = 100.0
    price_changes = np.random.normal(loc=0.0005, scale=0.01, size=num_rows)
    close_prices = base_price * np.exp(np.cumsum(price_changes))
    
    # Generate OHLCV based on close
    highs = close_prices * (1 + np.abs(np.random.normal(loc=0.005, scale=0.005, size=num_rows)))
    lows = close_prices * (1 - np.abs(np.random.normal(loc=0.005, scale=0.005, size=num_rows)))
    opens = close_prices * (1 + np.random.normal(loc=0.0, scale=0.002, size=num_rows))
    volumes = np.random.lognormal(mean=10, sigma=1, size=num_rows)
    
    df = pd.DataFrame({
        'open': opens,
        'high': highs,
        'low': lows,
        'close': close_prices,
        'volume': volumes
    })
    
    # ensure high >= max(open, close) and low <= min(open, close)
    df['high'] = df[['open', 'close', 'high']].max(axis=1)
    df['low'] = df[['open', 'close', 'low']].min(axis=1)
    
    df.to_csv('data.csv', index=False)
    print("Generated data.csv with {} rows".format(num_rows))

if __name__ == '__main__':
    generate_ohlcv()
