# app/streamlit_app.py
import json, random
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
# 2) Session-State initialisieren
# ---------------------------------------------------------
def init_state():
    st.session_state.setdefault("current_ks",   None)
    st.session_state.setdefault("question_set", [])
    st.session_state.setdefault("q_idx",        0)
    st.session_state.setdefault("score",        0)
    st.session_state.setdefault("answered",     False)
    st.session_state.setdefault("correct_last", None)

init_state()

# ---------------------------------------------------------
# 3) Hilfs-Funktionen zum State-Ändern
# ---------------------------------------------------------
def reset_quiz(ks_code: str):
    with KS_PATHS[ks_code].open(encoding="utf-8") as f:
        pool = json.load(f)
    st.session_state.current_ks   = ks_code
    st.session_state.question_set = random.sample(pool, min(15, len(pool)))
    st.session_state.q_idx        = 0
    st.session_state.score        = 0
    st.session_state.answered     = False
    st.session_state.correct_last = None

def next_question():
    st.session_state.q_idx    += 1
    st.session_state.answered  = False
    st.session_state.correct_last = None

def new_round():
    reset_quiz(st.session_state.current_ks)

# ---------------------------------------------------------
# 4) Layout & KS-Auswahl
# ---------------------------------------------------------
st.set_page_config(page_title="ATA-Quiz", page_icon="🩺", layout="wide")
st.title("🩺 ATA-Quiz – Kompetenzschwerpunkte")

placeholder = "-- bitte wählen --"
labels      = [placeholder] + [KS_LABELS[k] for k in sorted(KS_PATHS)]
idx         = labels.index(KS_LABELS[st.session_state.current_ks]) \
              if st.session_state.current_ks else 0

label = st.selectbox("KS auswählen:", labels, index=idx)
chosen = None if label == placeholder else next(k for k,v in KS_LABELS.items() if v == label)

if chosen and chosen != st.session_state.current_ks:
    reset_quiz(chosen)

# ---------------------------------------------------------
# 5) Frage / Ergebnis anzeigen
# ---------------------------------------------------------
if st.session_state.current_ks:

    # ------------------- Frage-Phase ----------------------
    if st.session_state.q_idx < len(st.session_state.question_set):
        q = st.session_state.question_set[st.session_state.q_idx]
        st.subheader(f"Frage {st.session_state.q_idx + 1} / {len(st.session_state.question_set)}")
        st.markdown(f"**{q['question']}**")

        cols = st.columns(2)
        for i, option in enumerate(q["options"]):
            if cols[i % 2].button(option, key=f"opt_{st.session_state.q_idx}_{i}") \
               and not st.session_state.answered:
                st.session_state.answered     = True
                st.session_state.correct_last = (i == q["answer"])
                if st.session_state.correct_last:
                    st.session_state.score += 1

        if st.session_state.answered:
            if st.session_state.correct_last:
                st.success("✔️ Richtig!")
            else:
                st.error(f"❌ Falsch – korrekt: **{q['options'][q['answer']]}**")

            # Weiter-Button via Callback
            btn_label = "➡️ Nächste Frage" if st.session_state.q_idx < len(st.session_state.question_set)-1 \
                        else "🏁 Ergebnis anzeigen"
            st.button(btn_label, on_click=next_question)

    # ------------------- Ergebnis-Phase -------------------
    else:
        st.balloons()
        st.header("🎉 Quiz beendet")
        st.success(f"Du hast **{st.session_state.score} / {len(st.session_state.question_set)}** richtig!")

        st.button("🔄 Neue Runde", on_click=new_round)
