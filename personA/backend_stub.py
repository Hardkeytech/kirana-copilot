"""
Fake versions of Person B's functions. Return JSON shaped exactly like
CONTRACT.md so the UI never has to change when the real ones are swapped
in at the integration checkpoint (Hour 5).

Build your whole app.py against these first. Don't wait for Person B.
"""


def fraud_check(transaction: dict) -> dict:
    """Stub: flags anything on the 'screenshot' channel as fraud, for demo purposes."""
    is_fraud = transaction.get("channel") == "screenshot" and transaction.get("amount", 0) >= 5000
    return {
        "transaction_id": transaction.get("transaction_id", "UNKNOWN"),
        "flagged": is_fraud,
        "reason": (
            "This screenshot's UTR doesn't match any real transaction in "
            "the last 24 hours. Ask the customer to pay again on your QR."
            if is_fraud else
            "Matches a confirmed credit in your transaction history."
        ),
        "confidence": 0.9 if is_fraud else 0.05,
    }


def get_forecast(df=None) -> dict:
    """Stub: hardcoded forecast, ignores the dataframe entirely."""
    return {
        "projected_income_next_week": 18400.0,
        "trend_pct": 12.0,
        "note": "Tuesdays are your best days — stock up before then.",
    }


def answer_question(question: str, df=None) -> dict:
    """Stub: canned answers for the exact questions in the demo script."""
    q = question.lower().strip()
    if "week" in q:
        answer = "You earned Rs 18,400 this week, up 12%. Tuesdays are your best days."
        lang = "en"
    elif "\u0926\u0941\u0915\u093e\u0928" in question:  # Hindi script present
        answer = "\u0906\u092a\u0915\u0940 \u0926\u0941\u0915\u093e\u0928 \u0905\u091a\u094d\u091b\u0940 \u091a\u0932 \u0930\u0939\u0940 \u0939\u0948\u0964 \u0907\u0938 \u0939\u092b\u094d\u0924\u0947 \u20b918,400 \u0915\u092e\u093e\u092f\u093e\u0964"
        lang = "hi"
    else:
        answer = "I'm still learning — try asking how your week or month went."
        lang = "en"
    return {"question": question, "answer": answer, "language": lang}


# TODO(vibe): once app.py works end-to-end with these stubs, ask your AI
# assistant: "add 2 more canned Q&A pairs to answer_question() covering
# 'which days were slow' and a Tamil-language question" so your demo has
# backup answers if judges ask something slightly different.
