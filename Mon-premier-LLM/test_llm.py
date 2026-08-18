import os
import requests
from dotenv import load_dotenv

load_dotenv()
api_key = os.environ.get("GROQ_API_KEY", "").strip()


def demander_au_llm(question: str, model: str = "groq/compound-mini") -> str:
    """
    Envoie une question au LLM (via Groq) et retourne sa réponse en texte.
    En cas d'erreur, retourne un message explicite au lieu de planter.
    """
    try:
        response = requests.post(
            "https://api.groq.com/openai/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json",
            },
            json={
                "model": model,
                "messages": [
                    {"role": "user", "content": question}
                ],
            },
            timeout=30,
        )
        data = response.json()

        if response.status_code != 200:
            erreur = data.get("error", {}).get("message", "Erreur inconnue")
            return f"❌ Erreur API : {erreur}"

        return data["choices"][0]["message"]["content"]

    except requests.exceptions.Timeout:
        return "❌ Le serveur a mis trop de temps à répondre."
    except requests.exceptions.ConnectionError:
        return "❌ Impossible de se connecter — vérifie ta connexion internet."
    except Exception as e:
        return f"❌ Erreur inattendue : {e}"


# Test de la fonction
if __name__ == "__main__":
    reponse = demander_au_llm("Donne-moi 3 idées de projets pour apprendre les LLM.")
    print(reponse) 