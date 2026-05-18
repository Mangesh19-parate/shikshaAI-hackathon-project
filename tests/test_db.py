import pytest
import os
import sqlite3
from app.db import init_db, save_lesson, get_lessons, get_lesson_count, clear_all_lessons, DB_PATH

@pytest.fixture(autouse=True)
def setup_db(request):
    """Ensure a clean test database for each test."""
    from pathlib import Path
    import uuid
    original_path = DB_PATH
    test_db_file = Path(f"data/test_lessons_{uuid.uuid4().hex}.db")
    import app.db
    app.db.DB_PATH = test_db_file
    
    init_db()
    clear_all_lessons()
    
    yield
    
    # Try cleanup, but don't fail if Windows has it locked
    app.db.DB_PATH = original_path
    try:
        if test_db_file.exists():
            test_db_file.unlink()
    except:
        pass

def test_db_initialization():
    import app.db
    assert app.db.DB_PATH.exists()
    with sqlite3.connect(str(app.db.DB_PATH)) as conn:
        cursor = conn.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='lessons'")
        assert cursor.fetchone() is not None

def test_save_and_retrieve_lesson():
    save_lesson(
        question="What is photosynthesis?",
        answer="A process used by plants...",
        language="English",
        grade="Grade 10",
        subject="Science",
        word_count=5,
        qc_passed=True
    )
    
    assert get_lesson_count() == 1
    lessons = get_lessons()
    assert len(lessons) == 1
    assert lessons[0]["question"] == "What is photosynthesis?"
    assert lessons[0]["subject"] == "Science"
    assert lessons[0]["qc_passed"] == 1

def test_clear_lessons():
    save_lesson("Q1", "A1")
    save_lesson("Q2", "A2")
    assert get_lesson_count() == 2
    clear_all_lessons()
    assert get_lesson_count() == 0

def test_get_lessons_with_limit():
    for i in range(15):
        save_lesson(f"Q{i}", f"A{i}")
    
    limited = get_lessons(limit=5)
    assert len(limited) == 5
    # Should be newest first
    assert limited[0]["question"] == "Q14"
