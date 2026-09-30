"""
Cash-flow forecasting. Keep this simple — a moving average or basic trend
line is completely legitimate to call "AI-powered forecasting" in a demo;
don't burn hours here.

Returns the ForecastResult shape from CONTRACT.md.
"""

import pandas as pd


def forecast_next_week(df: pd.DataFrame) -> dict:
    """
    df: the transactions dataframe (from transactions.csv), with columns
        including 'timestamp', 'amount', 'direction'.

    # TODO(vibe): this has a basic 7-day trailing average implemented.
    # Ask your AI assistant to: (1) also compute which weekday has the
    # highest average income and put it in `note`, (2) handle the case
    # where df has fewer than 14 rows gracefully.
    """
    df = df.copy()
    df["timestamp"] = pd.to_datetime(df["timestamp"])
    received = df[df["direction"] == "received"]

    if received.empty:
        return {
            "projected_income_next_week": 0.0,
            "trend_pct": 0.0,
            "note": "Not enough data yet.",
        }

    received = received.sort_values("timestamp")
    latest_date = received["timestamp"].max()

    last_7 = received[received["timestamp"] > latest_date - pd.Timedelta(days=7)]
    prev_7 = received[
        (received["timestamp"] <= latest_date - pd.Timedelta(days=7)) &
        (received["timestamp"] > latest_date - pd.Timedelta(days=14))
    ]

    this_week_total = float(last_7["amount"].sum())
    prev_week_total = float(prev_7["amount"].sum())

    if prev_week_total > 0:
        trend_pct = round(((this_week_total - prev_week_total) / prev_week_total) * 100, 1)
    else:
        trend_pct = 0.0

    # TODO(vibe): replace this static note with the best/worst weekday
    # computed from `received.groupby(received['timestamp'].dt.day_name())`.
    note = "Tuesdays are your best days — stock up before then."

    return {
        "projected_income_next_week": round(this_week_total, 2),
        "trend_pct": trend_pct,
        "note": note,
    }
