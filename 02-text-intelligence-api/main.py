from fastapi import FastAPI, HTTPException
from models import ProcessRequest, ProcessResponse
from llm_client import call_groq

app = FastAPI(title="Text Intelligence API")

PROMPTS = {
    "summarize": "Résume ce texte en 2 phrases maximum :\n\n{text}",
    "translate": "Traduis ce texte en {lang} :\n\n{text}",
    "classify": "Classe ce texte professionnel dans une des catégories suivantes : réclamation, question, commande, autre. Réponds uniquement par la catégorie.\n\n{text}",
}

@app.get("/health")
def health():
    return {"status": "ok"}

@app.post("/process", response_model=ProcessResponse)
def process(request: ProcessRequest):
    if request.task == "translate" and not request.target_language:
        raise HTTPException(status_code=400, detail="target_language requis pour 'translate'")

    prompt_template = PROMPTS[request.task]
    prompt = prompt_template.format(text=request.text, lang=request.target_language or "")

    try:
        result = call_groq(prompt)
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"Erreur API LLM : {e}")

    return ProcessResponse(
        task=request.task,
        result=result,
        original_length=len(request.text),
    ) 
    