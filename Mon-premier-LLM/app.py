import streamlit as st
import importlib

_module = importlib.import_module("01_appel_simple_groq")
demander_au_llm = _module.demander_au_llm

SYSTEM_PROMPT = """Tu es un assistant pédagogique qui aide les débutants à apprendre la programmation
et les LLM. Réponds toujours en français, avec des explications simples et des exemples concrets.
Si une question est floue, pose une question de clarification avant de répondre.
Reste concis : pas plus de 4-5 phrases sauf si on te demande plus de détails."""

st.set_page_config(page_title="Mon premier chatbot LLM", page_icon="🤖")
st.title("🤖 Mon premier chatbot LLM")
st.caption("Propulsé par Groq (LLaMA 3.3) — avec mémoire et personnalité")

if st.button("🗑️ Réinitialiser la conversation"):
    st.session_state.historique = [{"role": "system", "content": SYSTEM_PROMPT}]
    st.rerun()

if "historique" not in st.session_state:
    st.session_state.historique = [{"role": "system", "content": SYSTEM_PROMPT}]

for msg in st.session_state.historique:
    if msg["role"] == "system":
        continue
    with st.chat_message(msg["role"]):
        st.write(msg["content"])

question = st.chat_input("Écris ton message...")

if question:
    st.session_state.historique.append({"role": "user", "content": question})
    with st.chat_message("user"):
        st.write(question)

    with st.chat_message("assistant"):
        with st.spinner("Réflexion..."):
            reponse = demander_au_llm(st.session_state.historique)
        st.write(reponse)

    st.session_state.historique.append({"role": "assistant", "content": reponse})