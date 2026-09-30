"""
Kirana Copilot — demo chat UI, styled to look like a WhatsApp thread.

Run: streamlit run app.py

Swap the import line below at the Hour 5 integration checkpoint:
    from backend_stub import fraud_check, get_forecast, answer_question
becomes:
    from fraud_rules import check_transaction as fraud_check
    from forecast import forecast_next_week as get_forecast
    from llm_qa import answer_question
"""

import streamlit as st
import pandas as pd

from backend_stub import fraud_check, get_forecast, answer_question

st.set_page_config(page_title="Kirana Copilot", page_icon="\U0001F4B0", layout="centered")

# ---------- load data ----------
@st.cache_data
def load_transactions():
    return pd.read_csv("data/transactions.csv")

df = load_transactions()

# Pick two rows to use as the scripted demo screenshots.
FRAUD_ROW = df[df["channel"] == "screenshot"].iloc[-1].to_dict() if (df["channel"] == "screenshot").any() else df.iloc[-1].to_dict()
LEGIT_ROW = df[df["channel"] != "screenshot"].iloc[-1].to_dict()

# ---------- chat state ----------
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "bot", "text": "Hi! I'm Kirana Copilot. Forward a payment screenshot or ask me about your business anytime."}
    ]

def add_message(role, text, warning=False):
    st.session_state.messages.append({"role": role, "text": text, "warning": warning})

# ---------- header (styled like a WhatsApp chat header) ----------
st.markdown(
    """
    <div style="background:#075E54;padding:14px 18px;border-radius:8px 8px 0 0;">
      <span style="color:white;font-size:20px;font-weight:600;">\U0001F4AC Kirana Copilot</span>
      <div style="color:#cfe9e4;font-size:12px;">Sharma Kirana Store</div>
    </div>
    """,
    unsafe_allow_html=True,
)

# ---------- message bubbles ----------
chat_box = st.container()
with chat_box:
    for m in st.session_state.messages:
        is_bot = m["role"] == "bot"
        bg = "#FFFFFF" if not is_bot else ("#FDECEA" if m.get("warning") else "#DCF8C6")
        align = "flex-end" if not is_bot else "flex-start"
        st.markdown(
            f"""
            <div style="display:flex;justify-content:{align};margin:6px 0;">
              <div style="background:{bg};padding:10px 14px;border-radius:10px;
                          max-width:75%;font-size:14px;">
                {m['text']}
              </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

st.markdown("---")

# ---------- scripted demo actions ----------
st.caption("Demo actions (use these during judging instead of live typing):")
c1, c2 = st.columns(2)

with c1:
    if st.button("\U0001F4F7 Forward Screenshot #2 (fraud)"):
        add_message("user", f"[Forwarded screenshot: Rs {FRAUD_ROW['amount']:.0f} payment received]")
        result = fraud_check(FRAUD_ROW)
        if result["flagged"]:
            add_message("bot", f"\u26A0\uFE0F {result['reason']}", warning=True)
        else:
            add_message("bot", f"\u2705 {result['reason']}")
        st.rerun()

with c2:
    if st.button("\U0001F4F7 Forward Screenshot #1 (legit)"):
        add_message("user", f"[Forwarded screenshot: Rs {LEGIT_ROW['amount']:.0f} payment received]")
        result = fraud_check(LEGIT_ROW)
        if result["flagged"]:
            add_message("bot", f"\u26A0\uFE0F {result['reason']}", warning=True)
        else:
            add_message("bot", f"\u2705 {result['reason']}")
        st.rerun()

c3, c4 = st.columns(2)
with c3:
    if st.button("\U0001F4C8 Ask: How was my week?"):
        add_message("user", "How was my week?")
        result = answer_question("How was my week?", df)
        add_message("bot", result["answer"])
        st.rerun()

with c4:
    if st.button("\U0001F1EE\U0001F1F3 Ask in Hindi"):
        question = "\u092e\u0947\u0930\u0940 \u0926\u0941\u0915\u093e\u0928 \u0915\u0948\u0938\u0940 \u091a\u0932 \u0930\u0939\u0940 \u0939\u0948?"
        add_message("user", f"{question} (voice note)")
        result = answer_question(question, df)
        add_message("bot", result["answer"])
        st.rerun()

# ---------- free-text input, for anything beyond the scripted demo ----------
user_q = st.chat_input("Type a question (backup, avoid live during judging)...")
if user_q:
    add_message("user", user_q)
    result = answer_question(user_q, df)
    add_message("bot", result["answer"])
    st.rerun()

# TODO(vibe): ask your AI assistant to add a small forecast chart below
# the chat using get_forecast(df) and st.line_chart or st.bar_chart.
