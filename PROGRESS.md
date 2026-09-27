# Suivi de progression — Parcours Agents IA / LLM / RAG

**Profil :** Data Scientist / Data Engineer, base solide en Machine
Learning.
**Rythme :** sprint compressé (~25-30h/semaine) plutôt que le rythme
initial de 10-12h/semaine.
**Point de départ technique :** API Groq (`groq/compound-mini`
indisponible sur le compte → remplacé par `openai/gpt-oss-20b`).

---

## Phase 1 — Maîtriser les API LLM (semaines 1 à 4)

### Semaine 1 — LLM Playground ✅

- **Réalisé :** application de test de prompts avec journal CSV
  (température, streaming, message système, latence, tokens).
- **Compétences acquises :** notions de fenêtre de contexte et de
  température ; premiers appels à l'API Groq.

### Semaine 2 — Text Intelligence API ✅

- **Réalisé :** API FastAPI + Pydantic (routes `/health` et
  `/process`, tâches résumer/traduire/classer).
- **Difficulté corrigée :** `SSL_CERT_FILE` invalide sur l'environnement
  local — corrigé en fixant le chemin via `certifi.where()` dans
  `llm_client.py`.
- **Compétences acquises :** séparation des responsabilités,
  validation Pydantic, gestion d'erreurs HTTP.

### Semaine 3 — AI Document Extractor ✅

- **Réalisé :** extraction de données structurées (Facture, Bon de
  commande, Réclamation) avec modèles Pydantic, comparaison automatisée
  à une référence, export CSV.
- **Difficultés corrigées :**
  - schéma JSON envoyé tel quel au modèle au lieu d'un exemple de
    valeurs (le modèle hallucinait des valeurs) ;
  - un `Literal` non décrit explicitement dans le prompt ;
  - une fonction `extraire_document` dupliquée par erreur de
    copier-coller, la seconde définition écrasant silencieusement la
    première (symptôme : retour `None` sans erreur visible) ;
  - `comparer_a_reference` non appelée dans les tests.
- **Compétences acquises :** sorties structurées, diagnostic d'un bug
  silencieux (écrasement de fonction), tests de comparaison à une
  référence.

### Semaine 4 — AI Business Assistant ✅

- **Réalisé :**
  - `db.py` : persistance SQLite (conversations, journal des
    interactions), statistiques globales et par tâche.
  - `services.py` : `summarize`, `draft_email`, `extract_task` —
    chronométrage, journalisation systématique (succès et échec),
    aucune exception ne remonte jamais à l'appelant.
  - `models.py` : validation stricte des sorties structurées
    (`TaskExtraction`, priorité limitée par `Literal`).
  - `app.py` : interface Streamlit (page Assistant + page
    Statistiques), restylée après un premier retour critique
    ("trop plat", peu soigné visuellement).
  - 15 tests pytest, entièrement mockés (aucun appel réseau réel).
  - README, post LinkedIn (storytelling autour de la fiabilité, pas
    juste la démo) programmé.
- **Difficultés corrigées :**
  - cache Python périmé (`__pycache__`) sous OneDrive, faisant tourner
    une ancienne version d'un module malgré un fichier source modifié
    (`AttributeError` trompeur) ;
  - `st.dataframe()` cassé sous Windows/Anaconda (DLL `pyarrow`
    manquant) — contourné avec un tableau Markdown fait main.
- **Compétences acquises :** persistance et agrégation SQL (`GROUP BY`),
  gestion d'erreur systématique autour d'un appel API externe,
  observabilité (latence, tokens, taux d'erreur), diagnostic
  d'environnement (cache, DLL), retour critique sur son propre travail
  et itération.
- **Reste à faire :** aucun — semaine clôturée.

---

## Prochaine étape

**Phase 2 — Construire des RAG, semaine 5 : Embeddings et recherche
vectorielle.** Notions à venir : embeddings, similarité cosinus,
chunking, métadonnées ; comparaison pgvector / Qdrant ; Mini-projet 4 —
Semantic Search Engine.
