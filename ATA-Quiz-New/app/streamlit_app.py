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
# 2) Session-State sicher anlegen
# ---------------------------------------------------------
def init_state():
    defaults = dict(
        current_ks   = None,
        question_set = [],
        q_idx        = 0,
        score        = 0,
        answered     = False,
        correct_last = None
    )
    for k, v in defaults.items():
        st.session_state.setdefault(k, v)

init_state()

# ---------------------------------------------------------
# 3) Layout
# ---------------------------------------------------------
st.set_page_config(page_title="ATA-Quiz", page_icon="🩺", layout="wide")
st.title("🩺 ATA-Quiz – Kompetenzschwerpunkte")

# ---------------------------------------------------------
# 4) KS-Wahl
# ---------------------------------------------------------
placeholder = "-- bitte wählen --"
labels      = [placeholder] + [KS_LABELS[k] for k in sorted(KS_PATHS)]
idx         = labels.index(KS_LABELS[st.session_state.current_ks]) \
              if st.session_state.current_ks else 0

label_chosen = st.selectbox("Kompetenzschwerpunkt wählen:", labels, index=idx)
chosen_ks    = None if label_chosen == placeholder else \
               next(k for k, v in KS_LABELS.items() if v == label_chosen)

# ---------------------------------------------------------
# 5) Quiz zurücksetzen, wenn KS gewechselt
# ---------------------------------------------------------
def reset_quiz(ks_code: str):
    with KS_PATHS[ks_code].open(encoding="utf-8") as f:
        pool = json.load(f)
    st.session_state.update(
        current_ks   = ks_code,
        question_set = random.sample(pool, min(15, len(pool))),
        q_idx        = 0,
        score        = 0,
        answered     = False,
        correct_last = None
    )

if chosen_ks and chosen_ks != st.session_state.current_ks:
    reset_quiz(chosen_ks)

# ---------------------------------------------------------
# 6) Eine Frage rendern
# ---------------------------------------------------------
def show_question(q):
    st.subheader(f"Frage {st.session_state.q_idx + 1} / {len(st.session_state.question_set)}")
    st.markdown(f"**{q['question']}**")

    cols = st.columns(2)
    for i, opt in enumerate(q["options"]):
        if cols[i % 2].button(opt, key=f"opt_{st.session_state.q_idx}_{i}") \
           and not st.session_state.answered:
            st.session_state.answered     = True
            st.session_state.correct_last = (i == q["answer"])
            if st.session_state.correct_last:
                st.session_state.score += 1

    # Feedback + Navigation
    if st.session_state.answered:
        if st.session_state.correct_last:
            st.success("✔️ Richtig!")
        else:
            st.error(f"❌ Falsch – korrekt: **{q['options'][q['answer']]}**")

        if st.session_state.q_idx < len(st.session_state.question_set) - 1:
            if st.button("➡️ Nächste Frage"):
                st.session_state.q_idx       += 1
                st.session_state.answered     = False
                st.session_state.correct_last = None
                st.experimental_rerun()     # <<< sofort neu rendern
        else:
            if st.button("🏁 Ergebnis anzeigen"):
                st.session_state.q_idx += 1
                st.experimental_rerun()

# ---------------------------------------------------------
# 7) End-Ergebnis
# ---------------------------------------------------------
def show_result():
    st.balloons()
    st.header("🎉 Quiz beendet")
    st.success(f"Du hast **{st.session_state.score} / {len(st.session_state.question_set)}** richtig!")

    if st.button("🔄 Neue Runde"):
        reset_quiz(st.session_state.current_ks)
        st.experimental_rerun()

# ---------------------------------------------------------
# 8) Render-Logik
# ---------------------------------------------------------
if st.session_state.current_ks:
    if st.session_state.q_idx < len(st.session_state.question_set):
        show_question(st.session_state.question_set[st.session_state.q_idx])
    else:
        show_result()
