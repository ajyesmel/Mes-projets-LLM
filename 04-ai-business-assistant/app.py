"""Interface Streamlit — AI Business Assistant (Semaine 4).

Deux pages : Assistant (lancer les services) et Statistiques (observabilité).
Ce fichier ne contient AUCUNE logique métier : tout vit dans services.py et
db.py, réutilisables tels quels dans un futur backend (voir S17-20).
"""
import streamlit as st

from src import db, services

db.init_db()  # ne fait rien si la base existe déjà (CREATE TABLE IF NOT EXISTS)

st.set_page_config(
    page_title="AI Business Assistant",
    page_icon="🤖",
    layout="wide",
)

# Légère mise en forme, en plus du thème dans .streamlit/config.toml.
# Ne touche à rien de la logique : uniquement de la présentation.
st.markdown(
    """
    <style>
    .bloc-carte {
        background-color: #FFFFFF;
        border: 1px solid #E3E8E1;
        border-radius: 10px;
        padding: 1.1rem 1.3rem;
        margin-bottom: 0.6rem;
    }
    div[data-testid="stMetric"] {
        background-color: #FFFFFF;
        border: 1px solid #E3E8E1;
        border-radius: 10px;
        padding: 0.8rem 1rem 0.4rem 1rem;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

if "conversation_id" not in st.session_state:
    st.session_state.conversation_id = None

with st.sidebar:
    st.markdown("### 🤖 AI Business Assistant")
    st.caption("Résumé · Rédaction · Extraction — avec journalisation systématique")
    page = st.radio("Navigation", ["💬 Assistant", "📊 Statistiques"], label_visibility="collapsed")
    st.divider()
    st.caption("Semaine 4 · Phase 1 · Parcours Agents IA / LLM / RAG")


def _afficher_resultat(resultat):
    """Un seul endroit qui décide comment afficher un résultat de service.
    Gère explicitement le cas où le service a renvoyé None (échec journalisé)."""
    if resultat is None:
        st.error(
            "⚠️ Le service n'a pas pu produire de résultat. "
            "L'erreur a été journalisée — voir la page Statistiques."
        )
    else:
        st.success("✅ Résultat")
        if hasattr(resultat, "model_dump"):  # cas TaskExtraction (Pydantic)
            st.json(resultat.model_dump())
        else:
            with st.container(border=True):
                st.write(resultat)


ICONES_SERVICE = {
    "Résumer un échange": "📝",
    "Rédiger un courriel": "✉️",
    "Extraire une tâche": "🗂️",
}


if page == "💬 Assistant":
    st.title("💬 Assistant")
    st.caption("Une conversation = un dossier client. Choisis un service, colle le texte, lance.")

    conversations = db.list_conversations()
    titres = {c["id"]: c["title"] for c in conversations}

    col1, col2 = st.columns([2, 1])
    with col1:
        if conversations:
            choix = st.selectbox(
                "Conversation",
                options=list(titres.keys()),
                format_func=lambda cid: f"#{cid} — {titres[cid]}",
            )
            st.session_state.conversation_id = choix
    with col2:
        nouveau_titre = st.text_input("Nouvelle conversation", placeholder="Nom du client")
        if st.button("➕ Créer", use_container_width=True) and nouveau_titre.strip():
            st.session_state.conversation_id = db.create_conversation(nouveau_titre.strip())
            st.rerun()

    if st.session_state.conversation_id is None:
        st.info("👆 Crée ou sélectionne une conversation pour commencer.")
        st.stop()

    st.caption(f"Conversation active : **#{st.session_state.conversation_id}**")

    with st.container(border=True):
        tache = st.radio(
            "Service",
            list(ICONES_SERVICE.keys()),
            format_func=lambda t: f"{ICONES_SERVICE[t]}  {t}",
            horizontal=True,
        )
        texte = st.text_area("Texte source", height=140, placeholder="Colle ici le message ou le contexte client...")
        lance = st.button("🚀 Lancer", type="primary", use_container_width=True)

    if lance and texte.strip():
        with st.spinner("Appel au modèle en cours..."):
            if tache == "Résumer un échange":
                resultat = services.summarize(texte, st.session_state.conversation_id)
            elif tache == "Rédiger un courriel":
                resultat = services.draft_email(texte, st.session_state.conversation_id)
            else:
                resultat = services.extract_task(texte, st.session_state.conversation_id)
        _afficher_resultat(resultat)

    st.divider()
    st.subheader("🕘 Historique")
    historique = db.get_interactions(st.session_state.conversation_id)
    if not historique:
        st.caption("Aucune interaction pour cette conversation.")
    for interaction in reversed(historique):
        icone = "✅" if interaction["status"] == "ok" else "❌"
        with st.expander(f"{icone} {interaction['task']} — {interaction['created_at']}"):
            st.write("**Entrée :**", interaction["input_text"])
            if interaction["status"] == "ok":
                st.write("**Sortie :**", interaction["output_text"])
            else:
                st.write("**Erreur :**", interaction["error_message"])
            st.caption(f"⏱️ Latence : {interaction['latency_ms']} ms")

else:  # page == "📊 Statistiques"
    st.title("📊 Statistiques")
    st.caption("Fiabilité et coût réel des appels au modèle, mesurés automatiquement.")

    stats = db.get_stats()
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("📞 Appels totaux", stats["total"])
    c2.metric("❌ Erreurs", stats["errors"])
    c3.metric("⏱️ Latence moyenne", f"{round(stats['avg_latency_ms'])} ms")
    c4.metric("🔤 Tokens (total)", stats["prompt_tokens"] + stats["completion_tokens"])

    st.subheader("Détail par type de tâche")
    par_tache = db.get_stats_by_task()
    if par_tache:
        # st.dataframe()/st.table() dépendent de pyarrow en interne. Sur certains
        # environnements Windows/Anaconda, pyarrow a un DLL cassé (voir README).
        # On affiche donc un tableau Markdown, sans aucune dépendance à pyarrow.
        colonnes = list(par_tache[0].keys())
        entete = "| " + " | ".join(colonnes) + " |"
        separateur = "| " + " | ".join(["---"] * len(colonnes)) + " |"
        lignes = [
            "| " + " | ".join(str(ligne[c]) for c in colonnes) + " |"
            for ligne in par_tache
        ]
        st.markdown("\n".join([entete, separateur, *lignes]))
    else:
        st.caption("Aucune donnée pour l'instant — lance quelques services depuis la page Assistant.") 