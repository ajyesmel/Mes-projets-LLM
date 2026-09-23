from sentence_transformers import SentenceTransformer 
from sklearn.metrics.pairwise import cosine_similarity 


model = SentenceTransformer("all-MiniLM-L6-v2") 

phrases = [
    "Le chat dort sur le canapé.",
    "Le felin fait la sieste sur le sofa.",
    "La boursse a chuté de 3% aujourd'hui."
]

embeddings = model.encode(phrases)
print("Dimension des embeddings : ", embeddings.shape)

sim = cosine_similarity(embeddings)

print("/Matrice de similarité :\n")
print(sim)


