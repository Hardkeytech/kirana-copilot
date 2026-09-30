"""
Fraud detection rules. Pure functions, no UI, no I/O beyond what's passed
in — this is what makes it testable standalone and easy to vibe-code one
rule at a time.

Returns the FraudCheckResult shape from CONTRACT.md.
"""

from datetime import datetime, timedelta


def _parse_ts(ts_str: str) -> datetime:
    return datetime.fromisoformat(ts_str)


def _utr_exists_in_history(utr: str, history: list, exclude_id: str) -> bool:
    """True if this UTR appears on a non-screenshot (trusted) row in history."""
    for row in history:
        if row.get("transaction_id") == exclude_id:
            continue
        if row.get("utr") == utr and row.get("channel") in ("sms", "soundbox"):
            return True
    return False


def _utr_is_duplicate(utr: str, history: list, exclude_id: str) -> bool:
    count = sum(
        1 for row in history
        if row.get("utr") == utr and row.get("transaction_id") != exclude_id
    )
    return count >= 1


def check_transaction(transaction: dict, history: list) -> dict:
    """
    transaction: a single transaction dict, shape per CONTRACT.md.
    history: list of transaction dicts (e.g. df.to_dict("records")) —
             the merchant's existing, trusted log to check against.

    # TODO(vibe): this is scaffolded with rule 1 (UTR mismatch) fully
    # implemented as an example. Ask your AI assistant to implement rules
    # 2-4 from CONTRACT.md following the same pattern: check a condition,
    # append a reason string if it trips, and combine confidences.
    """
    reasons = []
    confidence = 0.0

    txn_id = transaction.get("transaction_id", "UNKNOWN")
    utr = transaction.get("utr", "")
    channel = transaction.get("channel", "")

    # Rule 1: UTR mismatch — only screenshot-channel claims need checking;
    # sms/soundbox are already trusted sources in this demo.
    if channel == "screenshot":
        if not _utr_exists_in_history(utr, history, txn_id):
            reasons.append(
                "This screenshot's UTR doesn't match any confirmed transaction "
                "in your history"
            )
            confidence = max(confidence, 0.85)

    # TODO(vibe): Rule 2 — timestamp implausibility.
    # Compare transaction['timestamp'] to "now" (or to when it was
    # forwarded, if you track that) and flag if it's in the future or
    # more than 10 minutes stale for a screenshot claim.

    # TODO(vibe): Rule 3 — duplicate reuse.
    # Use _utr_is_duplicate() above and add a reason if it trips.

    # TODO(vibe): Rule 4 — round-amount + unfamiliar counterparty (soft signal).
    # e.g. amount % 1000 == 0 and counterparty not seen elsewhere in history.
    # Lower confidence than rules 1-3 since it's a weaker signal alone.

    flagged = len(reasons) > 0
    reason_text = "; ".join(reasons) if reasons else (
        "Matches a confirmed credit in your transaction history."
    )

    return {
        "transaction_id": txn_id,
        "flagged": flagged,
        "reason": reason_text,
        "confidence": round(confidence, 2),
    }
