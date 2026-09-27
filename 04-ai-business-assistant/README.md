# AI Business Assistant

Assistant professionnel basé sur un LLM (Groq), qui résume des échanges
clients, rédige des courriels et transforme une demande en tâche
structurée — avec journalisation systématique de chaque appel (succès,
échec, latence, tokens).

## Problème métier

Les équipes qui utilisent des LLM pour du travail répétitif (résumer des
échanges, rédiger des courriels, extraire des tâches) manquent
généralement de visibilité sur la fiabilité et le coût réel de ces
appels : erreurs silencieuses, latence inconnue, pas d'historique
exploitable. Ce projet fournit un assistant métier pour ces trois
tâches, avec une journalisation systématique qui rend chaque appel
mesurable et traçable — la brique d'observabilité manque presque
toujours dans les prototypes IA, c'est précisément ce que ce projet
démontre.

## Fonctionnalités

- **Résumer** un échange client en 3 phrases maximum.
- **Rédiger** un courriel professionnel à partir d'un contexte.
- **Extraire une tâche structurée** (titre, priorité, description),
  validée par un schéma Pydantic — toute réponse du modèle qui ne
  respecte pas le schéma est rejetée et journalisée comme échec, jamais
  silencieusement ignorée.
- **Historique** complet par conversation.
- **Tableau de bord** : nombre d'appels, taux d'erreur, latence
  moyenne, tokens consommés — globalement et par type de tâche.

## Architecture

```
app.py (Streamlit)
   |
services.py -- résumer / rédiger / extraire (mesure + gestion d'erreur)
   |     \
   |      models.py (validation Pydantic des sorties structurées)
   |
llm_client.py -- appel à l'API Groq
   |
db.py (SQLite) -- conversations + journal des interactions
```

`services.py` ne dépend d'aucune bibliothèque d'interface (pas de
Streamlit) : la même logique sera réutilisée telle quelle dans un futur
backend FastAPI (plateforme multicanale, phases suivantes).

## Installation

```bash
git clone https://github.com/ajyesmel/Mes-projets-LLM.git
cd 04-ai-business-assistant
python -m venv .venv
source .venv/bin/activate   # Windows : .venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env        # puis renseigner GROQ_API_KEY
```

## Utilisation

```bash
streamlit run app.py
```

Deux pages :
- **Assistant** : créer/choisir une conversation, lancer un des trois
  services, consulter l'historique.
- **Statistiques** : indicateurs globaux et détaillés par tâche.

## Tests

```bash
pytest -v
```

15 tests couvrent `db.py` et `services.py`, y compris les cas d'échec
(API indisponible, JSON invalide, valeur hors schéma) — sans aucun
appel réseau réel, grâce à un faux client Groq simulé (*mock*).

## Limites connues

- Persistance en **SQLite local**, pas encore adaptée à un usage
  multi-utilisateur concurrent (prévu en PostgreSQL, phases
  suivantes).
- Aucune authentification ni isolation multi-entreprise (prévu Phase
  6).
- Le schéma `TaskExtraction` a une liste fermée de priorités
  (`basse`/`normale`/`haute`) : le modèle peut proposer une valeur hors
  de cette liste, auquel cas l'extraction échoue et est journalisée —
  ce n'est pas un bug, c'est un choix de validation stricte, mais cela
  suppose de faire évoluer le schéma si le besoin métier change.
- `app.py` n'a pas de tests automatisés dédiés : la logique testable
  est entièrement déléguée à `services.py` et `db.py` (voir plus haut).
- Prototype pédagogique : ne pas présenter comme prêt pour la
  production sans revue de sécurité et de charge.

## Prochaines améliorations

- Migration vers PostgreSQL.
- Ajout d'un cache pour éviter les appels redondants.
- Comparaison de plusieurs modèles/fournisseurs (Groq, OpenAI,
  Anthropic) sur les mêmes tâches.