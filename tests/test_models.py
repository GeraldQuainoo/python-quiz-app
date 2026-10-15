"""
Unit tests for Quiz Master app.
Run with: python -m pytest tests/ -v
"""

import pytest
import os
import tempfile
from pathlib import Path


# ── Fixture: use a temp DB so tests are isolated ──────────────────────────────

@pytest.fixture(autouse=True)
def temp_db(monkeypatch, tmp_path):
    """Redirect DB_PATH to a temporary file for each test."""
    tmp_db = tmp_path / "test_quiz.db"
    import quiz_app.database as db_module
    monkeypatch.setattr(db_module, "DB_PATH", tmp_db)
    db_module.initialize_db()
    yield tmp_db


# ── Category Tests ────────────────────────────────────────────────────────────

class TestCategory:
    def test_create_category(self):
        from quiz_app.models import create_category, get_all_categories
        cat = create_category("Science", "About science")
        assert cat.id is not None
        assert cat.name == "Science"
        assert cat.description == "About science"

    def test_list_categories(self):
        from quiz_app.models import create_category, get_all_categories
        create_category("Math")
        create_category("History")
        cats = get_all_categories()
        assert len(cats) == 2

    def test_update_category(self):
        from quiz_app.models import create_category, update_category, get_category_by_id
        cat = create_category("Old Name")
        assert update_category(cat.id, "New Name", "New Desc")
        updated = get_category_by_id(cat.id)
        assert updated.name == "New Name"

    def test_delete_category(self):
        from quiz_app.models import create_category, delete_category, get_category_by_id
        cat = create_category("To Delete")
        assert delete_category(cat.id)
        assert get_category_by_id(cat.id) is None

    def test_duplicate_category_raises(self):
        from quiz_app.models import create_category
        create_category("Unique")
        with pytest.raises(Exception):
            create_category("Unique")


# ── Quiz Tests ────────────────────────────────────────────────────────────────

class TestQuiz:
    def test_create_quiz(self):
        from quiz_app.models import create_quiz, get_quiz_by_id
        quiz = create_quiz("My Quiz", "A quiz", None, 60, True)
        assert quiz.id is not None
        assert quiz.title == "My Quiz"
        assert quiz.time_limit_seconds == 60
        assert quiz.randomize_questions is True

    def test_list_quizzes(self):
        from quiz_app.models import create_quiz, get_all_quizzes
        create_quiz("Quiz 1")
        create_quiz("Quiz 2")
        assert len(get_all_quizzes()) == 2

    def test_update_quiz(self):
        from quiz_app.models import create_quiz, update_quiz, get_quiz_by_id
        quiz = create_quiz("Original")
        update_quiz(quiz.id, "Updated", "New desc", None, 30, False)
        updated = get_quiz_by_id(quiz.id)
        assert updated.title == "Updated"
        assert updated.time_limit_seconds == 30

    def test_delete_quiz(self):
        from quiz_app.models import create_quiz, delete_quiz, get_quiz_by_id
        quiz = create_quiz("To Delete")
        assert delete_quiz(quiz.id)
        assert get_quiz_by_id(quiz.id) is None

    def test_quiz_with_category(self):
        from quiz_app.models import create_category, create_quiz, get_quiz_by_id
        cat = create_category("Tech")
        quiz = create_quiz("Tech Quiz", category_id=cat.id)
        fetched = get_quiz_by_id(quiz.id)
        assert fetched.category_id == cat.id
        assert fetched.category_name == "Tech"


# ── Question Tests ────────────────────────────────────────────────────────────

class TestQuestion:
    def setup_method(self):
        from quiz_app.models import create_quiz
        self.quiz = create_quiz("Test Quiz")

    def test_create_question(self):
        from quiz_app.models import create_question, get_questions_for_quiz
        q = create_question(self.quiz.id, "What is 2+2?", "Basic arithmetic.", 30)
        assert q.id is not None
        assert q.question_text == "What is 2+2?"
        assert q.time_limit_seconds == 30

    def test_list_questions(self):
        from quiz_app.models import create_question, get_questions_for_quiz
        create_question(self.quiz.id, "Q1")
        create_question(self.quiz.id, "Q2")
        create_question(self.quiz.id, "Q3")
        questions = get_questions_for_quiz(self.quiz.id)
        assert len(questions) == 3

    def test_update_question(self):
        from quiz_app.models import create_question, update_question, get_question_by_id
        q = create_question(self.quiz.id, "Original question?")
        update_question(q.id, "Updated question?", "New explanation", 45)
        updated = get_question_by_id(q.id)
        assert updated.question_text == "Updated question?"
        assert updated.explanation == "New explanation"

    def test_delete_question(self):
        from quiz_app.models import create_question, delete_question, get_question_by_id
        q = create_question(self.quiz.id, "Deletable?")
        assert delete_question(q.id)
        assert get_question_by_id(q.id) is None

    def test_cascade_delete_with_quiz(self):
        from quiz_app.models import create_question, delete_quiz, get_questions_for_quiz
        create_question(self.quiz.id, "Q in deleted quiz")
        delete_quiz(self.quiz.id)
        # Questions should be gone too
        questions = get_questions_for_quiz(self.quiz.id)
        assert questions == []


