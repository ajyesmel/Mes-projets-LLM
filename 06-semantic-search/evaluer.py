"""Compare plusieurs modèles d'embeddings sur le jeu de questions de référence."""

from sentence_transformers import SentenceTransformer, util

from corpus import PASSAGES, QUESTIONS

# (nom du modèle, préfixe question, préfixe passage)
MODELES = [
    ("paraphrase-multilingual-MiniLM-L12-v2", "", ""),
    ("intfloat/multilingual-e5-small", "query: ", "passage: "),
    ("paraphrase-multilingual-mpnet-base-v2", "query: ", "passage:")
]


def evaluer(nom, prefixe_q, prefixe_p):
    modele = SentenceTransformer(nom)
    ids = [p["id"] for p in PASSAGES]
    textes = {p["id"]: p["texte"] for p in PASSAGES}

    # Indexation : une seule fois pour tous les passages
    vecteurs = modele.encode(
        [prefixe_p + textes[i] for i in ids], normalize_embeddings=True
    )

    print("\n" + "=" * 78)
    print("MODÈLE :", nom)
    print("=" * 78)

    nb_top1 = nb_top3 = nb_pertinentes = 0
    meilleurs_pertinents = []   # meilleur score des questions pertinentes
    meilleurs_hors_sujet = []   # meilleur score des questions hors sujet

    for q in QUESTIONS:
        vecteur_q = modele.encode(prefixe_q + q["question"], normalize_embeddings=True)
        scores = util.cos_sim(vecteur_q, vecteurs)[0].tolist()
        classement = sorted(zip(scores, ids), reverse=True)
        meilleur_score, meilleur_id = classement[0]

        if q["attendu"] is None:
            meilleurs_hors_sujet.append(meilleur_score)
            print(f"[HORS SUJET] {q['question']}")
            print(f"     meilleur score : {meilleur_score:.2f} ({meilleur_id})")
            continue

        nb_pertinentes += 1
        meilleurs_pertinents.append(meilleur_score)
        top1 = meilleur_id in q["attendu"]
        top3 = any(i in q["attendu"] for _, i in classement[:3])
        nb_top1 += top1
        nb_top3 += top3
        marge = meilleur_score - classement[1][0]
        etat = "OK " if top1 else ("~3 " if top3 else "KO ")
        print(f"[{etat}] {q['question']}")
        print(f"     1er : {meilleur_id} ({meilleur_score:.2f}), marge sur le 2e : {marge:.2f}, "
              f"attendu : {q['attendu']}")

    print("\n--- RÉSUMÉ", nom)
    print(f"Bon passage 1er    : {nb_top1}/{nb_pertinentes}")
    print(f"Bon passage top-3  : {nb_top3}/{nb_pertinentes}")
    pire_pertinent = min(meilleurs_pertinents)
    pire_hors_sujet = max(meilleurs_hors_sujet)
    print(f"Plus faible meilleur score, questions pertinentes : {pire_pertinent:.2f}")
    print(f"Plus fort meilleur score, questions hors sujet    : {pire_hors_sujet:.2f}")
    if pire_pertinent > pire_hors_sujet:
        print(f"-> Un seuil entre {pire_hors_sujet:.2f} et {pire_pertinent:.2f} sépare les deux groupes.")
    else:
        print("-> CHEVAUCHEMENT : aucun seuil fixe ne sépare pertinent et hors sujet.")


if __name__ == "__main__":
    for nom, pq, pp in MODELES:
        evaluer(nom, pq, pp)
