"""
Models module - data classes and CRUD operations for each entity.
"""

from __future__ import annotations
import sqlite3
from dataclasses import dataclass, field
from typing import List, Optional
from quiz_app.database import get_connection


# ---------------------------------------------------------------------------
# Data Classes
# ---------------------------------------------------------------------------

@dataclass
class Category:
    id: int
    name: str
    description: str
    created_at: str = ""

    @staticmethod
    def from_row(row: sqlite3.Row) -> "Category":
        return Category(
            id=row["id"],
            name=row["name"],
            description=row["description"] or "",
            created_at=row["created_at"],
        )


@dataclass
class Answer:
    id: int
    question_id: int
    answer_text: str
    is_correct: bool

    @staticmethod
    def from_row(row: sqlite3.Row) -> "Answer":
        return Answer(
            id=row["id"],
            question_id=row["question_id"],
            answer_text=row["answer_text"],
            is_correct=bool(row["is_correct"]),
        )


@dataclass
class Question:
    id: int
    quiz_id: int
    question_text: str
    explanation: str
    time_limit_seconds: int
    created_at: str = ""
    answers: List[Answer] = field(default_factory=list)

    @staticmethod
    def from_row(row: sqlite3.Row) -> "Question":
        return Question(
            id=row["id"],
            quiz_id=row["quiz_id"],
            question_text=row["question_text"],
            explanation=row["explanation"] or "",
            time_limit_seconds=row["time_limit_seconds"],
            created_at=row["created_at"],
        )


@dataclass
class Quiz:
    id: int
    title: str
    description: str
    category_id: Optional[int]
    category_name: str
    time_limit_seconds: int
    randomize_questions: bool
    created_at: str = ""
    questions: List[Question] = field(default_factory=list)

    @staticmethod
    def from_row(row: sqlite3.Row) -> "Quiz":
        return Quiz(
            id=row["id"],
            title=row["title"],
            description=row["description"] or "",
            category_id=row["category_id"],
            category_name=row["category_name"] if "category_name" in row.keys() else "",
            time_limit_seconds=row["time_limit_seconds"],
            randomize_questions=bool(row["randomize_questions"]),
            created_at=row["created_at"],
        )


@dataclass
class Score:
    id: int
    player_name: str
    quiz_id: int
    quiz_title: str
    score: int
    total_questions: int
    percentage: float
    time_taken_seconds: float
    played_at: str

    @staticmethod
    def from_row(row: sqlite3.Row) -> "Score":
        return Score(
            id=row["id"],
            player_name=row["player_name"],
            quiz_id=row["quiz_id"],
            quiz_title=row["quiz_title"],
            score=row["score"],
            total_questions=row["total_questions"],
            percentage=row["percentage"],
            time_taken_seconds=row["time_taken_seconds"],
            played_at=row["played_at"],
        )


# ---------------------------------------------------------------------------
# Category CRUD
# ---------------------------------------------------------------------------

def create_category(name: str, description: str = "") -> Category:
    with get_connection() as conn:
        cursor = conn.execute(
            "INSERT INTO categories (name, description) VALUES (?, ?)",
            (name.strip(), description.strip()),
        )
        conn.commit()
        row = conn.execute("SELECT * FROM categories WHERE id = ?", (cursor.lastrowid,)).fetchone()
        return Category.from_row(row)


def get_all_categories() -> List[Category]:
    with get_connection() as conn:
        rows = conn.execute("SELECT * FROM categories ORDER BY name").fetchall()
        return [Category.from_row(r) for r in rows]


def get_category_by_id(category_id: int) -> Optional[Category]:
    with get_connection() as conn:
        row = conn.execute("SELECT * FROM categories WHERE id = ?", (category_id,)).fetchone()
        return Category.from_row(row) if row else None


def update_category(category_id: int, name: str, description: str) -> bool:
    with get_connection() as conn:
        conn.execute(
            "UPDATE categories SET name = ?, description = ? WHERE id = ?",
            (name.strip(), description.strip(), category_id),
        )
        conn.commit()
        return conn.execute("SELECT changes()").fetchone()[0] > 0


