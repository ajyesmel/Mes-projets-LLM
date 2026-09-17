import os
import certifi
os.environ["SSL_CERT_FILE"] = certifi.where()

from groq import Groq
from dotenv import load_dotenv

load_dotenv()
client = Groq(api_key=os.environ["GROQ_API_KEY"])

def call_groq(prompt: str, model: str = "groq/compound-mini") -> str:
    response = client.chat.completions.create(
        model=model,
        messages=[{"role": "user", "content": prompt}],
        temperature=0.3,
    )
    return response.choices[0].message.content 