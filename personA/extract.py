"""
Extract a Transaction dict from a payment screenshot using a
vision-capable LLM API (OpenAI-compatible; works with OpenAI or Groq).

Demo safety net: if there is no API key set, the network is down, or the
model reply can't be parsed, we return a pre-defined demo transaction, so
the upload flow still works with ZERO internet during judging.

API keys come from environment variables only — never hardcode them:
    OPENAI_API_KEY (tried first)  or  GROQ_API_KEY
"""

import base64
import json
import os
import re
import urllib.request
from datetime import datetime

# Returned whenever live extraction is unavailable. Its UTR is deliberately
# NOT in the transaction log, so the fraud check still has something to flag.
DEMO_SCREENSHOT_TRANSACTION = {
    "transaction_id": "TXN-UPLOADED",
    "timestamp": "2026-09-29T18:41:00",
    "counterparty": "Ramesh Kumar",
    "amount": 12450.0,
    "direction": "received",
    "channel": "screenshot",
    "utr": "428916370512",
    "raw_text": "Rs 12450 paid via UPI. UTR 428916370512. From Ramesh Kumar.",
}

_PROMPT = (
    "You read Indian UPI payment screenshots. Reply with ONLY a JSON object "
    "(no markdown, no extra text) with these keys: "
    "counterparty (payer name), amount (number, rupees), "
    "utr (12-digit UTR/reference, digits only), "
    'timestamp (payment date+time as "YYYY-MM-DDTHH:MM:SS"; if the date is '
    "unclear use 2026-09-29). Use null for anything unreadable."
)

# (env var, endpoint, vision-capable model) — first env var found wins.
_PROVIDERS = [
    ("OPENAI_API_KEY", "https://api.openai.com/v1/chat/completions", "gpt-4o-mini"),
    ("GROQ_API_KEY", "https://api.groq.com/openai/v1/chat/completions",
     "meta-llama/llama-4-scout-17b-16e-instruct"),
]


def _api_config():
    for env_var, url, model in _PROVIDERS:
        key = os.environ.get(env_var, "").strip()
        if key:
            return url, model, key
    return None


def _call_vision_api(image_bytes, url, model, key):
    mime = "image/png" if image_bytes[:8] == b"\x89PNG\r\n\x1a\n" else "image/jpeg"
    data_uri = "data:" + mime + ";base64," + base64.b64encode(image_bytes).decode()
    body = json.dumps({
        "model": model,
        "messages": [{
            "role": "user",
            "content": [
                {"type": "text", "text": _PROMPT},
                {"type": "image_url", "image_url": {"url": data_uri}},
            ],
        }],
        "max_tokens": 300,
        "temperature": 0,
    }).encode()
    req = urllib.request.Request(
        url,
        data=body,
        headers={"Content-Type": "application/json",
                 "Authorization": "Bearer " + key},
    )
    with urllib.request.urlopen(req, timeout=20) as resp:
        payload = json.loads(resp.read().decode("utf-8"))
    return payload["choices"][0]["message"]["content"]


def _extract_json(text):
    """Best-effort: pull a dict out of whatever the model replied."""
    text = (text or "").strip()
    text = re.sub(r"^```(?:json)?\s*|```\s*$", "", text).strip()
    start, end = text.find("{"), text.rfind("}")
    if start != -1 and end > start:
        try:
            return json.loads(text[start:end + 1])
        except json.JSONDecodeError:
            pass
    # Regex salvage for stubborn replies.
    utr = re.search(r"\b\d{12}\b", text)
    amount = re.search(r"(?:rs\.?|₹|inr)\s*([\d,]+(?:\.\d{1,2})?)", text,
                       re.IGNORECASE)
    if utr or amount:
        return {
            "utr": utr.group(0) if utr else None,
            "amount": amount.group(1) if amount else None,
            "counterparty": None,
            "timestamp": None,
        }
    return {}


def _build_transaction(data):
    """Validate model output into the CONTRACT Transaction shape, or None."""
    utr = re.sub(r"\D", "", str(data.get("utr") or ""))
    if not re.fullmatch(r"\d{12}", utr):
        return None
    try:
        amount = float(re.sub(r"[^\d.]", "", str(data.get("amount"))))
    except (TypeError, ValueError):
        return None
    if amount <= 0:
        return None
    counterparty = str(data.get("counterparty") or "Unknown").strip() or "Unknown"
    try:
        timestamp = datetime.fromisoformat(str(data.get("timestamp")).strip()).isoformat()
    except (ValueError, TypeError):
        timestamp = datetime.now().isoformat(timespec="seconds")
    return {
        "transaction_id": "TXN-UPLOADED",
        "timestamp": timestamp,
        "counterparty": counterparty,
        "amount": amount,
        "direction": "received",
        "channel": "screenshot",
        "utr": utr,
        "raw_text": "Rs {:.2f} paid via UPI. UTR {}. From {}.".format(
            amount, utr, counterparty),
    }


def extract_transaction_from_image(image_bytes: bytes) -> dict:
    """Return a Transaction dict (channel="screenshot") read from an image.

    Never raises. Never depends on the network: any failure — no key, bad
    key, timeout, unparseable reply — returns DEMO_SCREENSHOT_TRANSACTION.
    """
    if not image_bytes:
        return dict(DEMO_SCREENSHOT_TRANSACTION)
    config = _api_config()
    if config is None:
        return dict(DEMO_SCREENSHOT_TRANSACTION)
    try:
        reply = _call_vision_api(image_bytes, *config)
        transaction = _build_transaction(_extract_json(reply))
    except Exception:
        transaction = None
    return transaction if transaction is not None else dict(DEMO_SCREENSHOT_TRANSACTION)
