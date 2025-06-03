# app/streamlit_app.py
import json, random, streamlit as st
from pathlib import Path

#############################################
# 1)  Daten-Verzeichnisse & Labels
#############################################
QUEST_DIR = Path(__file__).parent.parent / "questions"
KS_PATHS  = {p.stem.split("_")[0].upper(): p for p in QUEST_DIR.glob("ks*_questions.json")}

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

#############################################
# 2)  Session-State sicher initialisieren
#############################################
def init_state():
    """legt ALLE benötigten Keys einmalig an"""
    defaults = dict(
        current_ks   = None,   # z. B. "KS3"
        question_set = [],     # Liste der 15 Fragen
        q_idx        = 0,      # Nummer der aktuellen Frage
        score        = 0,      # richtige Antworten
        answered     = False,  # ob aktuelle Frage beantwortet
        correct_last = None    # Ergebnis der zuletzt beantworteten
    )
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v

init_state()  # ← GANZ am Anfang aufrufen

#############################################
# 3)  Grund-Layout
#############################################
st.set_page_config(page_title="ATA-Quiz", page_icon="🩺", layout="wide")
st.title("🩺 ATA-Quiz – Kompetenzschwerpunkte")

#############################################
# 4)  KS-Dropdown mit Platzhalter
#############################################
placeholder = "-- bitte wählen --"
label_list  = [placeholder] + [KS_LABELS[k] for k in sorted(KS_PATHS)]

sel_idx = 0
if st.session_state.current_ks:
    sel_idx = label_list.index(KS_LABELS[st.session_state.current_ks])

chosen_label = st.selectbox("Kompetenzschwerpunkt wählen:", label_list, index=sel_idx)
chosen_ks    = None if chosen_label == placeholder else next(k for k,v in KS_LABELS.items() if v == chosen_label)

#############################################
# 5)  Quiz neu starten, falls KS gewechselt
#############################################
def reset_quiz(ks_code: str):
    with KS_PATHS[ks_code].open(encoding="utf-8") as f:
        pool = json.load(f)
    k = 15 if len(pool) >= 15 else len(pool)         # Fallback falls <15 Fragen
    st.session_state.current_ks   = ks_code
    st.session_state.question_set = random.sample(pool, k)
    st.session_state.q_idx        = 0
    st.session_state.score        = 0
    st.session_state.answered     = False
    st.session_state.correct_last = None

if chosen_ks and chosen_ks != st.session_state.current_ks:
    reset_quiz(chosen_ks)

#############################################
# 6)  Anzeige einer Frage
#############################################
def show_question(q):
    st.subheader(f"Frage {st.session_state.q_idx + 1} / {len(st.session_state.question_set)}")
    st.markdown(f"**{q['question']}**")

    # Antwort-Buttons in zwei Spalten
    cols = st.columns(2)
    for i, option in enumerate(q["options"]):
        if cols[i % 2].button(option, key=f"btn_{st.session_state.q_idx}_{i}") and not st.session_state.answered:
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
                st.session_state.q_idx    += 1
                st.session_state.answered  = False
                st.session_state.correct_last = None
                st.experimental_rerun()
        else:
            if st.button("🏁 Ergebnis anzeigen"):
                st.session_state.answered = False
                st.experimental_rerun()

#############################################
# 7)  End-Ergebnis
#############################################
def show_result():
    st.balloons()
    st.header("🎉 Quiz beendet")
    st.success(f"Du hast **{st.session_state.score} / {len(st.session_state.question_set)}** richtig!")

    if st.button("🔄 Neue Runde"):
        reset_quiz(st.session_state.current_ks)
        st.experimental_rerun()

#############################################
# 8)  Render-Logik
#############################################
if st.session_state.current_ks:
    if st.session_state.q_idx < len(st.session_state.question_set):
        show_question(st.session_state.question_set[st.session_state.q_idx])
    else:
        show_result()
