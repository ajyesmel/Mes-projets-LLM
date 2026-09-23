def chunk_text(text:str, chunk_size: int=200, overlap: int=50) :
    chunk = []
    start = 0 
    while start < len(text):
        end = start + chunk_size
        chunk.append(text[start:end])
        start+= chunk_size - overlap
    return chunk 

texte = """Analyser et tokeniser un fichier MIDI avec le package music21, c'est comme transformer une partition en un alphabet que l'IA peut lire. Chaque note, chaque silence, chaque durée devient un symbole, un peu comme transcrire un air de zouglou en une suite de syllabes précises que n'importe qui peut ensuite déchiffrer et rejouer.

L'encodage positionnel avec sinus, c'est le métronome silencieux de l'IA. Il rappelle en permanence au modèle à quel instant précis de la mesure il se trouve, comme un percussionniste qui garde le rythme en tête même quand les autres musiciens improvisent autour de lui."""

chunks = chunk_text(texte, chunk_size=200, overlap=50)

for i, c in enumerate(chunks): 
    print(f"-----Chunk{i} -----\n{c}\n")
    
    