def delete_category(category_id: int) -> bool:
    with get_connection() as conn:
        conn.execute("DELETE FROM categories WHERE id = ?", (category_id,))
        conn.commit()
        return conn.execute("SELECT changes()").fetchone()[0] > 0


# ---------------------------------------------------------------------------
# Quiz CRUD
# ---------------------------------------------------------------------------

def create_quiz(
    title: str,
    description: str = "",
    category_id: Optional[int] = None,
    time_limit_seconds: int = 0,
    randomize_questions: bool = False,
) -> Quiz:
    with get_connection() as conn:
        cursor = conn.execute(
            """INSERT INTO quizzes (title, description, category_id, time_limit_seconds, randomize_questions)
               VALUES (?, ?, ?, ?, ?)""",
            (title.strip(), description.strip(), category_id, time_limit_seconds, int(randomize_questions)),
        )
        conn.commit()
        return get_quiz_by_id(cursor.lastrowid)


def get_all_quizzes() -> List[Quiz]:
    with get_connection() as conn:
        rows = conn.execute("""
            SELECT q.*, COALESCE(c.name, 'Uncategorized') AS category_name
            FROM quizzes q
            LEFT JOIN categories c ON q.category_id = c.id
            ORDER BY q.created_at DESC
        """).fetchall()
        return [Quiz.from_row(r) for r in rows]


def get_quiz_by_id(quiz_id: int) -> Optional[Quiz]:
    with get_connection() as conn:
        row = conn.execute("""
            SELECT q.*, COALESCE(c.name, 'Uncategorized') AS category_name
            FROM quizzes q
            LEFT JOIN categories c ON q.category_id = c.id
            WHERE q.id = ?
        """, (quiz_id,)).fetchone()
        return Quiz.from_row(row) if row else None


def update_quiz(
    quiz_id: int,
    title: str,
    description: str,
    category_id: Optional[int],
    time_limit_seconds: int,
    randomize_questions: bool,
) -> bool:
    with get_connection() as conn:
        conn.execute(
            """UPDATE quizzes SET title=?, description=?, category_id=?,
               time_limit_seconds=?, randomize_questions=? WHERE id=?""",
            (title.strip(), description.strip(), category_id, time_limit_seconds, int(randomize_questions), quiz_id),
        )
        conn.commit()
        return conn.execute("SELECT changes()").fetchone()[0] > 0


def delete_quiz(quiz_id: int) -> bool:
    with get_connection() as conn:
        conn.execute("DELETE FROM quizzes WHERE id = ?", (quiz_id,))
        conn.commit()
        return conn.execute("SELECT changes()").fetchone()[0] > 0


# ---------------------------------------------------------------------------
# Question CRUD
# ---------------------------------------------------------------------------

def create_question(
    quiz_id: int,
    question_text: str,
    explanation: str = "",
    time_limit_seconds: int = 0,
) -> Question:
    with get_connection() as conn:
        cursor = conn.execute(
            """INSERT INTO questions (quiz_id, question_text, explanation, time_limit_seconds)
               VALUES (?, ?, ?, ?)""",
            (quiz_id, question_text.strip(), explanation.strip(), time_limit_seconds),
        )
        conn.commit()
        row = conn.execute("SELECT * FROM questions WHERE id = ?", (cursor.lastrowid,)).fetchone()
        return Question.from_row(row)


def get_questions_for_quiz(quiz_id: int) -> List[Question]:
    with get_connection() as conn:
        rows = conn.execute(
            "SELECT * FROM questions WHERE quiz_id = ? ORDER BY created_at", (quiz_id,)
        ).fetchall()
        questions = [Question.from_row(r) for r in rows]
        for q in questions:
            q.answers = get_answers_for_question(q.id)
        return questions


def get_question_by_id(question_id: int) -> Optional[Question]:
    with get_connection() as conn:
        row = conn.execute("SELECT * FROM questions WHERE id = ?", (question_id,)).fetchone()
        if not row:
            return None
        q = Question.from_row(row)
        q.answers = get_answers_for_question(q.id)
        return q


