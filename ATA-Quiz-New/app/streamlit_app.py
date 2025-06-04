# streamlit_app.py  –  komplette, lauffähige Version
import json, random, pathlib, streamlit as st

# --------------------------------------------------
# Ordner-Pfad automatisch bestimmen  (<>__file__)
BASE_DIR   = pathlib.Path(__file__).resolve().parent       # = app/
DATA_PATH  = (BASE_DIR.parent / "questions").resolve()    # = questions/

KS_ORDER   = [1, 2, 3, 4, 5, 6, 7, 8]
NUM_QUEST  = 15

st.set_page_config("ATA-Quiz", "🩺", layout="wide")

# --------------------------------------------------
@st.cache_data
def load_questions(ks: int):
    """
    Sucht zuerst ksX_questions_detailed.json, dann ksX_questions.json
    im Ordner DATA_PATH.  Zeigt Fehlermeldung + Dateiliste, falls nichts da.
    """
    cand1 = DATA_PATH / f"ks{ks}_questions_detailed.json"
    cand2 = DATA_PATH / f"ks{ks}_questions.json"

    if cand1.exists(): target = cand1
    elif cand2.exists(): target = cand2
    else:
        st.error(f"⚠️ Keine Fragen-Datei für KS {ks} gefunden!")
        files = [p.name for p in DATA_PATH.glob("*.json")]
        st.write("Gefundene Dateien im Ordner:", files or "– keine –")
        st.stop()

    with target.open(encoding="utf-8") as fh:
        return json.load(fh)

def init_state():
    defaults = dict(
        state_ready=False, ks=None, q_set=[], q_idx=0,
        score=0, show_result=False, chosen=None, correct=False
    )
    for k, v in defaults.items():
        st.session_state.setdefault(k, v)

def start_quiz(ks: int):
    qs = load_questions(ks)
    random.shuffle(qs)
    st.session_state.update(
        state_ready=True, ks=ks, q_set=qs[:NUM_QUEST],
        q_idx=0, score=0, show_result=False, chosen=None, correct=False
    )

# --------------------------------------------------
init_state()
st.title("🩺 ATA-Quiz")

if not st.session_state.state_ready:
    st.subheader("Kompetenzschwerpunkt wählen")
    for col, ks in zip(st.columns(len(KS_ORDER)), KS_ORDER):
        if col.button(f"KS {ks}"):
            start_quiz(ks)
    st.stop()

# --------------------------------------------------
q = st.session_state.q_set[st.session_state.q_idx]
st.markdown(f"### Frage {st.session_state.q_idx + 1}/{NUM_QUEST}")
st.write(q["question"])

for idx, opt in enumerate(q["options"]):
    if st.button(opt, key=f"opt{idx}", disabled=st.session_state.show_result):
        st.session_state.chosen = idx
        st.session_state.correct = (idx == q["answer"])
        if st.session_state.correct:
            st.session_state.score += 1
        st.session_state.show_result = True

if st.session_state.show_result:
    corr_idx = q["answer"]
    corr_opt = q["options"][corr_idx]
    if st.session_state.correct:
        st.success("✅ **Richtig!**")
    else:
        st.error(f"❌ **Falsch** – korrekt: **{corr_opt}**")

    st.info(q.get("answer_explanation", "Für diese Frage liegt noch keine ausführliche Erklärung vor."))

    if st.button("Nächste Frage"):
        st.session_state.q_idx += 1
        if st.session_state.q_idx >= NUM_QUEST:
            st.session_state.state_ready = False
        st.session_state.show_result = False
        st.experimental_rerun()

# --------------------------------------------------
if not st.session_state.state_ready:
    st.success(f"Fertig! Ergebnis: {st.session_state.score}/{NUM_QUEST} Punkte.")
    if st.button("🔄 Neuer Durchgang"):
        st.session_state.clear()
        st.experimental_rerun()
