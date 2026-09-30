# Person A — Frontend + Data

You touch only files in this folder. Read `../CONTRACT.md` first.

## Setup
```bash
cd personA
python -m venv venv
source venv/bin/activate   # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

## Order of work
1. `python generate_data.py` — makes `data/transactions.csv`. Open it,
   check the fraud rows look plausible, adjust `NUM_ROWS` or
   `NUM_FRAUD_ROWS` in the script if you want more/fewer.
2. Open `backend_stub.py` — these are fake versions of Person B's
   functions, returning hardcoded JSON matching CONTRACT.md. Build your
   whole UI against these first.
3. Run the app:
   ```bash
   streamlit run app.py
   ```
4. Vibe-code the UI: paste `app.py` into your AI assistant and ask it to
   improve the chat bubble styling, add the fraud-flag warning color, etc.
   Keep re-running `streamlit run app.py` after each change.
5. At Hour 5 (integration): copy Person B's `fraud_rules.py`,
   `forecast.py`, `llm_qa.py` into this folder, then in `app.py` change:
   ```python
   from backend_stub import fraud_check, get_forecast, answer_question
   ```
   to:
   ```python
   from fraud_rules import check_transaction as fraud_check
   from forecast import forecast_next_week as get_forecast
   from llm_qa import answer_question
   ```
   Run it, fix whatever the real functions expect differently than the
   stub did (the CONTRACT.md shapes should make this a 5-minute fix, not
   a rewrite).

## Demo script — lock this before Hour 6

Write the exact sequence of buttons/questions you'll click during judging
here, so nothing is typed live:

1. Click "Forward Screenshot #2 (fraud)" → should show fraud warning
2. Click "Forward Screenshot #1 (legit)" → should log normally
3. Type "How was my week?" → should show forecast answer
4. Click "Ask in Hindi" preset button → should show Hindi reply
