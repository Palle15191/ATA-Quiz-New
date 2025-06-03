import json, random, streamlit as st
from pathlib import Path

# ---------- Datenverzeichnisse ----------
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

# ---------- Session-State ----------
for key, val in {"current_ks": None, "question_set": [], "submitted": False}.items():
    st.session_state.setdefault(key, val)

st.set_page_config(page_title="ATA-Quiz", page_icon="🩺", layout="wide")
st.title("🩺 ATA-Quiz – Kompetenzschwerpunkte")

# ---------- KS-Auswahl ----------
label_placeholder = "-- bitte wählen --"
label_list = [label_placeholder] + [KS_LABELS[k] for k in sorted(KS_PATHS)]

current_idx = 0
if st.session_state.current_ks:
    current_idx = label_list.index(KS_LABELS[st.session_state.current_ks])

chosen_label = st.selectbox("Kompetenzschwerpunkt wählen:", label_list, index=current_idx)

chosen_ks = None
if chosen_label != label_placeholder:
    chosen_ks = next(k for k, v in KS_LABELS.items() if v == chosen_label)

# ---------- Fragen ziehen ----------
if chosen_ks and chosen_ks != st.session_state.current_ks:
    with KS_PATHS[chosen_ks].open(encoding="utf-8") as f:
        pool = json.load(f)
    st.session_state.question_set = random.sample(pool, 15)
    st.session_state.current_ks, st.session_state.submitted = chosen_ks, False

# ---------- Quiz ----------
if st.session_state.current_ks:
    st.header(f"15 Fragen aus {KS_LABELS[st.session_state.current_ks]}")

    with st.form("quiz"):
        answers = []
        for i, q in enumerate(st.session_state.question_set, 1):
            st.markdown(f"**{i}. {q['question']}**")
            answers.append(st.radio("", q["options"], key=f"q{i}"))
            st.markdown("---")
        if st.form_submit_button("🎯 Auswertung"):
            st.session_state.submitted = True

    # ---------- Auswertung ----------
    if st.session_state.submitted:
        correct = sum(
            ua == q["options"][q["answer"]]
            for ua, q in zip(answers, st.session_state.question_set)
        )
        st.success(f"🏆 Ergebnis: **{correct} / 15** richtig")
        for i, (ua, q) in enumerate(zip(answers, st.session_state.question_set), 1):
            ok = ua == q["options"][q["answer"]]
            st.write(f"{'✅' if ok else '❌'} **{i}.** {q['question']}")
            if not ok:
                st.caption(f"Richtige Antwort: {q['options'][q['answer']]}")

        if st.button("🔄 Neue Runde"):
            st.session_state.submitted = False
            st.experimental_rerun()
