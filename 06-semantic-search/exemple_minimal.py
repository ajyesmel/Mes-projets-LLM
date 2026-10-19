from sentence_transformers import SentenceTransformer, util

# Modèle multilingue (français + anglais). Téléchargé au premier lancement.
modele = SentenceTransformer("paraphrase-multilingual-MiniLM-L12-v2")

passages = [
    "Les colis sont livrés à Abidjan sous 48 heures ouvrables.",
    "Pour suivre votre livraison, utilisez le numéro de suivi reçu par SMS.",
    "Les remboursements sont effectués sous 14 jours après réception du retour.",
    "Our office is closed on public holidays.",
]

question = "Où est mon colis ?"

vecteurs = modele.encode(passages)           # un vecteur par passage
vecteur_q = modele.encode(question)          # un vecteur pour la question

scores = util.cos_sim(vecteur_q, vecteurs)[0]  # similarité cosinus avec chaque passage

for score, texte in sorted(zip(scores.tolist(), passages), reverse=True):
    print(f"{score:.2f}  {texte}") 