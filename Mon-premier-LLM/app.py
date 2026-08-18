import streamlit as st
from test_llm import demander_au_llm

# Configuration de la page
st.set_page_config(page_title="Mon premier chatbot LLM", page_icon="🤖")

st.title("🤖 Mon premier chatbot LLM")
st.caption("Propulsé par Groq (LLaMA 3.3)")

# Zone de saisie utilisateur
question = st.text_input("Pose ta question ici :")

# Bouton pour envoyer
if st.button("Envoyer"):
    if question.strip() == "":
        st.warning("Écris d'abord une question.")
    else:
        with st.spinner("Réflexion en cours..."):
            reponse = demander_au_llm(question)
        st.markdown("### Réponse")
        st.write(reponse) 