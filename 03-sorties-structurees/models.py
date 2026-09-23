from pydantic import BaseModel
from typing import Optional, Literal

class Facture(BaseModel):
    fournisseur: str
    montant: float
    devise: str
    date: str
    numero_facture: Optional[str] = None

class BonDeCommande(BaseModel):
    client: str
    produits: list[str]
    quantite_totale: int
    date_commande: str

class Reclamation(BaseModel):
    client: str
    objet: str
    urgence: Literal["faible", "moyenne", "haute"]   # valeurs contrôlées
    date: Optional[str] = None                        # peut être absente du texte