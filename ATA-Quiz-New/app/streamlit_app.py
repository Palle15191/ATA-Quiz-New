# streamlit_app.py
import json, random, pathlib, streamlit as st

# --------------------------------------------------
# Ordner mit Frage-Dateien automatisch finden
BASE_DIR  = pathlib.Path(__file__).resolve().parent      # = app/
DATA_PATH = (BASE_DIR.parent / "questions").resolve()    # = questions/

KS_ORDER  = [1, 2, 3, 4, 5, 6, 7, 8]
NUM_QUEST = 15

st.set_page_config("ATA-Quiz", "🩺", layout="wide")

# --------------------------------------------------
# Kompatibles Rerun (neu: st.rerun, alt: st.experimental_rerun)
def do_rerun():
    if hasattr(st, "rerun"):
        st.rerun()
    else:                              # Fallback für ältere Version
        st.experimental_rerun()

# --------------------------------------------------
@st.cache_data
def load_questions(ks: int):
    """
    Lädt ksX_questions_detailed.json, sonst ksX_questions.json
    und zeigt vorhandene Dateien, falls nichts passt.
    """
    candidates = [
        DATA_PATH / f"ks{ks}_questions_detailed.json",
        DATA_PATH / f"ks{ks}_questions.json",
    ]
    for file in candidates:
        if file.exists():
            with file.open(encoding="utf-8") as fh:
                return json.load(fh)

    st.error(f"⚠️ Keine Fragen-Datei für KS {ks} gefunden!")
    st.write("Im Ordner 'questions' vorhanden:", [p.name for p in DATA_PATH.glob('*.json')] or "– keine –")
    st.stop()

def init_state():
    defaults = dict(
        state_ready=False, ks=None, q_set=[],
        q_idx=0, score=0, show_result=False,
        chosen=None, correct=False,
    )
    for k, v in defaults.items():
        st.session_state.setdefault(k, v)

def start_quiz(ks: int):
    q = load_questions(ks)
    random.shuffle(q)
    st.session_state.update(
        state_ready=True, ks=ks, q_set=q[:NUM_QUEST],
        q_idx=0, score=0, show_result=False,
        chosen=None, correct=False,
    )

# --------------------------------------------------
init_state()
st.title("🩺 ATA-Quiz")

if not st.session_state.state_ready:
    st.subheader("Kompetenzschwerpunkt wählen")
    for col, ks in zip(st.columns(len(KS_ORDER)), KS_ORDER):
        if col.button(f"KS {ks}"):
            start_quiz(ks)
            do_rerun()
    st.stop()

# --------------------------------------------------
q = st.session_state.q_set[st.session_state.q_idx]
st.markdown(f"### Frage {st.session_state.q_idx + 1} / {NUM_QUEST}")
st.write(q["question"])

for idx, opt in enumerate(q["options"]):
    if st.button(opt, key=f"opt{idx}", disabled=st.session_state.show_result):
        st.session_state.chosen  = idx
        st.session_state.correct = (idx == q["answer"])
        if st.session_state.correct:
            st.session_state.score += 1
        st.session_state.show_result = True
        do_rerun()  # Antwort registriert → neu zeichnen

if st.session_state.show_result:
    corr_idx, corr_text = q["answer"], q["options"][q["answer"]]
    if st.session_state.correct:
        st.success("✅ **Richtig!**")
    else:
        st.error(f"❌ **Falsch** – korrekt: **{corr_text}**")

    st.info(q.get("answer_explanation", "Für diese Frage liegt keine ausführliche Erklärung vor."))

    if st.button("Nächste Frage"):
        st.session_state.q_idx += 1
        if st.session_state.q_idx >= NUM_QUEST:
            st.session_state.state_ready = False
        st.session_state.show_result = False
        do_rerun()

# --------------------------------------------------
if not st.session_state.state_ready:
    st.success(f"Quiz beendet – dein Ergebnis: **{st.session_state.score}/{NUM_QUEST}** Punkte")
    if st.button("🔄 Neuer Durchgang"):
        st.session_state.clear()
        do_rerun()
