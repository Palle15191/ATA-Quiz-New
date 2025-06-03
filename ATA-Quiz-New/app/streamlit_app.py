
import json, random
from pathlib import Path
import streamlit as st

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

def init_state():
    for k, v in dict(current_ks=None, question_set=[], q_idx=0, score=0,
                     answered=False, correct_last=None).items():
        st.session_state.setdefault(k, v)

init_state()

def reset_quiz(ks_code):
    with KS_PATHS[ks_code].open(encoding='utf-8') as f:
        pool = json.load(f)
    st.session_state.update(
        current_ks=ks_code,
        question_set=random.sample(pool, min(15, len(pool))),
        q_idx=0, score=0, answered=False, correct_last=None
    )

def next_q():
    st.session_state.q_idx += 1
    st.session_state.answered = False
    st.session_state.correct_last = None

def new_round():
    reset_quiz(st.session_state.current_ks)

st.set_page_config(page_title='ATA-Quiz', page_icon='🩺', layout='wide')
st.title('🩺 ATA-Quiz – Kompetenzschwerpunkte')

placeholder='-- bitte wählen --'
labels=[placeholder]+[KS_LABELS[k] for k in sorted(KS_PATHS)]
sel_idx=labels.index(KS_LABELS[st.session_state.current_ks]) if st.session_state.current_ks else 0
label=st.selectbox('KS auswählen:', labels, index=sel_idx)
chosen=None if label==placeholder else next(k for k,v in KS_LABELS.items() if v==label)

if chosen and chosen!=st.session_state.current_ks:
    reset_quiz(chosen)

if st.session_state.current_ks:
    if st.session_state.q_idx < len(st.session_state.question_set):
        q=st.session_state.question_set[st.session_state.q_idx]
        st.subheader(f'Frage {st.session_state.q_idx+1} / {len(st.session_state.question_set)}')
        st.markdown(f"**{q['question']}**")
        cols=st.columns(2)
        for i,opt in enumerate(q['options']):
            if cols[i%2].button(opt, key=f"opt_{st.session_state.q_idx}_{i}") and not st.session_state.answered:
                st.session_state.answered=True
                st.session_state.correct_last=(i==q['answer'])
                if st.session_state.correct_last:
                    st.session_state.score+=1
        if st.session_state.answered:
            if st.session_state.correct_last:
                st.success('✔️ Richtig!')
            else:
                st.error(f"❌ Falsch – korrekt: **{q['options'][q['answer']]}**")
            ref = q.get('ref_detail') or q.get('ref')
            if ref:
                st.info(f'📖 Nachschlagen: *ATA-Lehrbuch* {ref}')
            btn_label='➡️ Nächste Frage' if st.session_state.q_idx < len(st.session_state.question_set)-1 else '🏁 Ergebnis anzeigen'
            st.button(btn_label, on_click=next_q)
    else:
        st.balloons()
        st.header('🎉 Quiz beendet')
        st.success(f"Du hast **{st.session_state.score} / {len(st.session_state.question_set)}** richtig!")
        st.button('🔄 Neue Runde', on_click=new_round)
