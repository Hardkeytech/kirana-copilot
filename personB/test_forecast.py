"""
Run standalone: python test_forecast.py
Once Person A pushes data/transactions.csv, this will use the real file;
until then it builds a small synthetic one so you're not blocked.
"""

import os
import pandas as pd
from forecast import forecast_next_week

REAL_DATA_PATH = "../personA/data/transactions.csv"


def make_fake_df():
    import random
    from datetime import datetime, timedelta
    random.seed(1)
    rows = []
    start = datetime(2026, 9, 1)
    for i in range(40):
        ts = start + timedelta(days=random.randint(0, 27), hours=random.randint(8, 20))
        rows.append({
            "transaction_id": f"TXN{i:04d}",
            "timestamp": ts.isoformat(),
            "amount": round(random.uniform(50, 1200), 2),
            "direction": "received",
            "channel": "sms",
        })
    return pd.DataFrame(rows)


def main():
    if os.path.exists(REAL_DATA_PATH):
        print(f"Using real data from {REAL_DATA_PATH}")
        df = pd.read_csv(REAL_DATA_PATH)
    else:
        print("Real data not found yet — using synthetic fallback")
        df = make_fake_df()

    result = forecast_next_week(df)
    print("\nForecastResult:")
    for k, v in result.items():
        print(f"  {k}: {v}")


if __name__ == "__main__":
    main()
