"""Services métier : résumé et rédaction, avec mesure et journalisation systématiques."""
import time

from src import db
from src.llm_client import call_groq_full


def _run_llm_task(
    task: str,
    prompt: str,
    conversation_id: int,
    model: str = "openai/gpt-oss-20b",
    db_path=db.DB_PATH,
) -> str | None:
    """Squelette commun à tous les services LLM : chronomètre, appelle,
    journalise (succès ou échec), et ne laisse jamais une exception
    remonter jusqu'à l'appelant."""
    start = time.perf_counter()
    try:
        result = call_groq_full(prompt, model=model)
        latency_ms = int((time.perf_counter() - start) * 1000)
        db.log_interaction(
            conversation_id=conversation_id,
            task=task,
            input_text=prompt,
            model=model,
            status="ok",
            output_text=result.text,
            latency_ms=latency_ms,
            prompt_tokens=result.prompt_tokens,
            completion_tokens=result.completion_tokens,
            db_path=db_path,
        )
        return result.text
    except Exception as exc:
        latency_ms = int((time.perf_counter() - start) * 1000)
        db.log_interaction(
            conversation_id=conversation_id,
            task=task,
            input_text=prompt,
            model=model,
            status="error",
            latency_ms=latency_ms,
            error_message=str(exc),
            db_path=db_path,
        )
        return None


def summarize(text: str, conversation_id: int, db_path=db.DB_PATH) -> str | None:
    prompt = (
        "Résume l'échange client suivant en 3 phrases maximum, "
        "en français professionnel, sans inventer d'information :\n\n"
        f"{text}"
    )
    return _run_llm_task("summarize", prompt, conversation_id, db_path=db_path)


def draft_email(context: str, conversation_id: int, db_path=db.DB_PATH) -> str | None:
    prompt = (
        "Rédige un courriel professionnel en français, poli et concis, "
        "à partir du contexte suivant. N'invente aucune information "
        "absente du contexte :\n\n"
        f"{context}"
    )
    return _run_llm_task("email", prompt, conversation_id, db_path=db_path)


import json
from pydantic import ValidationError
from src.models import TaskExtraction


def extract_task(
    text: str,
    conversation_id: int,
    model: str = "openai/gpt-oss-20b",
    db_path=db.DB_PATH,
) -> TaskExtraction | None:
    """Transforme une demande client en tâche structurée, validée par Pydantic.

    Deux causes d'échec distinctes sont journalisées séparément :
    - l'appel à Groq échoue (réseau, quota, timeout) ;
    - Groq répond, mais le JSON est invalide ou ne respecte pas le schéma.
    Dans les deux cas : aucune exception ne remonte, la fonction renvoie None.
    """
    prompt = (
        "Transforme la demande client suivante en tâche structurée.\n"
        "Réponds UNIQUEMENT avec un objet JSON valide, sans texte autour, "
        "contenant exactement les clés :\n"
        '- "titre" (chaîne courte)\n'
        '- "priorite" ("basse", "normale" ou "haute")\n'
        '- "description" (chaîne)\n\n'
        f"Demande : {text}"
    )
    start = time.perf_counter()

    try:
        result = call_groq_full(prompt, model=model)
    except Exception as exc:
        latency_ms = int((time.perf_counter() - start) * 1000)
        db.log_interaction(
            conversation_id=conversation_id, task="extract", input_text=prompt,
            model=model, status="error", latency_ms=latency_ms,
            error_message=f"Erreur API Groq : {exc}", db_path=db_path,
        )
        return None

    latency_ms = int((time.perf_counter() - start) * 1000)

    try:
        data = json.loads(result.text)
        task = TaskExtraction.model_validate(data)
    except (json.JSONDecodeError, ValidationError) as exc:
        db.log_interaction(
            conversation_id=conversation_id, task="extract", input_text=prompt,
            model=model, status="error", output_text=result.text,
            latency_ms=latency_ms, prompt_tokens=result.prompt_tokens,
            completion_tokens=result.completion_tokens,
            error_message=f"JSON invalide ou non conforme au schéma : {exc}",
            db_path=db_path,
        )
        return None

    db.log_interaction(
        conversation_id=conversation_id, task="extract", input_text=prompt,
        model=model, status="ok", output_text=task.model_dump_json(),
        latency_ms=latency_ms, prompt_tokens=result.prompt_tokens,
        completion_tokens=result.completion_tokens, db_path=db_path,
    )
    return task