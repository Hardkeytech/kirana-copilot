# Shared Contract

Both of you code against these exact shapes. Don't change field names
without telling the other person — this is the only thing that lets you
work in parallel without talking all night.

## Transaction (one row of transactions.csv, as a dict)

```json
{
  "transaction_id": "TXN0042",
  "timestamp": "2026-09-29T14:32:00",
  "counterparty": "Ramesh Kumar",
  "amount": 450.0,
  "direction": "received",
  "channel": "sms",
  "utr": "310928471234",
  "raw_text": "Rs 450 credited to your a/c via UPI. UTR 310928471234"
}
```

- `direction`: "received" or "sent"
- `channel`: "sms" | "screenshot" | "soundbox"
- `utr`: 12-digit UPI reference number, may be missing/fake for fraud rows
- `raw_text`: what the merchant forwarded — this is what fraud_rules.py
  and llm_qa.py actually reason over

## FraudCheckResult (what fraud_rules.py returns)

```json
{
  "transaction_id": "TXN0042",
  "flagged": true,
  "reason": "UTR does not match any real transaction in the last 24 hours",
  "confidence": 0.87
}
```

`reason` must be a single plain-language sentence — this is what gets
shown to the merchant, so no jargon, no "anomaly score: 0.87" as the
user-facing text.

## ForecastResult (what forecast.py returns)

```json
{
  "projected_income_next_week": 18400.0,
  "trend_pct": 12.0,
  "note": "Tuesdays are your best days — stock up before then."
}
```

## QAResult (what llm_qa.py returns)

```json
{
  "question": "How was my week?",
  "answer": "You earned Rs 18,400 this week, up 12%. Tuesdays are your best days.",
  "language": "en"
}
```

`language`: "en" | "hi" | "ta" — Person A uses this to pick which chat
bubble style/font note to show, doesn't need to do any translation itself.

## Fraud rules to implement (Person B, Hour 1–3)

Implement these as separate checks inside `check_transaction()`, and flag
if ANY of them trip:

1. **UTR mismatch** — no transaction with this UTR exists in the last 24
   hours of the merchant's real transaction log (for the demo: compare
   against `data/transactions.csv`).
2. **Timestamp implausibility** — the screenshot's claimed time is in the
   future, or more than 10 minutes before the message was forwarded.
3. **Duplicate reuse** — the same UTR appears more than once in the
   merchant's log (a reused old screenshot).
4. **Amount round-tripping** — an unusually round amount (e.g. exactly
   ₹5000.00) combined with a new/unfamiliar counterparty name — a soft
   signal, lower confidence than the others.

Each rule that trips should produce its own plain-language reason string;
if multiple trip, join them with "; ".
