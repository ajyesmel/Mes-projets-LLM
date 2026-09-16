import os
import csv
import time
from datetime import datetime
from groq import Groq
from dotenv import load_dotenv

load_dotenv()
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

LOG_FILE = "playground_log.csv"

def tester_prompt(question: str, temperature: float = 0.7, model: str = "groq/compound-mini",
                   system: str = None, stream: bool = False) -> dict:
    messages = []
    if system:
        messages.append({"role": "system", "content": system})
    messages.append({"role": "user", "content": question})

    debut = time.perf_counter()
    try:
        if stream:
            reponse_texte = ""
            flux = client.chat.completions.create(
                model=model, messages=messages, temperature=temperature, stream=True
            )
            for morceau in flux:
                contenu = morceau.choices[0].delta.content or ""
                print(contenu, end="", flush=True)
                reponse_texte += contenu
            print()
            tokens = None  # usage non renvoyé en mode stream par défaut
        else:
            result = client.chat.completions.create(
                model=model, messages=messages, temperature=temperature
            )
            reponse_texte = result.choices[0].message.content
            tokens = result.usage.total_tokens

        latence = round(time.perf_counter() - debut, 2)

        enregistrer_resultat(question, model, temperature, latence, tokens, reponse_texte)
        return {"reponse": reponse_texte, "latence": latence, "tokens": tokens}

    except Exception as e:
        print(f"❌ Erreur : {e}")
        return {"reponse": None, "latence": None, "tokens": None}


def enregistrer_resultat(question, model, temperature, latence, tokens, reponse):
    nouveau_fichier = not os.path.exists(LOG_FILE)
    with open(LOG_FILE, "a", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        if nouveau_fichier:
            writer.writerow(["date", "question", "model", "temperature", "latence_s", "tokens", "reponse"])
        writer.writerow([datetime.now().isoformat(), question, model, temperature, latence, tokens, reponse])


if __name__ == "__main__":
    q = "Donne-moi 3 idées de projets IA pour une PME ivoirienne."
    for temp in [0, 0.5, 1.0]:
        print(f"\n--- Température {temp} ---")
        tester_prompt(q, temperature=temp)
        