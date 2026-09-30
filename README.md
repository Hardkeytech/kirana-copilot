# Kirana Copilot — Overnight Build

Two people, two machines, one repo. This file is the plan. Read CONTRACT.md
before writing any code — it's the one thing both of you must agree on
before splitting up.

## 0. Get the repo shared (do this together, first, 10 minutes)

1. One of you creates a new **private** GitHub repo, e.g. `kirana-copilot`.
2. Push this starter folder to it:
   ```bash
   cd kirana-starter
   git init
   git add .
   git commit -m "starter scaffold"
   git branch -M main
   git remote add origin <your-repo-url>
   git push -u origin main
   ```
3. The other person clones it:
   ```bash
   git clone <your-repo-url>
   cd kirana-copilot
   ```
4. **Working rule for the night:** Person A only edits files inside
   `personA/`. Person B only edits files inside `personB/`. Neither of you
   touches the other's folder until the integration checkpoint (Hour 5).
   This means you can `git pull` each other's work anytime without merge
   conflicts.
5. Commit and push every 30–45 minutes, even half-finished code. If your
   laptop dies, the repo is the backup.

## 1. The plan (start the clock now)

| Hour | Person A (frontend + data) | Person B (logic + LLM) |
|---|---|---|
| 0–1 | `generate_data.py` → produce `data/transactions.csv` | Read CONTRACT.md, stub out function signatures, no logic yet |
| 1–3 | Build `app.py` chat UI against `backend_stub.py` (fake JSON) | Write real `fraud_rules.py` + `forecast.py`, test standalone |
| 3–5 | Polish UI, add hardcoded Hindi/Tamil replies | Write `llm_qa.py`, test standalone with `test_qa.py` |
| **5–6** | **INTEGRATE** — copy B's 3 files into A's `app.py` imports, swap stub calls for real ones | Sit together for this hour, fix integration bugs |
| 6–7 | Lock exact demo inputs — nothing typed live during judging | Same |
| 7–8 | Rehearse demo twice, fix whatever breaks | Same |

Don't start integration early and don't skip it — Person A builds the UI
against **fake but correctly-shaped** JSON the whole time, so when B's real
functions drop in at Hour 5, nothing about the UI needs to change, only the
import line and the data going into it.

## 2. "Vibe coding" — how to use this with an AI coding assistant

Every file below has a `# TODO(vibe):` comment where you're expected to
paste it into Claude Code / Cursor / Copilot and ask it to extend that
specific function. Don't ask the AI to "build the whole app" — ask it to
fill one `TODO` at a time, run it, check it works, then move to the next
one. That's what keeps AI-generated code debuggable at 2am.

Suggested first prompt for Person A, after generating data:
> "Here's my transactions.csv and backend_stub.py. Build a Streamlit chat
> UI in app.py that looks like a WhatsApp thread: message bubbles, a text
> input at the bottom, and 2 buttons for 'forward screenshot #1 (fraud)'
> and 'forward screenshot #2 (legit)'. Use session_state for message
> history. Call the stub functions from backend_stub.py, don't write any
> fraud/forecast logic yourself."

Suggested first prompt for Person B:
> "Here's CONTRACT.md and my transactions.csv shape. Implement
> check_transaction() in fraud_rules.py using these rules: [list 3-4 rules
> from CONTRACT.md]. Return the exact JSON shape specified. Then write
> test_fraud.py that runs it against 5 sample transactions and prints
> results."

## 3. If you fall behind

Cut in this order, cheapest cuts first:
1. Drop the forecast chart — say the number out loud instead of plotting it.
2. Drop real LLM calls — hardcode 3 Q&A pairs for the exact questions in
   your demo script.
3. Drop Hindi/Tamil — do the whole demo in English, mention multilingual
   as "next step" verbally.
4. Never cut the fraud-flag moment — it's the single most impressive beat
   in the demo. Protect it above everything else.
