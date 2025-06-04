# streamlit_app.py
import json
import random
import pathlib
import streamlit as st

# --------------------------------------------------
# Grundeinstellungen
# --------------------------------------------------
st.set_page_config(
    page_title="ATA-Quiz",
    page_icon="🩺",
    layout="wide"
)

DATA_PATH = pathlib.Path("questions")   # Ordner mit den JSON-Dateien
KS_ORDER  = [1, 2, 3, 4, 5, 6, 7, 8]   # Reihenfolge der Schwerpunkte
NUM_QUEST = 15                         # Fragen pro Durchgang

# --------------------------------------------------
# Hilfsfunktionen
# --------------------------------------------------
@st.cache_data
def load_questions(ks_no: int):
    """
    Lädt die Datei …_detailed.json, 
    fällt bei Nichtvorhandensein auf …questions.json zurück
    """
    fname_new = DATA_PATH / f"ks{ks_no}_questions_detailed.json"
    fname_old = DATA_PATH / f"ks{ks_no}_questions.json"
    file = fname_new if fname_new.exists() else fname_old
    if not file.exists():
        raise FileNotFoundError(f"Keine Fragen-Datei für KS {ks_no} gefunden.")
    with open(file, encoding="utf-8") as f:
        return json.load(f)

def init_state():
    """setzt alle Session-Variablen, falls noch nicht vorhanden"""
    defaults = dict(
        state_ready=False,
        ks=None,
        q_set=[],
        q_idx=0,
        score=0,
        show_result=False,
        chosen_idx=None,
        is_correct=None,
    )
    for k, v in defaults.items():
        st.session_state.setdefault(k, v)

def start_quiz(ks_no: int):
    """initialisiert ein neues Quiz"""
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
# Start / Auswahl
# --------------------------------------------------
init_state()
st.title("🩺 ATA-Quiz")

if not st.session_state.state_ready:
    st.subheader("Kompetenzschwerpunkt wählen")
    cols = st.columns(len(KS_ORDER))
    for col, ks_no in zip(cols, KS_ORDER):
        if col.button(f"KS {ks_no}"):
            start_quiz(ks_no)
    st.stop()  # Ende – warten auf Auswahl

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

# Ergebnis & Erklärung
if st.session_state.show_result:
    chosen   = st.session_state.chosen_idx
    correct  = q["answer"]
    correct_option = q["options"][correct]

    if st.session_state.is_correct:
        st.success("✅ **Richtig!**")
    else:
        st.error(f"❌ **Falsch** – korrekt: **{correct_option}**")

    # ausführliche Erklärung (wenn vorhanden)
    st.info(q.get("answer_explanation", "Für diese Frage liegt noch keine ausführliche Erklärung vor."))

    if st.button("Nächste Frage"):
        st.session_state.q_idx += 1
        if st.session_state.q_idx >= NUM_QUEST:
            st.session_state.state_ready = False  # Quiz beendet
        st.session_state.show_result = False
        st.session_state.chosen_idx  = None
        st.session_state.is_correct  = None
        st.experimental_rerun()

# --------------------------------------------------
# Endauswertung
# --------------------------------------------------
if not st.session_state.state_ready:
    st.success(f"Quiz beendet – Ergebnis: **{st.session_state.score} / {NUM_QUEST}** Punkte")
    if st.button("🔄 Neuer Durchgang"):
        st.session_state.clear()
        st.experimental_rerun()
