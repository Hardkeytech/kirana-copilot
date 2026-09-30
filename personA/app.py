"""
Kirana Copilot — demo chat UI, styled to look like a WhatsApp thread.

Run:  streamlit run app.py

Hour-5 integration: Person B's real modules are already imported inside the
three small wrappers at the top. To swap the stubs for the real ones:
  1. change the 3 import lines below,
  2. in fraud_wrapper() delete the one comment-marked line that passes history.
Everything else in the UI stays untouched.
"""

import inspect
from datetime import datetime

import pandas as pd
import streamlit as st

from backend_stub import fraud_check, get_forecast, answer_question
from extract import extract_transaction_from_image

# --- Hour-5 swap: replace these 3 lines with Person B's real modules ---
# from fraud_rules import check_transaction as _fraud_check
# from forecast import forecast_next_week as _get_forecast
# from llm_qa import answer_question as _answer_question
_fraud_check = fraud_check
_get_forecast = get_forecast
_answer_question = answer_question


# ---------- one small wrapper per backend function ----------
def fraud_wrapper(transaction: dict) -> dict:
    """Stub fraud_check(transaction) vs B's check_transaction(transaction, history)."""
    if _fraud_check.__name__ == "check_transaction":
        return _fraud_check(transaction, load_transactions().to_dict("records"))
    return _fraud_check(transaction)


def forecast_wrapper(df: pd.DataFrame) -> dict:
    return _get_forecast(df)


def qa_wrapper(question: str, df: pd.DataFrame, language: str = "en") -> dict:
    """Pass language through only if the backend function accepts it."""
    params = inspect.signature(_answer_question).parameters
    if "language" in params or any(p.kind == inspect.Parameter.VAR_KEYWORD
                                   for p in params.values()):
        return _answer_question(question, df, language=language)
    return _answer_question(question, df)


# ---------- load data ----------
@st.cache_data
def load_transactions() -> pd.DataFrame:
    return pd.read_csv("data/transactions.csv", dtype={"utr": str})


df = load_transactions()


def pick_rows(df: pd.DataFrame):
    """Pick the two scripted demo rows so each verdict is genuinely earned.

    LEGIT_ROW: screenshot-channel row whose UTR exists on a real
    (sms/soundbox) row — so the pass is actually verified.
    FRAUD_ROW: screenshot-channel row whose UTR matches nothing — so the
    flag is guaranteed. (Protects the demo's single most important moment.)
    """
    shots = df[df["channel"] == "screenshot"]
    real_utrs = set(df.loc[df["channel"] != "screenshot", "utr"])

    legit = shots[shots["utr"].isin(real_utrs)]
    if legit.empty:
        legit = shots  # last-resort fallback, should not happen
    legit_row = legit.iloc[0].to_dict()

    fraud = shots[~shots["utr"].isin(real_utrs)]
    if not fraud.empty:
        fraud_row = fraud.loc[fraud["amount"].idxmax()].to_dict()
    else:
        fraud_row = shots.iloc[-1].to_dict()
    return legit_row, fraud_row


LEGIT_ROW, FRAUD_ROW = pick_rows(df)

# ---------- chat state ----------
if "messages" not in st.session_state:
    st.session_state.messages = [{
        "role": "bot",
        "text": "Hi! I'm Kirana Copilot. Forward a payment screenshot or ask "
                "me about your business anytime.",
        "ts": datetime.now().strftime("%H:%M"),
    }]


def add_message(role, text, verdict=None):
    st.session_state.messages.append({
        "role": role,
        "text": text,
        "verdict": verdict,  # None | "flagged" | "verified"
        "ts": datetime.now().strftime("%H:%M"),
    })


def verdict_message(result):
    verdict = "flagged" if result["flagged"] else "verified"
    icon = "\u26A0\uFE0F" if result["flagged"] else "\u2705"
    add_message("bot", f"{icon} {result['reason']}", verdict=verdict)


def forward_row(row):
    add_message("user", f"[Forwarded screenshot: Rs {row['amount']:.0f} "
                        f"payment received]")
    verdict_message(fraud_wrapper(row))


# ---------- sidebar ----------
with st.sidebar:
    st.subheader("Kirana Copilot")
    st.caption("Sharma Kirana Store")
    st.markdown("### Demo mode")
    st.success("Scripted demo — works offline, zero typing", icon="🎬")
    st.markdown("### Reply language")
    language = st.selectbox(
        "Q&A language", ["en", "hi", "ta"],
        format_func={"en": "English", "hi": "हिन्दी", "ta": "தமிழ்"}.get,
        label_visibility="collapsed",
    )
    st.markdown("### Or upload a real screenshot")
    st.caption("No API key set? A demo transaction is used — the demo never "
               "depends on live internet.")
    upload = st.file_uploader("Payment screenshot", type=["png", "jpg", "jpeg"],
                              label_visibility="collapsed")

if upload is not None:
    add_message("user", f"[Forwarded screenshot: {upload.name}]")
    transaction = extract_transaction_from_image(upload.getvalue())
    verdict_message(fraud_wrapper(transaction))
    st.session_state.uploaded = None
    st.rerun()

