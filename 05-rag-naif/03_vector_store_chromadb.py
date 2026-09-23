# Importation des librairies 
import chromadb
from sentence_transformers import SentenceTransformer 

# Reutilisation de la fonction Chunks 
def chunk_text(text : str, chunk_size : int = 100, overlap : int = 20):
    chunks = []
    start = 0
    while start < len(text):
        end = min(start + chunk_size, len(text))
        chunks.append(text[start:end])
        start += chunk_size - overlap
    return chunks

texte = """Analyser et tokeniser un fichier MIDI avec le package music21, c'est comme transformer une partition en un alphabet que l'IA peut lire. Chaque note, chaque silence, chaque durée devient un symbole, un peu comme transcrire un air de zouglou en une suite de syllabes précises que n'importe qui peut ensuite déchiffrer et rejouer.
L'encodage positionnel avec sinus, c'est le métronome silencieux de l'IA. Il rappelle en permanence au modèle à quel instant précis de la mesure il se trouve, comme un percussionniste qui garde le rythme en tête même quand les autres musiciens improvisent autour de lui."""

chunks = chunk_text(texte, chunk_size=150, overlap=30)

# 2. Modèle d'embedding (le même que tout à l'heure)
model = SentenceTransformer('all-MiniLM-L6-v2')

# 3. Créer un vector store local en mémoire
client = chromadb.Client()
collection = client.create_collection(name="test_midi")

# 4. Ajouter les chunks (Chroma calcule les embeddings tout seul par défaut,
#    mais on peut aussi lui passer les nôtres — restons simple ici)
collection.add(
    documents=chunks,
    ids=[f"chunk_{i}" for i in range(len(chunks))]
)

# 5. Faire une recherche par similarité
query = "Comment l'IA sait où elle en est dans le rythme ?"
results = collection.query(
    query_texts=[query],
    n_results=2
)

print(f"🔍 Requête : {query}\n")
for doc, dist in zip(results['documents'][0], results['distances'][0]):
    print(f"Distance: {dist:.4f}")
    print(f"Chunk: {doc}\n")

