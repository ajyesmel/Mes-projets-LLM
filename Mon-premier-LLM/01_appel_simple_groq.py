import os
import requests
from dotenv import load_dotenv

load_dotenv()
api_key = os.environ.get("GROQ_API_KEY", "").strip()


def demander_au_llm(messages: list, model: str = "groq/compound-mini") -> str:
    try:
        response = requests.post(
            "https://api.groq.com/openai/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json",
            },
            json={
                "model": model,
                "messages": messages,
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