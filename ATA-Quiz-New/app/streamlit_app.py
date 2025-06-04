# streamlit_app.py
import json
import random
import pathlib
import streamlit as st

# --------------------------------------------------
# Grund­einstellungen
# --------------------------------------------------
st.set_page_config(
    page_title="ATA-Quiz",
    page_icon="🩺",
    layout="wide"
)

DATA_PATH = pathlib.Path("questions")       # dort liegen ksX_questions_detailed.json
KS_ORDER  = [1, 2, 3, 4, 5, 6, 7, 8]
NUM_QUEST = 15                              # Fragen pro Durchgang

# --------------------------------------------------
# Hilfsfunktionen
# --------------------------------------------------
@st.cache_data
def load_questions(ks_no: int):
    file = DATA_PATH / f"ks{ks_no}_questions_detailed.json"
    with open(file, encoding="utf-8") as f:
        return json.load(f)

def init_state():
    st.session_state.setdefault("state_ready", False)
    st.session_state.setdefault("ks", None)
    st.session_state.setdefault("q_set", [])
    st.session_state.setdefault("q_idx", 0)
    st.session_state.setdefault("score", 0)
    st.session_state.setdefault("show_result", False)
    st.session_state.setdefault("chosen_idx", None)
    st.session_state.setdefault("is_correct", None)

def start_quiz(ks_no: int):
    qs = load_questions(ks_no)
    random.shuffle(qs)
    st.session_state.update(
        state_ready=True,
        ks=ks_no,
        q_set=qs[:NUM_QUEST],
        q_idx=0,
        score=0,
        show_result=False,
        chosen_idx=None,
        is_correct=None,
    )

# --------------------------------------------------
# UI-Logik
# --------------------------------------------------
init_state()
st.title("🩺 ATA-Quiz")

if not st.session_state.state_ready:
    st.subheader("Kompetenz­schwerpunkt wählen")
    cols = st.columns(len(KS_ORDER))
    for i, ks_no in enumerate(KS_ORDER):
        if cols[i].button(f"KS {ks_no}"):
            start_quiz(ks_no)
    st.stop()

# --------------------------------------------------
# Quiz-Durchgang
# --------------------------------------------------
q = st.session_state.q_set[st.session_state.q_idx]
st.markdown(f"### Frage {st.session_state.q_idx + 1} / {NUM_QUEST}")
st.write(q["question"])

# Antwort-Buttons
for idx, option in enumerate(q["options"]):
    if st.button(option, key=f"opt{idx}", disabled=st.session_state.show_result):
        st.session_state.chosen_idx = idx
        st.session_state.is_correct = (idx == q["answer"])
        if st.session_state.is_correct:
            st.session_state.score += 1
        st.session_state.show_result = True

# Ergebnis- und Erklärungsanzeige
if st.session_state.show_result:
    chosen = st.session_state.chosen_idx
    correct_idx = q["answer"]
    correct_text = q["options"][correct_idx]

    if st.session_state.is_correct:
        st.success("✅ Richtig!")
    else:
        st.error(f"❌ Falsch – korrekt: **{correct_text}**")

    # Ausführliche Erklärung aus JSON
    st.info(q.get("answer_explanation", "Keine ausführliche Erklärung hinterlegt."))

    if st.button("Nächste Frage"):
        st.session_state.q_idx += 1
        if st.session_state.q_idx >= NUM_QUEST:
            st.session_state.state_ready = False  # Quiz fertig
        st.session_state.show_result = False
        st.session_state.chosen_idx = None
        st.session_state.is_correct = None
        st.experimental_rerun()

# --------------------------------------------------
# Auswertung am Ende
# --------------------------------------------------
if not st.session_state.state_ready:
    st.success(f"Fertig! Punkte: {st.session_state.score} / {NUM_QUEST}")
    if st.button("🔄 Neuer Durchgang"):
        st.session_state.clear()   # Reset alles
        st.experimental_rerun()
