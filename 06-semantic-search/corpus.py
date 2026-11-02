"""Corpus fictif d'une entreprise ivoirienne de e-commerce (« Kolo Express »)
et jeu de questions de référence.

Tout est inventé : aucune donnée réelle.
"""

PASSAGES = [
    {"id": "P01", "texte": "Les colis sont livrés à Abidjan sous 48 heures ouvrables."},
    {"id": "P02", "texte": "Pour les villes de l'intérieur (Bouaké, Yamoussoukro, San-Pédro), le délai de livraison est de 3 à 5 jours ouvrables."},
    {"id": "P03", "texte": "Pour suivre votre livraison, utilisez le numéro de suivi reçu par SMS."},
    {"id": "P04", "texte": "La livraison est gratuite à partir de 25 000 FCFA d'achat. En dessous, elle coûte 1 500 FCFA à Abidjan."},
    {"id": "P05", "texte": "Les remboursements sont effectués sous 14 jours après réception du retour."},
    {"id": "P06", "texte": "Vous disposez de 7 jours après la livraison pour retourner un article non utilisé dans son emballage d'origine."},
    {"id": "P07", "texte": "Un article reçu endommagé ou défectueux est échangé gratuitement. Envoyez une photo au service client sous 48 heures."},
    {"id": "P08", "texte": "Vous pouvez payer par Orange Money, MTN MoMo, Moov Money ou Wave."},
    {"id": "P09", "texte": "Le paiement à la livraison en espèces est disponible uniquement à Abidjan."},
    {"id": "P10", "texte": "Une commande peut être annulée gratuitement tant qu'elle n'a pas été expédiée."},
    {"id": "P11", "texte": "Le service client est ouvert du lundi au vendredi de 8h à 18h, et le samedi de 9h à 13h."},
    {"id": "P12", "texte": "Vous pouvez nous écrire sur WhatsApp au +225 00 00 00 00 00 (numéro fictif)."},
    {"id": "P13", "texte": "Our office is closed on public holidays."},
    {"id": "P14", "texte": "Si votre colis n'est pas arrivé après 7 jours ouvrables, contactez le service client avec votre numéro de commande."},
    {"id": "P15", "texte": "Vous pouvez modifier l'adresse de livraison avant l'expédition, depuis votre compte ou par WhatsApp."},
    {"id": "P16", "texte": "La livraison en point relais est disponible dans 40 points à Abidjan, pour 800 FCFA."},
    {"id": "P17", "texte": "Pour réinitialiser votre mot de passe, cliquez sur « Mot de passe oublié » sur la page de connexion."},
    {"id": "P18", "texte": "Votre facture est envoyée par e-mail après l'expédition et reste disponible dans votre compte."},
    {"id": "P19", "texte": "Les appareils électroniques bénéficient d'une garantie de 12 mois."},
    {"id": "P20", "texte": "Les codes promotionnels ne sont pas cumulables et sont valables 30 jours."},
    {"id": "P21", "texte": "Chaque tranche de 1 000 FCFA dépensée donne 1 point de fidélité ; 100 points valent 1 000 FCFA de réduction."},
    {"id": "P22", "texte": "Nous livrons aussi au Sénégal, au Ghana et au Burkina Faso, en 7 à 10 jours ouvrables."},
    # Piège : contient « colis » mais n'a aucun rapport avec une commande client
    {"id": "P23", "texte": "Mon colis préféré est le colis de Noël offert chaque année aux employés."},
    {"id": "P24", "texte": "Pour déposer une réclamation, écrivez à reclamation@exemple.ci en indiquant votre numéro de commande."},
]

# "attendu" = liste des passages jugés acceptables ; None = hors sujet
# (le moteur devrait idéalement répondre « rien de pertinent »).
QUESTIONS = [
    {"question": "Où est mon colis ?", "attendu": ["P03", "P14"]},
    {"question": "Ou est mon colis ?", "attendu": ["P03", "P14"]},
    {"question": "Combien de temps pour être remboursé ?", "attendu": ["P05"]},
    {"question": "Mon colis n'est toujours pas arrivé", "attendu": ["P14", "P03"]},
    {"question": "C'est combien la livraison ?", "attendu": ["P04"]},
    {"question": "Je veux payer avec Wave", "attendu": ["P08"]},
    {"question": "Peut-on payer en cash à la livraison ?", "attendu": ["P09"]},
    {"question": "J'ai reçu un article cassé", "attendu": ["P07"]},
    {"question": "Jusqu'à quand puis-je renvoyer un produit ?", "attendu": ["P06"]},
    {"question": "a quelle heure vous ouvrez le samedi", "attendu": ["P11"]},
    {"question": "Je me suis trompé d'adresse", "attendu": ["P15"]},
    {"question": "J'ai oublié mon mot de passe", "attendu": ["P17"]},
    {"question": "Livrez-vous à Dakar ?", "attendu": ["P22"]},
    {"question": "Combien de temps pour une livraison à Bouaké ?", "attendu": ["P02"]},
    {"question": "Can I cancel my order?", "attendu": ["P10"]},
    {"question": "Comment avoir une réduction ?", "attendu": ["P20", "P21"]},
    # Hors sujet
    {"question": "Quelle est la capitale du Japon ?", "attendu": None},
    {"question": "Quel temps fait-il demain à Abidjan ?", "attendu": None},
    {"question": "Donne-moi une recette d'attiéké", "attendu": None},
    {"question": "Comment fonctionne un moteur diesel ?", "attendu": None},
]
