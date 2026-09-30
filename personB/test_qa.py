"""
Run standalone: python test_qa.py
Works with or without GROQ_API_KEY set (falls back to offline responder).
"""

import os
import pandas as pd
from llm_qa import answer_question

REAL_DATA_PATH = "../personA/data/transactions.csv"


def make_fake_df():
    import random
    from datetime import datetime, timedelta
    random.seed(1)
    rows = []
    start = datetime(2026, 9, 1)
    for i in range(20):
        ts = start + timedelta(days=random.randint(0, 27), hours=random.randint(8, 20))
        rows.append({
            "transaction_id": f"TXN{i:04d}",
            "timestamp": ts.isoformat(),
            "amount": round(random.uniform(50, 1200), 2),
            "direction": "received",
            "counterparty": "Test Customer",
        })
    return pd.DataFrame(rows)


def main():
    if os.path.exists(REAL_DATA_PATH):
        df = pd.read_csv(REAL_DATA_PATH)
    else:
        print("Real data not found yet — using synthetic fallback")
        df = make_fake_df()

    if not os.environ.get("GROQ_API_KEY"):
        print("(No GROQ_API_KEY set — testing offline fallback path)\n")

    questions = [
        "How was my week?",
        "Which days were slow?",
    ]
    for q in questions:
        result = answer_question(q, df)
        print(f"Q: {q}")
        print(f"A: {result['answer']}")
        print(f"   language={result['language']}\n")


if __name__ == "__main__":
    main()
