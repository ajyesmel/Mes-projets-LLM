import chromadb

# 1. Réutilise ta fonction chunk_text()
def chunk_text(text: str, chunk_size: int = 100, overlap: int = 20):
    chunks = []
    start = 0
    while start < len(text):
        end = start + chunk_size
        chunks.append(text[start:end])
        start += chunk_size - overlap
    return chunks 

texte = """Analyser et tokeniser un fichier MIDI avec le package music21, c'est comme transformer une partition en un alphabet que l'IA peut lire. Chaque note, chaque silence, chaque durée devient un symbole, un peu comme transcrire un air de zouglou en une suite de syllabes précises que n'importe qui peut ensuite déchiffrer et rejouer.
L'encodage positionnel avec sinus, c'est le métronome silencieux de l'IA. Il rappelle en permanence au modèle à quel instant précis de la mesure il se trouve, comme un percussionniste qui garde le rythme en tête même quand les autres musiciens improvisent autour de lui."""

chunks = chunk_text(texte, chunk_size=150, overlap=30)

# 2. Vector Strore ( Chromabd gère les embeddings automatiquement comme avant)
client = chromadb.Client()
collection = client.create_collection(name="rag_pipeline")

collection.add(
    documents=chunks,
    ids = [f"chunk_{i}" for i in range(len(chunks))]
    )

# 3. Fonction qui recupère et formate le contexte 
def get_context(query: str, n_results: int = 2 ) -> str:
    results = collection.query(
        query_texts = [query],
        n_results = n_results
    )
    chunks_trouves = results["documents"][0]
    contexte = "\n\n---\n\n".join(chunks_trouves)
    return contexte 

# 4. Test 
query = "Comment l'IA sait ou elle en est dans le rythme ?"

contexte = get_context(query)

print(f"Contexte récupéré pour la requête :\n")
print(contexte)


import os
from dotenv import load_dotenv
from groq import Groq

load_dotenv()
client_groq = Groq(api_key=os.getenv("GROQ_API_KEY"))

def generate_answer(query: str, contexte: str) -> str:
    prompt = f"""Tu es un assistant qui répond UNIQUEMENT à partir du contexte fourni ci-dessous.
Si la réponse n'est pas dans le contexte, dis-le clairement au lieu d'inventer.

Contexte :
{contexte}

Question : {query}

Réponse :"""

    response = client_groq.chat.completions.create(
        model="groq/compound-mini",
        messages=[{"role": "user", "content": prompt}],
        max_tokens=300
    )
    return response.choices[0].message.content

# Génération finale
reponse = generate_answer(query, contexte)
print("\n🤖 RÉPONSE DU RAG :\n")
print(reponse)