"""
Generates a synthetic UPI transaction history for one merchant so the
whole team has consistent fake data to build and demo against.

Run: python generate_data.py
Output: data/transactions.csv
"""

import csv
import random
from datetime import datetime, timedelta

random.seed(42)  # same output every run — keep the demo reproducible

MERCHANT_NAME = "Sharma Kirana Store"
NUM_ROWS = 140
NUM_FRAUD_ROWS = 6  # planted, obviously-off rows for the fraud demo
START_DATE = datetime(2026, 9, 1)

FIRST_NAMES = ["Ramesh", "Priya", "Arjun", "Divya", "Karthik", "Meena",
               "Suresh", "Lakshmi", "Vijay", "Anitha", "Rahul", "Sneha"]
LAST_NAMES = ["Kumar", "Nair", "Reddy", "Iyer", "Raman", "Pillai", "Sharma"]


def random_name():
    return f"{random.choice(FIRST_NAMES)} {random.choice(LAST_NAMES)}"


def random_utr():
    return "".join(str(random.randint(0, 9)) for _ in range(12))


def make_legit_row(idx, day_offset):
    ts = START_DATE + timedelta(days=day_offset,
                                 hours=random.randint(8, 21),
                                 minutes=random.randint(0, 59))
    return {
        "transaction_id": f"TXN{idx:04d}",
        "timestamp": ts.isoformat(),
        "counterparty": random_name(),
        "amount": round(random.uniform(20, 1500), 2),
        "direction": "received",
        "channel": random.choice(["sms", "soundbox"]),
        "utr": random_utr(),
        "raw_text": "",  # filled below
    }


def make_fraud_row(idx, day_offset, real_utrs):
    """A row designed to trip the fraud rules in CONTRACT.md."""
    ts = START_DATE + timedelta(days=day_offset,
                                 hours=random.randint(8, 21),
                                 minutes=random.randint(0, 59))
    kind = random.choice(["bad_utr", "future_time", "reused_utr", "round_amount"])

    if kind == "bad_utr":
        utr = random_utr()  # won't match anything real
        amount = round(random.uniform(200, 2000), 2)
    elif kind == "future_time":
        ts = ts + timedelta(days=2)  # claims a time in the future
        utr = random_utr()
        amount = round(random.uniform(200, 2000), 2)
    elif kind == "reused_utr":
        utr = random.choice(real_utrs) if real_utrs else random_utr()
        amount = round(random.uniform(200, 2000), 2)
    else:  # round_amount
        utr = random_utr()
        amount = 5000.00

    return {
        "transaction_id": f"TXN{idx:04d}",
        "timestamp": ts.isoformat(),
        "counterparty": random_name(),
        "amount": amount,
        "direction": "received",
        "channel": "screenshot",
        "utr": utr,
        "raw_text": "",
        "_seeded_fraud_kind": kind,  # for your own reference, not in CONTRACT.md
    }


def build_raw_text(row):
    return (f"Rs {row['amount']:.0f} credited to your a/c via UPI. "
            f"UTR {row['utr']}. From {row['counterparty']}.")


def main():
    rows = []
    real_utrs = []

    for i in range(1, NUM_ROWS - NUM_FRAUD_ROWS + 1):
        day_offset = random.randint(0, 27)  # spread over ~4 weeks
        row = make_legit_row(i, day_offset)
        row["raw_text"] = build_raw_text(row)
        rows.append(row)
        real_utrs.append(row["utr"])

    for j in range(NUM_FRAUD_ROWS):
        idx = NUM_ROWS - NUM_FRAUD_ROWS + j + 1
        day_offset = random.randint(20, 27)  # cluster fraud rows in the recent week
        row = make_fraud_row(idx, day_offset, real_utrs)
        row["raw_text"] = build_raw_text(row)
        rows.append(row)

    rows.sort(key=lambda r: r["timestamp"])

    fieldnames = ["transaction_id", "timestamp", "counterparty", "amount",
                  "direction", "channel", "utr", "raw_text"]

    import os
    os.makedirs("data", exist_ok=True)
    with open("data/transactions.csv", "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)

    print(f"Wrote {len(rows)} rows to data/transactions.csv "
          f"({NUM_FRAUD_ROWS} seeded as fraud) for {MERCHANT_NAME}")


if __name__ == "__main__":
    main()

# TODO(vibe): ask your AI assistant to add a --seed and --rows CLI flag
# if you want to regenerate different-sized datasets during the night.
