# app/streamlit_app.py
import json
import random
from pathlib import Path
import streamlit as st

# ---------------------------------------------------------
# 1) Dateien & Labels
# ---------------------------------------------------------
QUEST_DIR = Path(__file__).parent.parent / "questions"
KS_PATHS  = {p.stem.split("_")[0].upper(): p
             for p in QUEST_DIR.glob("ks*_questions.json")}

KS_LABELS = {
    "KS1": "KS1 – Berufsbezogene Aufgaben",
    "KS2": "KS2 – Diagnostik & Therapie",
    "KS3": "KS3 – Interprofessionelles Handeln",
    "KS4": "KS4 – Persönliche Entwicklung",
    "KS5": "KS5 – Recht & Qualität",
    "KS6": "KS6 – Kommunikation",
    "KS7": "KS7 – Krisen- & Katastrophenmanagement",
    "KS8": "KS8 – Hygiene & Sterilgut"
}

# ---------------------------------------------------------
# 2) Session-State sicher anlegen
# ---------------------------------------------------------
def init_state():
    defaults = dict(
        current_ks   = None,   # z. B. "KS3"
        question_set = [],     # 15 Fragen aus dem Pool
        q_idx        = 0,      # Index der aktuellen Frage
        score        = 0,      # richtige Antworten
        answered     = False,  # wurde aktuelle Frage beantwortet?
        correct_last = None    # Ergebnis der letzten Antwort
    )
    for k, v in defaults.items():
        st.session_state.setdefault(k, v)

init_state()

# ---------------------------------------------------------
# 3) Grund-Layout
# ---------------------------------------------------------
st.set_page_config(page_title="ATA-Quiz", page_icon="🩺", layout="wide")
st.title("🩺 ATA-Quiz – Kompetenzschwerpunkte")

# ---------------------------------------------------------
# 4) KS wählen
# ---------------------------------------------------------
placeholder = "-- bitte wählen --"
labels = [placeholder] + [KS_LABELS[k] for k in sorted(KS_PATHS)]
idx    = labels.index(KS_LABELS[st.session_state.current_ks]) \
         if st.session_state.current_ks else 0

chosen_label = st.selectbox("Kompetenzschwerpunkt wählen:", labels, index=idx)
chosen_ks    = None if chosen_label == placeholder else \
               next(k for k, v in KS_LABELS.items() if v == chosen_label)

# ---------------------------------------------------------
# 5) Quiz neu starten, wenn KS wechselt
# ---------------------------------------------------------
def reset_quiz(ks_code: str):
    with KS_PATHS[ks_code].open(encoding="utf-8") as f:
        pool = json.load(f)
    k = min(15, len(pool))
    st.session_state.update(
        current_ks   = ks_code,
        question_set = random.sample(pool, k),
        q_idx        = 0,
        score        = 0,
        answered     = False,
        correct_last = None
    )

if chosen_ks and chosen_ks != st.session_state.current_ks:
    reset_quiz(chosen_ks)

# ---------------------------------------------------------
# 6) Eine Frage anzeigen
# ---------------------------------------------------------
def show_question(q):
    st.subheader(f"Frage {st.session_state.q_idx + 1} / {len(st.session_state.question_set)}")
    st.markdown(f"**{q['question']}**")

    # vier Buttons in zwei Spalten
    cols = st.columns(2)
    for i, option in enumerate(q["options"]):
        if cols[i % 2].button(option, key=f"btn_{st.session_state.q_idx}_{i}") \
           and not st.session_state.answered:
            st.session_state.answered     = True
            st.session_state.correct_last = (i == q["answer"])
            if st.session_state.correct_last:
                st.session_state.score += 1

    # Sofort-Feedback
    if st.session_state.answered:
        if st.session_state.correct_last:
            st.success("✔️ Richtig!")
        else:
            st.error(f"❌ Falsch – korrekt wäre: **{q['options'][q['answer']]}**")

        # Weiter- oder Ergebnis-Button
        if st.session_state.q_idx < len(st.session_state.question_set) - 1:
            if st.button("➡️ Nächste Frage"):
                st.session_state.q_idx   += 1
                st.session_state.answered = False
                st.session_state.correct_last = None
        else:
            if st.button("🏁 Ergebnis anzeigen"):
                st.session_state.q_idx += 1     # führt in die Ergebnis-Ansicht

# ---------------------------------------------------------
# 7) Ergebnis-Seite
# ---------------------------------------------------------
def show_result():
    st.balloons()
    st.header("🎉 Quiz beendet")
    st.success(f"Du hast **{st.session_state.score} / {len(st.session_state.question_set)}** "
               "Fragen richtig beantwortet.")

    if st.button("🔄 Neue Runde"):
        reset_quiz(st.session_state.current_ks)

# ---------------------------------------------------------
# 8) Render-Logik
# ---------------------------------------------------------
if st.session_state.current_ks:
    if st.session_state.q_idx < len(st.session_state.question_set):
        show_question(st.session_state.question_set[st.session_state.q_idx])
    else:
        show_result()
