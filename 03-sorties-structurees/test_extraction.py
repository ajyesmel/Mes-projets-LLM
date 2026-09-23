from models import Facture, BonDeCommande, Reclamation
from extractor import extraire_document
import csv

documents = [
    ("documents_fictifs/facture_01.txt", Facture, "Facture"),
    ("documents_fictifs/commande_01.txt", BonDeCommande, "BonDeCommande"),
    ("documents_fictifs/reclamation_01.txt", Reclamation, "Reclamation"),
]

resultats = []
for chemin, schema, nom in documents:
    with open(chemin, encoding="utf-8") as f:
        texte = f.read()
    resultat = extraire_document(texte, schema, nom)
    print(f"--- {nom} ---\n{resultat}\n")
    if resultat:
        resultats.append({"type": nom, **resultat.model_dump()})

# Export vers CSV pour usage Excel/SQL
if resultats:
    cles = sorted({k for r in resultats for k in r.keys()})
    with open("extraction_resultats.csv", "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=cles)
        writer.writeheader()
        writer.writerows(resultats)  