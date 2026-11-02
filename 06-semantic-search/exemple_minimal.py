from sentence_transformers import SentenceTransformer, util

passages = [
    "Les colis sont livrés à Abidjan sous 48 heures ouvrables.",
    "Pour suivre votre livraison, utilisez le numéro de suivi reçu par SMS.",
    "Les remboursements sont effectués sous 14 jours après réception du retour.",
    "Our office is closed on public holidays.",
    # Piège : mêmes mots que la question, mais autre sens
    "Mon colis préféré est le colis de Noël offert chaque année aux employés.",
]

questions = [
    "Où est mon colis ?",
    "Ou est mon colis ?",   # même question sans accent
    "Combien de temps pour être remboursé ?",
    "Quelle est la capitale du Japon ?",
]


def tester(nom_modele, prefixe_question="", prefixe_passage=""):
    modele = SentenceTransformer("paraphrase-multilingual-MiniLM-L12-v2")
    vecteurs = modele.encode(
        [prefixe_passage + p for p in passages], normalize_embeddings=True
    )
    print("=" * 70)
    print("MODÈLE :", nom_modele)

    for q in questions:
        vecteur_q = modele.encode(prefixe_question + q, normalize_embeddings=True)
        scores = util.cos_sim(vecteur_q, vecteurs)[0]
        print(f"\nQuestion : {q}")
        for score, texte in sorted(zip(scores.tolist(), passages), reverse=True):
            print(f"  {score:.2f}  {texte}")


tester("paraphrase-multilingual-MiniLM-L12-v2")
tester("intfloat/multilingual-e5-small", "query: ", "passage: ")