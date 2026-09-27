import os
from dataclasses import dataclass

import certifi
os.environ["SSL_CERT_FILE"] = certifi.where()

from groq import Groq
from dotenv import load_dotenv

load_dotenv()
client = Groq(api_key=os.environ.get("GROQ_API_KEY", ""))


def call_groq(prompt: str, model: str = "openai/gpt-oss-20b") -> str:
    """Fonction historique (S1-S3) : renvoie uniquement le texte. Conservée telle quelle."""
    response = client.chat.completions.create(
        model=model,
        messages=[{"role": "user", "content": prompt}],
        temperature=0.3,
    )
    return response.choices[0].message.content


@dataclass
class LLMResult:
    text: str
    prompt_tokens: int | None
    completion_tokens: int | None


def call_groq_full(prompt: str, model: str = "openai/gpt-oss-20b") -> LLMResult:
    """Nouvelle fonction (S4) : renvoie aussi les tokens, pour la journalisation."""
    response = client.chat.completions.create(
        model=model,
        messages=[{"role": "user", "content": prompt}],
        temperature=0.3,
    )
    usage = getattr(response, "usage", None)
    return LLMResult(
        text=response.choices[0].message.content,
        prompt_tokens=getattr(usage, "prompt_tokens", None) if usage else None,
        completion_tokens=getattr(usage, "completion_tokens", None) if usage else None,
    )