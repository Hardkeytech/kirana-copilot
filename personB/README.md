# Person B — Logic + LLM

You touch only files in this folder. Read `../CONTRACT.md` first — the
fraud rules to implement are listed there.

## Setup
```bash
cd personB
python -m venv venv
source venv/bin/activate   # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

You don't need Person A's Streamlit app to test any of this. Every module
has a matching `test_*.py` you run standalone from the command line.

## Order of work

1. **`fraud_rules.py`** — implement `check_transaction()` using the 4
   rules in CONTRACT.md. Test with:
   ```bash
   python test_fraud.py
   ```
   (It generates its own tiny fake dataset, no need to wait for Person A's
   `transactions.csv` — though once they push it, point `test_fraud.py` at
   the real file for a better sanity check.)

2. **`forecast.py`** — implement `forecast_next_week()`. A simple 7-day
   moving average projected forward is enough; don't overbuild this.
   Test with:
   ```bash
   python test_forecast.py
   ```

3. **`llm_qa.py`** — this is the one that needs an API key. Get a free key
   from **Groq** (fast, generous free tier, OpenAI-compatible) at
   console.groq.com, or swap in whichever free LLM API you already have
   access to. Set it as an environment variable so it's never committed:
   ```bash
   export GROQ_API_KEY=your_key_here      # Windows: set GROQ_API_KEY=...
   ```
   Test with:
   ```bash
   python test_qa.py
   ```
   If you don't have a key yet, `llm_qa.py` has an offline fallback so you
   can keep building — swap to the real API call as soon as the key
   arrives.

## At Hour 5 (integration)

Push your 3 files. Tell Person A to pull, copy `fraud_rules.py`,
`forecast.py`, `llm_qa.py` into their folder, and update their import
line. Sit with them for the first 15 minutes of integration — the CONTRACT
shapes should make it close to a drop-in, but real data always surfaces
one or two mismatches (e.g. a column name, a date format).

## If your LLM calls are slow or flaky during judging

Pre-compute the answers for your exact demo-script questions and cache
them in a dict at the top of `llm_qa.py` as a fast-path before it ever
calls the API. Never depend on live network latency during judging.
