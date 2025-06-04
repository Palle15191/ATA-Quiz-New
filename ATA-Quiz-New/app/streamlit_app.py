# streamlit_app.py
import json
import random
import pathlib
import streamlit as st

# --------------------------------------------------
# Grundeinstellungen
# --------------------------------------------------
st.set_page_config(page_title="ATA-Quiz", page_icon="🩺", layout="wide")
DATA_PATH = pathlib.Path("questions")        # Ordner mit ks1_questions_detailed.json usw.
KS_ORDER   = [1, 2, 3, 4, 5, 6, 7, 8]       # Reihenfolge der Kompetenzschwerpunkte
NUM_QUEST  = 15                             # Fragen pro Durchgang

# --------------------------------------------------
# Hilfsfunktionen
# --------------------------------------------------
@st.cache_data
def load_questions(ks_no: int):
    file = DATA_PATH / f"ks{ks_no}_questions_detailed.json"
    with open(file, "r", encoding="utf-8") as f:
        return json.load(f)

def init_session():
    if "state_ready" not in st.session_state:
        st.session_state.update({
            "state_ready": False,
            "ks": None,
            "q_set": [],
            "q_idx": 0,
            "score": 0,
            "show_result": False,
        })

def start_quiz(ks_no: int):
    qs = load_questions(ks_no)
    random.shuffle(qs)
    st.session_state.update(
        ks=ks_no,
        q_set=qs[:NUM_QUEST],
        q_idx=0,
        score=0,
        state_ready=True,
        show_result=False,
    )

def next_question(correct: bool):
    if correct:
        st.session_state.score += 1
    st.session_state.show_result = True

def proceed():
    st.session_state.q_idx += 1
    st.session_state.show_result = False
    if st.session_state.q_idx >= NUM_QUEST:
        st.session_state.state_ready = False  # Quiz beendet

# --------------------------------------------------
# UI: KS-Auswahl oder Quiz
# --------------------------------------------------
init_session()

st.title("🩺 ATA-Quiz")

if not st.session_state.state_ready:
    st.subheader("Kompetenzschwerpunkt wählen")
    cols = st.columns(len(KS_ORDER))
    for ix, ks in enumerate(KS_ORDER):
        if cols[ix].button(f"KS {ks}"):
            start_quiz(ks)
    st.write("⬆️ Bitte Schwerpunkt auswählen.")
else:
    q_obj = st.session_state.q_set[st.session_state.q_idx]
    st.write(f"**Frage {st.session_state.q_idx + 1} / {NUM_QUEST}**")
    st.markdown(f"### {q_obj['question']}")

    # Antwort-Buttons
    for idx, option in enumerate(q_obj["options"]):
        if st.button(option, disabled=st.session_state.show_result):
            correct = idx == q_obj["answer"]
            next_question(correct)

    # Ergebnis-Anzeige
    if st.session_state.show_result:
        correct = q_obj["answer"]
        result_text = "✅ Richtig!" if idx == correct else f"❌ Falsch – korrekt: {q_obj['options'][correct]}"
        st.markdown(result_text)

        # **Neue ausführliche Begründung**
        st.info(q_obj.get("answer_explanation", "Keine Erklärung hinterlegt."))

        # Weiter-Button
        if st.button("Nächste Frage"):
            proceed()

# --------------------------------------------------
# End-Scoring
# --------------------------------------------------
if st.session_state.state_ready is False and st.session_state.ks is not None:
    st.success(f"Fertig! Du hast {st.session_state.score} von {NUM_QUEST} Punkten erreicht.")
    if st.button("🔄 Neuer Durchgang"):
        st.session_state.ks = None
