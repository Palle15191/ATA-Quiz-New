import json, random, streamlit as st
from pathlib import Path

# ---------- Konstanten ----------
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

# ---------- Session-State Defaults ----------
defaults = dict(
    current_ks   = None,   # z. B. "KS3"
    question_set = [],     # Liste aus 15 Fragen
    q_idx        = 0,      # aktuelle Frage-Nr. (0-basiert)
    score        = 0,      # richtige Antworten
    answered     = False,  # ob aktuelle Frage bereits beantwortet
    correct_last = None    # True / False
)
for k, v in defaults.items():
    st.session_state.setdefault(k, v)

st.set_page_config(page_title="ATA-Quiz", page_icon="🩺", layout="wide")
st.title("🩺 ATA-Quiz – Kompetenzschwerpunkte")

# ---------- KS-Dropdown ----------
placeholder = "-- bitte wählen --"
label_list  = [placeholder] + [KS_LABELS[k] for k in sorted(KS_PATHS)]
sel_idx     = 0 if not st.session_state.current_ks else label_list.index(KS_LABELS[st.session_state.current_ks])

chosen_label = st.selectbox("Kompetenzschwerpunkt wählen:", label_list, index=sel_idx)
chosen_ks    = None if chosen_label == placeholder else next(k for k,v in KS_LABELS.items() if v == chosen_label)

# ---------- Neu starten, falls anderer KS gewählt ----------
if chosen_ks and chosen_ks != st.session_state.current_ks:
    with KS_PATHS[chosen_ks].open(encoding="utf-8") as f:
        pool = json.load(f)
    st.session_state.update(
        current_ks   = chosen_ks,
        question_set = random.sample(pool, 15),
        q_idx        = 0,
        score        = 0,
        answered     = False,
        correct_last = None
    )

# ---------- Quiz-Logik ----------
def show_question(q):
    st.subheader(f"Frage {st.session_state.q_idx + 1} / 15")
    st.markdown(f"**{q['question']}**")

    # Vier Antwort-Buttons als Columns
    cols = st.columns(2)
    for i, option in enumerate(q["options"]):
        col = cols[i % 2]
        if col.button(option, key=f"opt{st.session_state.q_idx}_{i}") and not st.session_state.answered:
            st.session_state.answered     = True
            st.session_state.correct_last = (i == q["answer"])
            if st.session_state.correct_last:
                st.session_state.score += 1

    # Bei Antwort sofort Feedback
    if st.session_state.answered:
        if st.session_state.correct_last:
            st.success("✔️ Richtig!")
        else:
            corr = q["options"][q["answer"]]
            st.error(f"❌ Falsch – korrekt wäre: **{corr}**")

        # Weiter- bzw. Ergebnis-Button
        if st.session_state.q_idx < 14:
            if st.button("➡️ Nächste Frage"):
                st.session_state.q_idx    += 1
                st.session_state.answered  = False
                st.session_state.correct_last = None
                st.experimental_rerun()
        else:
            if st.button("🏁 Ergebnis anzeigen"):
                st.session_state.answered = False
                st.experimental_rerun()

def show_result():
    st.balloons()
    st.header("🎉 Quiz beendet")
    st.success(f"Du hast **{st.session_state.score} von 15** Fragen richtig beantwortet!")

    if st.button("🔄 Neue Runde"):
        st.session_state.q_idx   = 0
        st.session_state.score   = 0
        st.session_state.answered = False
        random.shuffle(st.session_state.question_set)   # Fragen neu mischen
        st.experimental_rerun()

# ---------- Anzeige ----------
if st.session_state.current_ks:
    if st.session_state.q_idx < 15:
        show_question(st.session_state.question_set[st.session_state.q_idx])
    else:
        show_result()