# ---------- WhatsApp look: theme is also pinned in .streamlit/config.toml,
# this CSS keeps every bubble's text dark and readable in any mode ----------
st.markdown(
    """
    <style>
      /* Main app + chat background: WhatsApp beige */
      .stApp, [data-testid="stMain"] { background:#ECE5DD; }
      section[data-testid="stSidebar"] { background:#FFFFFF; }

      /* Force dark, readable text on every bubble */
      .wa-msg, .wa-msg * { color:#111b21 !important; }

      /* Chat buttons: WhatsApp-green, always readable */
      .wa-thread + div .stButton > button,
      div[data-testid="stHorizontalBlock"] .stButton > button {
        background:#25D366 !important; color:#062e16 !important;
        border:none !important; border-radius:20px !important;
        font-weight:600 !important; padding:8px 10px !important;
      }
      div[data-testid="stHorizontalBlock"] .stButton > button:hover {
        background:#1fb857 !important; color:#062e16 !important;
      }

      /* Hide Streamlit chrome so it feels like one chat window */
      #MainMenu, header[data-testid="stHeader"], [data-testid="stToolbar"] {
        visibility:hidden; height:0rem;
      }
    </style>
    """,
    unsafe_allow_html=True,
)

# ---------- header (styled like a WhatsApp chat header) ----------
st.markdown(
    """
    <div style="background:#075E54;padding:14px 18px;border-radius:8px 8px 0 0;">
      <span style="color:#ffffff;font-size:20px;font-weight:600;">💬 Kirana Copilot</span>
      <div style="color:#cfe9e4;font-size:12px;">Sharma Kirana Store
        &nbsp;•&nbsp; <span style="color:#a5f2c8;">● online</span></div>
    </div>
    """,
    unsafe_allow_html=True,
)

# ---------- message bubbles ----------
chat_box = st.container()
with chat_box:
    for m in st.session_state.messages:
        is_bot = m["role"] == "bot"
        verdict = m.get("verdict")
        if is_bot and verdict == "flagged":
            bg, border = "#FDE2E1", "#E53935"      # red warning bubble
        elif is_bot and verdict == "verified":
            bg, border = "#E3F6E5", "#2E7D32"      # green verified bubble
        elif is_bot:
            bg, border = "#DCF8C6", "none"         # bot reply bubble
        else:
            bg, border = "#FFFFFF", "none"         # merchant bubble
        align = "flex-start" if is_bot else "flex-end"
        radius = "0 14px 14px 14px" if is_bot else "14px 14px 0 14px"
        st.markdown(
            f"""
            <div style="display:flex;justify-content:{align};margin:6px 0;">
              <div class="wa-msg" style="background:{bg};border:1px solid {border};
                          color:#111b21;padding:9px 13px 5px;border-radius:{radius};
                          max-width:78%;font-size:15px;line-height:1.5;
                          box-shadow:0 1px 1px rgba(0,0,0,.12);">
                {m['text']}
                <div style="text-align:right;font-size:10px;color:#7a8f88;
                            margin-top:4px;">{m['ts']} {'✓✓' if not is_bot else ''}</div>
              </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

# ---------- scripted demo actions (live inside the chat box, so buttons
# render above the chart and st.rerun keeps the thread on top) ----------
c1, c2 = st.columns(2)
with c1:
    if st.button("📸 Forward fraud screenshot", use_container_width=True):
        forward_row(FRAUD_ROW)
        st.rerun()
with c2:
    if st.button("📸 Forward legit screenshot", use_container_width=True):
        forward_row(LEGIT_ROW)
        st.rerun()

c3, c4 = st.columns(2)
with c3:
    if st.button("📊 Ask: How was my week?", use_container_width=True):
        add_message("user", "How was my week?")
        add_message("bot", qa_wrapper("How was my week?", df, language)["answer"])
        st.rerun()
with c4:
    if st.button("🎙️ Ask in Hindi", use_container_width=True):
        question = "मेरी दुकान कैसी चल रही है?"
        add_message("user", f"{question} (voice note)")
        add_message("bot", qa_wrapper(question, df, language)["answer"])
        st.rerun()

# ---------- free-text input, backup beyond the scripted demo ----------
user_q = st.chat_input("Type a question (backup — avoid live during judging)...")
if user_q:
    add_message("user", user_q)
    add_message("bot", qa_wrapper(user_q, df, language)["answer"])
    st.rerun()

# ---------- cash-flow: daily received totals + forecast summary ----------
st.markdown("---")
forecast = forecast_wrapper(df)

received = df[df["direction"] == "received"].copy()
received["day"] = pd.to_datetime(received["timestamp"], errors="coerce").dt.strftime("%m-%d")
daily = (received.dropna(subset=["day"])
         .groupby("day", as_index=False)["amount"].sum()
         .set_index("day"))

st.subheader("Cash flow")
st.caption(f"Projected income next week: Rs {forecast['projected_income_next_week']:,.0f}"
           f" ({forecast['trend_pct']:+.0f}% vs this week)")
st.bar_chart(daily, height=220)
st.caption(f"💡 {forecast['note']}")
