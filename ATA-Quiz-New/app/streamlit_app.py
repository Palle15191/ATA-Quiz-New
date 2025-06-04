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
        state_rea_
