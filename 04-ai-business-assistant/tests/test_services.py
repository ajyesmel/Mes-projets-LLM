"""Tests de services.py — Groq est simulé (mock), aucun vrai appel réseau n'est fait."""
import pytest
from src import db, services
from src.llm_client import LLMResult


@pytest.fixture
def db_path(tmp_path):
    path = tmp_path / "test.db"
    db.init_db(path)
    return path


def test_summarize_succes_journalise_ok(monkeypatch, db_path):
    monkeypatch.setattr(
        services, "call_groq_full",
        lambda prompt, model="openai/gpt-oss-20b": LLMResult(
            text="Le client demande le statut de sa commande.",
            prompt_tokens=42,
            completion_tokens=12,
        ),
    )
    conv_id = db.create_conversation("Test", db_path)

    result = services.summarize("Bonjour, où est mon colis ?", conv_id, db_path=db_path)

    assert result == "Le client demande le statut de sa commande."
    rows = db.get_interactions(conv_id, db_path)
    assert len(rows) == 1
    assert rows[0]["status"] == "ok"
    assert rows[0]["task"] == "summarize"
    assert rows[0]["prompt_tokens"] == 42
    assert rows[0]["latency_ms"] is not None


def test_summarize_echec_ne_plante_pas_et_journalise_error(monkeypatch, db_path):
    def faux_appel_qui_plante(prompt, model="openai/gpt-oss-20b"):
        raise TimeoutError("Le serveur Groq n'a pas répondu à temps")

    monkeypatch.setattr(services, "call_groq_full", faux_appel_qui_plante)
    conv_id = db.create_conversation("Test", db_path)

    result = services.summarize("Bonjour", conv_id, db_path=db_path)

    assert result is None  # pas d'exception : l'appelant reçoit None proprement
    rows = db.get_interactions(conv_id, db_path)
    assert rows[0]["status"] == "error"
    assert "Groq" in rows[0]["error_message"]


def test_draft_email_succes(monkeypatch, db_path):
    monkeypatch.setattr(
        services, "call_groq_full",
        lambda prompt, model="openai/gpt-oss-20b": LLMResult(
            text="Bonjour, votre colis est en cours de livraison.",
            prompt_tokens=30,
            completion_tokens=10,
        ),
    )
    conv_id = db.create_conversation("Test", db_path)

    result = services.draft_email("Client demande statut colis", conv_id, db_path=db_path)

    assert "colis" in result
    rows = db.get_interactions(conv_id, db_path)
    assert rows[0]["task"] == "email"


def test_extract_task_succes_json_valide(monkeypatch, db_path):
    monkeypatch.setattr(
        services, "call_groq_full",
        lambda prompt, model="openai/gpt-oss-20b": LLMResult(
            text='{"titre": "Colis manquant", "priorite": "haute", "description": "Le client n\'a pas reçu sa commande."}',
            prompt_tokens=50,
            completion_tokens=20,
        ),
    )
    conv_id = db.create_conversation("Test", db_path)

    task = services.extract_task("Où est mon colis ?", conv_id, db_path=db_path)

    assert task.titre == "Colis manquant"
    assert task.priorite == "haute"
    rows = db.get_interactions(conv_id, db_path)
    assert rows[0]["status"] == "ok"
    assert rows[0]["task"] == "extract"


def test_extract_task_json_invalide_journalise_texte_brut(monkeypatch, db_path):
    monkeypatch.setattr(
        services, "call_groq_full",
        lambda prompt, model="openai/gpt-oss-20b": LLMResult(
            text="Bien sûr ! Voici la tâche : titre=Colis, priorite=urgent",  # pas du JSON, priorite invalide
            prompt_tokens=50,
            completion_tokens=20,
        ),
    )
    conv_id = db.create_conversation("Test", db_path)

    task = services.extract_task("Où est mon colis ?", conv_id, db_path=db_path)

    assert task is None
    rows = db.get_interactions(conv_id, db_path)
    assert rows[0]["status"] == "error"
    assert rows[0]["output_text"] == "Bien sûr ! Voici la tâche : titre=Colis, priorite=urgent"
    assert "JSON" in rows[0]["error_message"]


def test_extract_task_priorite_hors_enum_refusee(monkeypatch, db_path):
    monkeypatch.setattr(
        services, "call_groq_full",
        lambda prompt, model="openai/gpt-oss-20b": LLMResult(
            text='{"titre": "Colis", "priorite": "urgente-absolue", "description": "d"}',
            prompt_tokens=50,
            completion_tokens=20,
        ),
    )
    conv_id = db.create_conversation("Test", db_path)

    task = services.extract_task("x", conv_id, db_path=db_path)

    assert task is None
    rows = db.get_interactions(conv_id, db_path)
    assert rows[0]["status"] == "error"


def test_extract_task_echec_api_journalise_sans_texte_brut(monkeypatch, db_path):
    def faux_appel_qui_plante(prompt, model="openai/gpt-oss-20b"):
        raise ConnectionError("Réseau indisponible")

    monkeypatch.setattr(services, "call_groq_full", faux_appel_qui_plante)
    conv_id = db.create_conversation("Test", db_path)

    task = services.extract_task("x", conv_id, db_path=db_path)

    assert task is None
    rows = db.get_interactions(conv_id, db_path)
    assert rows[0]["status"] == "error"
    assert rows[0]["output_text"] is None  # rien à journaliser : Groq n'a jamais répondu
    assert "API Groq" in rows[0]["error_message"]