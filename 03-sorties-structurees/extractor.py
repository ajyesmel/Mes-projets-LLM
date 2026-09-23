import os
import re
import json
from groq import Groq
from pydantic import BaseModel, ValidationError
from dotenv import load_dotenv
load_dotenv()
import typing 

client = Groq(api_key=os.environ["GROQ_API_KEY"]) 

def extraire_json(texte_brut: str) -> dict:
    """Isole le bloc JSON même si le modèle a ajouté du texte autour."""
    match = re.search(r"\{.*\}", texte_brut, re.DOTALL)
    if not match:
        raise ValueError(f"Aucun JSON trouvé dans la réponse : {texte_brut}")
    return json.loads(match.group(0))

def extraire_document(texte: str, schema: type[BaseModel], nom_schema: str) -> BaseModel | None:
    # On construit un EXEMPLE de format (valeurs, pas un schéma) à partir des noms de champs
    exemple = {nom: f"<{champ.annotation.__name__ if hasattr(champ.annotation, '__name__') else str(champ.annotation)}>"
               for nom, champ in schema.model_fields.items()}

    prompt = f"""
Extrait les informations suivantes du texte ci-dessous, réponds UNIQUEMENT en JSON valide.
Utilise exactement ces clés, remplies avec les vraies valeurs trouvées dans le texte (pas les types entre <>) :
{json.dumps(exemple, ensure_ascii=False)}

Si une information est absente du texte, mets la valeur null (n'invente rien).

Texte : "{texte}"
"""
    resp = client.chat.completions.create(
        model="openai/gpt-oss-20b",
        messages=[{"role": "user", "content": prompt}],
        temperature=0,
    )
    brut = resp.choices[0].message.content

    try:
        data = extraire_json(brut)
        return schema(**data)
    except (json.JSONDecodeError, ValueError) as e:
        print(f"[{nom_schema}] Échec parsing JSON : {e}\nRéponse brute : {brut}")
        return None
    except ValidationError as e:
        print(f"[{nom_schema}] Échec validation Pydantic : {e}")
        return None



def decrire_champ(annotation) -> str:
    if typing.get_origin(annotation) is typing.Literal:
        valeurs = typing.get_args(annotation)
        return f"une valeur EXACTEMENT parmi {list(valeurs)}"
    nom_type = getattr(annotation, "__name__", str(annotation))
    return f"<{nom_type}>"

def extraire_document(texte: str, schema: type[BaseModel], nom_schema: str) -> BaseModel | None:
    exemple = {nom: decrire_champ(champ.annotation) for nom, champ in schema.model_fields.items()}
    # ... reste inchangé

REFERENCES = {
    "Facture": {"fournisseur": "ARYLINE HOLDING", "montant": 150000.0, "devise": "FCFA"},
    "BonDeCommande": {"client": "KOUASSI SARL", "quantite_totale": 15},
    "Reclamation": {"client": "TRAORE"},
}

def comparer_a_reference(nom_schema: str, resultat: BaseModel):
    ref = REFERENCES.get(nom_schema, {})
    for champ, valeur_attendue in ref.items():
        valeur_obtenue = getattr(resultat, champ, None)
        statut = "OK" if valeur_obtenue == valeur_attendue else "❌ ÉCART"
        print(f"  {champ}: attendu={valeur_attendue!r} / obtenu={valeur_obtenue!r} → {statut}")