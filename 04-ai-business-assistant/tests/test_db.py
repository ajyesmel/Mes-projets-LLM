import sqlite3
import pytest
from src import db


@pytest.fixture
def db_path(tmp_path):
    path = tmp_path / "test.db"
    db.init_db(path)
    return path


def test_creation_et_lecture_conversation(db_path):
    conv_id = db.create_conversation("Client Abidjan", db_path)
    convs = db.list_conversations(db_path)
    assert len(convs) == 1
    assert convs[0]["id"] == conv_id
    assert convs[0]["title"] == "Client Abidjan"


def test_log_interaction_ok(db_path):
    conv_id = db.create_conversation("Test", db_path)
    db.log_interaction(conv_id, "summarize", "texte", "m", "ok",
                       output_text="resume", latency_ms=120,
                       prompt_tokens=10, completion_tokens=5, db_path=db_path)
    rows = db.get_interactions(conv_id, db_path)
    assert rows[0]["output_text"] == "resume"
    assert rows[0]["status"] == "ok"


def test_stats_avec_erreur(db_path):
    conv_id = db.create_conversation("Test", db_path)
    db.log_interaction(conv_id, "summarize", "a", "m", "ok",
                       latency_ms=100, prompt_tokens=10,
                       completion_tokens=5, db_path=db_path)
    db.log_interaction(conv_id, "summarize", "b", "m", "error",
                       error_message="timeout", db_path=db_path)
    s = db.get_stats(db_path)
    assert s["total"] == 2
    assert s["errors"] == 1
    assert s["prompt_tokens"] == 10


def test_stats_base_vide(db_path):
    s = db.get_stats(db_path)
    assert s["total"] == 0 and s["errors"] == 0


def test_conversation_inexistante_refusee(db_path):
    with pytest.raises(sqlite3.IntegrityError):
        db.log_interaction(999, "summarize", "a", "m", "ok", db_path=db_path)


def test_statut_invalide_refuse(db_path):
    conv_id = db.create_conversation("Test", db_path)
    with pytest.raises(sqlite3.IntegrityError):
        db.log_interaction(conv_id, "summarize", "a", "m", "bizarre", db_path=db_path)


def test_get_stats_by_task_regroupe_correctement(db_path):
    conv_id = db.create_conversation("Test", db_path)
    db.log_interaction(conv_id, "summarize", "a", "m", "ok",
                       latency_ms=100, db_path=db_path)
    db.log_interaction(conv_id, "summarize", "b", "m", "error",
                       error_message="timeout", db_path=db_path)
    db.log_interaction(conv_id, "email", "c", "m", "ok",
                       latency_ms=200, db_path=db_path)

    stats = {row["task"]: row for row in db.get_stats_by_task(db_path)}

    assert stats["summarize"]["total"] == 2
    assert stats["summarize"]["errors"] == 1
    assert stats["email"]["total"] == 1
    assert stats["email"]["errors"] == 0


def test_get_stats_by_task_base_vide(db_path):
    assert db.get_stats_by_task(db_path) == []