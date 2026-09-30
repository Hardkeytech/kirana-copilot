"""
Run standalone: python test_fraud.py
No dependency on Person A's app or dataset — builds its own tiny fake
history so you can iterate on fraud_rules.py fast.

Once Person A pushes data/transactions.csv, point HISTORY at that file
instead (see load_real_data() below) for a fuller sanity check.
"""

from fraud_rules import check_transaction

HISTORY = [
    {"transaction_id": "TXN0001", "timestamp": "2026-09-29T10:00:00",
     "counterparty": "Ramesh Kumar", "amount": 450.0, "direction": "received",
     "channel": "sms", "utr": "111111111111"},
    {"transaction_id": "TXN0002", "timestamp": "2026-09-29T11:00:00",
     "counterparty": "Priya Nair", "amount": 220.0, "direction": "received",
     "channel": "soundbox", "utr": "222222222222"},
]

TEST_CASES = [
    {
        "name": "legit screenshot, UTR matches history",
        "transaction": {"transaction_id": "TXN0003", "timestamp": "2026-09-29T12:00:00",
                         "counterparty": "Ramesh Kumar", "amount": 450.0,
                         "direction": "received", "channel": "screenshot",
                         "utr": "111111111111"},
        "expect_flagged": False,
    },
    {
        "name": "fake screenshot, UTR not in history",
        "transaction": {"transaction_id": "TXN0004", "timestamp": "2026-09-29T13:00:00",
                         "counterparty": "Unknown Person", "amount": 900.0,
                         "direction": "received", "channel": "screenshot",
                         "utr": "999999999999"},
        "expect_flagged": True,
    },
]


def load_real_data(path="../personA/data/transactions.csv"):
    import pandas as pd
    return pd.read_csv(path).to_dict("records")


def main():
    print("--- Running fraud_rules.check_transaction() against test cases ---\n")
    passed = 0
    for case in TEST_CASES:
        result = check_transaction(case["transaction"], HISTORY)
        ok = result["flagged"] == case["expect_flagged"]
        status = "PASS" if ok else "FAIL"
        passed += ok
        print(f"[{status}] {case['name']}")
        print(f"       -> flagged={result['flagged']}, reason={result['reason']!r}\n")

    print(f"{passed}/{len(TEST_CASES)} test cases passed")

    # TODO(vibe): once rules 2-4 are implemented, add test cases here for
    # future timestamps, reused UTRs, and round-amount+new-counterparty.


if __name__ == "__main__":
    main()