def update_question(
    question_id: int,
    question_text: str,
    explanation: str,
    time_limit_seconds: int,
) -> bool:
    with get_connection() as conn:
        conn.execute(
            "UPDATE questions SET question_text=?, explanation=?, time_limit_seconds=? WHERE id=?",
            (question_text.strip(), explanation.strip(), time_limit_seconds, question_id),
        )
        conn.commit()
        return conn.execute("SELECT changes()").fetchone()[0] > 0


def delete_question(question_id: int) -> bool:
    with get_connection() as conn:
        conn.execute("DELETE FROM questions WHERE id = ?", (question_id,))
        conn.commit()
        return conn.execute("SELECT changes()").fetchone()[0] > 0


# ---------------------------------------------------------------------------
# Answer CRUD
# ---------------------------------------------------------------------------

def add_answer(question_id: int, answer_text: str, is_correct: bool = False) -> Answer:
    with get_connection() as conn:
        cursor = conn.execute(
            "INSERT INTO answers (question_id, answer_text, is_correct) VALUES (?, ?, ?)",
            (question_id, answer_text.strip(), int(is_correct)),
        )
        conn.commit()
        row = conn.execute("SELECT * FROM answers WHERE id = ?", (cursor.lastrowid,)).fetchone()
        return Answer.from_row(row)


def get_answers_for_question(question_id: int) -> List[Answer]:
    with get_connection() as conn:
        rows = conn.execute(
            "SELECT * FROM answers WHERE question_id = ? ORDER BY id", (question_id,)
        ).fetchall()
        return [Answer.from_row(r) for r in rows]


def update_answer(answer_id: int, answer_text: str, is_correct: bool) -> bool:
    with get_connection() as conn:
        conn.execute(
            "UPDATE answers SET answer_text=?, is_correct=? WHERE id=?",
            (answer_text.strip(), int(is_correct), answer_id),
        )
        conn.commit()
        return conn.execute("SELECT changes()").fetchone()[0] > 0


def delete_answer(answer_id: int) -> bool:
    with get_connection() as conn:
        conn.execute("DELETE FROM answers WHERE id = ?", (answer_id,))
        conn.commit()
        return conn.execute("SELECT changes()").fetchone()[0] > 0


def delete_answers_for_question(question_id: int) -> None:
    with get_connection() as conn:
        conn.execute("DELETE FROM answers WHERE question_id = ?", (question_id,))
        conn.commit()


# ---------------------------------------------------------------------------
# Score CRUD
# ---------------------------------------------------------------------------

def save_score(
    player_name: str,
    quiz_id: int,
    quiz_title: str,
    score: int,
    total_questions: int,
    time_taken_seconds: float,
) -> Score:
    percentage = (score / total_questions * 100) if total_questions > 0 else 0.0
    with get_connection() as conn:
        cursor = conn.execute(
            """INSERT INTO scores (player_name, quiz_id, quiz_title, score, total_questions, percentage, time_taken_seconds)
               VALUES (?, ?, ?, ?, ?, ?, ?)""",
            (player_name, quiz_id, quiz_title, score, total_questions, percentage, time_taken_seconds),
        )
        conn.commit()
        row = conn.execute("SELECT * FROM scores WHERE id = ?", (cursor.lastrowid,)).fetchone()
        return Score.from_row(row)


def get_leaderboard(quiz_id: Optional[int] = None, limit: int = 10) -> List[Score]:
    with get_connection() as conn:
        if quiz_id:
            rows = conn.execute(
                """SELECT * FROM scores WHERE quiz_id = ?
                   ORDER BY percentage DESC, time_taken_seconds ASC LIMIT ?""",
                (quiz_id, limit),
            ).fetchall()
        else:
            rows = conn.execute(
                """SELECT * FROM scores
                   ORDER BY percentage DESC, time_taken_seconds ASC LIMIT ?""",
                (limit,),
            ).fetchall()
        return [Score.from_row(r) for r in rows]


def get_player_stats(player_name: str) -> dict:
    with get_connection() as conn:
        row = conn.execute("""
            SELECT
                COUNT(*) as quizzes_taken,
                ROUND(AVG(percentage), 2) as avg_percentage,
                MAX(percentage) as best_percentage,
                SUM(score) as total_correct,
                SUM(total_questions) as total_questions
            FROM scores WHERE player_name = ?
        """, (player_name,)).fetchone()
        return dict(row) if row else {}
