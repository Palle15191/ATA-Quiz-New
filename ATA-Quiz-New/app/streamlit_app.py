# app/streamlit_app.py
import json, random, streamlit as st
from pathlib import Path

##############################
# 1)  Pfade & Katalog laden  #
##############################
QUEST_DIR = Path(__file__).resolve().parent.parent / "questions"
KS_FILES  = sorted(QUEST_DIR.glob("ks*_questions.json"))   # → [Path('.../ks1_questions.json'), …]

#   Mapping:  KS-Code  →  Pfad
KS_PATHS = {p.stem.split("_")[0].upper(): p for p in KS_FILES}

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
##############################
# 2)  Session-State anlegen  #
##############################
if "current_ks"   not in st.session_state: st.session_state.current_ks   = None
if "question_set" not in st.session_state: st.session_state.question_set = []
if "submitted"    not in st.session_state: st.session_state.submitted    = False

st.set_page_config(page_title="ATA-Quiz", page_icon="🩺", layout="wide")
st.title("🩺 ATA-Quiz – Kompetenzschwerpunkte")

################################
# 3)  KS auswählen → Fragenpool #
################################
chosen_label = st.selectbox(
    "Kompetenzschwerpunkt wählen:",
    options=[KS_LABELS[k] for k in KS_PATHS],
    index=-1 if st.session_state.current_ks is None else list(KS_PATHS).index(st.session_state.current_ks)
)

# Label → KS-Code
chosen_ks = next((k for k, v in KS_LABELS.items() if v == chosen_label), None)

# wenn neue Auswahl  →  JSON laden & 15 Fragen ziehen
if chosen_ks and chosen_ks != st.session_state.current_ks:
    with KS_PATHS[chosen_ks].open(encoding="utf-8") as f:
        pool = json.load(f)
    random.shuffle(pool)
    st.session_state.question_set = pool[:15]
    st.session_state.current_ks   = chosen_ks
    st.session_state.submitted    = False

###########################
# 4)  Quiz anzeigen/lösen #
###########################
if st.session_state.current_ks:

    st.header(f"15 Fragen aus {KS_LABELS[st.session_state.current_ks]}")

    with st.form("quiz_form"):
        answers = []
        for i, q in enumerate(st.session_state.question_set, 1):
            st.markdown(f"**{i}. {q['question']}**")
            ans = st.radio("", q["options"], key=f"q{i}")
            answers.append(ans)
            st.markdown("---")
        submitted = st.form_submit_button("🎯 Auswertung")

    if submitted:
        st.session_state.submitted = True
        correct = sum(
            ua == q["options"][q["answer"]]
            for ua, q in zip(answers, st.session_state.question_set)
        )

        st.success(f"🏆 Ergebnis: **{correct} / {len(st.session_state.question_set)} richtig**")
        for idx, (ua, q) in enumerate(zip(answers, st.session_state.question_set), 1):
            symb = "✅" if ua == q["options"][q["answer"]] else "❌"
            st.write(f"{symb} **{idx}.** {q['question']}")
            if symb == "❌":
                st.caption(f"Richtige Antwort: {q['options'][q['answer']]}")

        if st.button("🔄 Neue Runde"):
            st.session_state.submitted = False
            st.experimental_rerun()