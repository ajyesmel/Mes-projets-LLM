import os
import tiktoken
from dotenv import load_dotenv
from groq import Groq

# 1. Charger les variables d'environnement depuis le fichier .env
load_dotenv()

# 2. Vérifier que la clé existe
api_key = os.getenv("GROQ_API_KEY")
if not api_key:
    raise ValueError("❌ Clé GROQ_API_KEY non trouvée dans le fichier .env")

# 3. Initialiser le client Groq
client = Groq(api_key=api_key)

MODEL_NAME = "groq/compound-mini"
ENCODING_NAME = "cl100k_base"

def generate_exact_prompt(target_tokens: int) -> str:
    encoder = tiktoken.get_encoding(ENCODING_NAME)
    base_text = "test " 
    tokens = encoder.encode(base_text)
    repeated_tokens = (tokens * (target_tokens // len(tokens) + 1))[:target_tokens]
    return encoder.decode(repeated_tokens)

def test_context_limit():
    test_sizes = [4096, 8192, 16384, 32768, 65536]
    max_successful_tokens = 0

    print(f"--- Début du test pour : {MODEL_NAME} ---")

    for size in test_sizes:
        prompt_text = generate_exact_prompt(size)
        
        try:
            response = client.chat.completions.create(
                model=MODEL_NAME,
                messages=[{"role": "user", "content": prompt_text}],
                max_tokens=10
            )
            
            prompt_tokens_used = response.usage.prompt_tokens
            print(f"✅ Succès : {prompt_tokens_used} tokens passés sans erreur.")
            max_successful_tokens = prompt_tokens_used

        except Exception as e:
            print(f"❌ Limite atteinte à ~{size} tokens.")
            print(f"Erreur API : {e}")
            break

    print(f"\n🎯 Taille max validée du contexte : {max_successful_tokens} tokens.")

if __name__ == "__main__":
    test_context_limit()