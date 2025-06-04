# streamlit_app.py  – nur die Unterschiede 👇
import json, random, pathlib, streamlit as st

# … (Setup bleibt gleich)

def next_question(chosen_idx: int):
    """setzt Ergebnis & zeigt Erklärung an"""
    q = st.session_state.q_set[st.session_state.q_idx]
    st.session_state.chosen_idx = chosen_idx         # neu
    st.session_state.is_correct = (chosen_idx == q["answer"])
    if st.session_state.is_correct:
        st.session_state.score += 1
    st.session_state.show_result = True

# --------------------------------------------------
# Quiz-Darstellung
# --------------------------------------------------
if st.session_state.state_ready:
    q = st.session_state.q_set[st.session_state.q_idx]
    st.write(f"**Frage {st.session_state.q_idx + 1} / {NUM_QUEST}**")
    st.markdown(f"### {q['question']}")

    for idx, opt in enumerate(q["options"]):
        if st.button(opt, disabled=st.session_state.show_result, key=f"opt{idx}"):
            next_question(idx)                       # Auswahl übergeben

    # Ergebnis-Anzeige
    if st.session_state.show_result:
        chosen = st.session_state.chosen_idx
        correct = q["answer"]

        result_txt = (
            "✅ **Richtig!**" if st.session_state.is_correct
            else f"❌ **Falsch** – korrekt: {q['options'][correct]}"
        )
        st.markdown(result_txt)

        # ► ausführliche Erklärung aus JSON
        st.info(q.get("answer_explanation", "Keine Erläuterung hinterlegt."))

        # Weiter-Button
        if st.button("Nächste Frage"):
            st.session_state.q_idx += 1
            if st.session_state.q_idx >= NUM_QUEST:
                st.session_state.state_ready = False
            st.session_state.show_result = False

# … (End-Scoring unverändert)