# ── Answer Tests ──────────────────────────────────────────────────────────────

class TestAnswer:
    def setup_method(self):
        from quiz_app.models import create_quiz, create_question
        self.quiz = create_quiz("Test Quiz")
        self.question = create_question(self.quiz.id, "What color is the sky?")

    def test_add_answer(self):
        from quiz_app.models import add_answer, get_answers_for_question
        ans = add_answer(self.question.id, "Blue", is_correct=True)
        assert ans.id is not None
        assert ans.answer_text == "Blue"
        assert ans.is_correct is True

    def test_multiple_answers(self):
        from quiz_app.models import add_answer, get_answers_for_question
        add_answer(self.question.id, "Blue", True)
        add_answer(self.question.id, "Red", False)
        add_answer(self.question.id, "Green", False)
        answers = get_answers_for_question(self.question.id)
        assert len(answers) == 3
        correct = [a for a in answers if a.is_correct]
        assert len(correct) == 1

    def test_update_answer(self):
        from quiz_app.models import add_answer, update_answer, get_answers_for_question
        ans = add_answer(self.question.id, "Original", False)
        update_answer(ans.id, "Updated", True)
        answers = get_answers_for_question(self.question.id)
        updated = next(a for a in answers if a.id == ans.id)
        assert updated.answer_text == "Updated"
        assert updated.is_correct is True

    def test_delete_answer(self):
        from quiz_app.models import add_answer, delete_answer, get_answers_for_question
        ans = add_answer(self.question.id, "Deletable", False)
        assert delete_answer(ans.id)
        answers = get_answers_for_question(self.question.id)
        assert all(a.id != ans.id for a in answers)


# ── Score / Leaderboard Tests ─────────────────────────────────────────────────

class TestScores:
    def setup_method(self):
        from quiz_app.models import create_quiz
        self.quiz = create_quiz("Score Test Quiz")

    def test_save_score(self):
        from quiz_app.models import save_score
        score = save_score("Alice", self.quiz.id, "Score Test Quiz", 8, 10, 45.0)
        assert score.id is not None
        assert score.player_name == "Alice"
        assert score.percentage == 80.0

    def test_leaderboard_order(self):
        from quiz_app.models import save_score, get_leaderboard
        save_score("Alice", self.quiz.id, "Quiz", 6, 10, 30.0)   # 60%
        save_score("Bob",   self.quiz.id, "Quiz", 9, 10, 20.0)   # 90%
        save_score("Carol", self.quiz.id, "Quiz", 9, 10, 15.0)   # 90% faster

        lb = get_leaderboard(quiz_id=self.quiz.id)
        assert lb[0].player_name == "Carol"   # same % but faster
        assert lb[1].player_name == "Bob"
        assert lb[2].player_name == "Alice"

    def test_global_leaderboard(self):
        from quiz_app.models import create_quiz, save_score, get_leaderboard
        quiz2 = create_quiz("Second Quiz")
        save_score("Alice", self.quiz.id, "Quiz 1", 5, 10, 30.0)
        save_score("Bob",   quiz2.id,     "Quiz 2", 9, 10, 20.0)
        lb = get_leaderboard()
        assert len(lb) == 2

    def test_player_stats(self):
        from quiz_app.models import save_score, get_player_stats
        save_score("Alice", self.quiz.id, "Quiz", 7, 10, 30.0)
        save_score("Alice", self.quiz.id, "Quiz", 9, 10, 25.0)
        stats = get_player_stats("Alice")
        assert stats["quizzes_taken"] == 2
        assert stats["best_percentage"] == 90.0
