"""
CLI menus - all interactive menu screens for the Quiz Master app.
"""

from typing import Optional
from quiz_app import models, display as ui
from quiz_app.engine import run_quiz


# ── Helpers ──────────────────────────────────────────────────────────────────

def _get_int(label: str, default: int = 0, min_val: int = 0, max_val: int = 99999) -> int:
    while True:
        raw = ui.prompt(label, str(default))
        try:
            val = int(raw)
            if min_val <= val <= max_val:
                return val
            ui.error(f"Please enter a number between {min_val} and {max_val}.")
        except ValueError:
            ui.error("Please enter a valid number.")


def _confirm(msg: str) -> bool:
    raw = ui.prompt(f"{msg} (y/n)", "n").lower()
    return raw in ("y", "yes")


def _pick_category() -> Optional[int]:
    """Prompt user to pick a category. Returns category_id or None."""
    cats = models.get_all_categories()
    if not cats:
        return None
    print(f"\n  {ui.DIM}Available categories:{ui.RESET}")
    print(f"  {ui.DIM}[0] No category{ui.RESET}")
    for c in cats:
        print(f"  {ui.DIM}[{c.id}] {c.name}{ui.RESET}")
    print()
    raw = ui.prompt("Category ID (0 for none)", "0")
    try:
        cat_id = int(raw)
        if cat_id == 0:
            return None
        if any(c.id == cat_id for c in cats):
            return cat_id
    except ValueError:
        pass
    ui.warning("Invalid category ID, defaulting to None.")
    return None


# ── Category Management ───────────────────────────────────────────────────────

def menu_categories() -> None:
    while True:
        choice = ui.menu("Category Management", [
            ("list",   "List all categories"),
            ("add",    "Add new category"),
            ("edit",   "Edit a category"),
            ("delete", "Delete a category"),
        ], icon="🗂")

        if choice == "back":
            break
        elif choice == "1":   # list
            _list_categories()
        elif choice == "2":   # add
            _add_category()
        elif choice == "3":   # edit
            _edit_category()
        elif choice == "4":   # delete
            _delete_category()


def _list_categories() -> None:
    ui.section_header("All Categories", "🗂")
    cats = models.get_all_categories()
    if not cats:
        ui.info("No categories yet. Add some!")
        ui.press_enter()
        return
    ui.table(
        ["ID", "Name", "Description", "Created"],
        [[str(c.id), c.name, c.description[:40], c.created_at[:10]] for c in cats],
        col_widths=[6, 20, 44, 14],
    )
    ui.press_enter()


def _add_category() -> None:
    ui.section_header("Add Category", "➕")
    name = ui.prompt("Category name")
    if not name:
        ui.error("Name cannot be empty.")
        return
    desc = ui.prompt("Description (optional)")
    try:
        cat = models.create_category(name, desc)
        ui.success(f"Category '{cat.name}' created (ID: {cat.id}).")
    except Exception as e:
        ui.error(f"Failed: {e}")
    ui.press_enter()


def _edit_category() -> None:
    ui.section_header("Edit Category", "✏️")
    _list_categories()
    raw = ui.prompt("Enter category ID to edit")
    try:
        cid = int(raw)
    except ValueError:
        ui.error("Invalid ID.")
        return
    cat = models.get_category_by_id(cid)
    if not cat:
        ui.error("Category not found.")
        return
    name = ui.prompt("New name", cat.name)
    desc = ui.prompt("New description", cat.description)
    if models.update_category(cid, name, desc):
        ui.success("Category updated.")
    else:
        ui.error("Update failed.")
    ui.press_enter()


def _delete_category() -> None:
    ui.section_header("Delete Category", "🗑️")
    _list_categories()
    raw = ui.prompt("Enter category ID to delete")
    try:
        cid = int(raw)
    except ValueError:
        ui.error("Invalid ID.")
        return
    if not _confirm("Are you sure?"):
        return
    if models.delete_category(cid):
        ui.success("Category deleted.")
    else:
        ui.error("Deletion failed.")
    ui.press_enter()


# ── Quiz Management ───────────────────────────────────────────────────────────

def menu_quizzes() -> None:
    while True:
        choice = ui.menu("Quiz Management", [
            ("list",   "List all quizzes"),
            ("add",    "Create new quiz"),
            ("edit",   "Edit a quiz"),
            ("delete", "Delete a quiz"),
            ("questions", "Manage questions for a quiz"),
        ], icon="📚")

        if choice == "back":
            break
        elif choice == "1":
            _list_quizzes()
        elif choice == "2":
            _add_quiz()
        elif choice == "3":
            _edit_quiz()
        elif choice == "4":
            _delete_quiz()
        elif choice == "5":
            _pick_quiz_for_questions()


def _list_quizzes(return_id: bool = False) -> Optional[int]:
    ui.section_header("All Quizzes", "📚")
    quizzes = models.get_all_quizzes()
    if not quizzes:
        ui.info("No quizzes yet. Create one first!")
        if not return_id:
            ui.press_enter()
        return None
    ui.table(
        ["ID", "Title", "Category", "Questions", "Time Limit", "Shuffle", "Created"],
        [
            [
                str(q.id),
                q.title[:30],
                q.category_name[:15],
                str(len(models.get_questions_for_quiz(q.id))),
                f"{q.time_limit_seconds}s" if q.time_limit_seconds else "None",
                "Yes" if q.randomize_questions else "No",
                q.created_at[:10],
            ]
            for q in quizzes
        ],
        col_widths=[6, 34, 18, 12, 12, 10, 14],
    )
    if return_id:
        raw = ui.prompt("Enter quiz ID (0 to cancel)", "0")
        try:
            qid = int(raw)
            return qid if qid > 0 else None
        except ValueError:
            return None
    ui.press_enter()
    return None


def _add_quiz() -> None:
    ui.section_header("Create New Quiz", "➕")
    title = ui.prompt("Quiz title")
    if not title:
        ui.error("Title cannot be empty.")
        return
    desc = ui.prompt("Description (optional)")
    cat_id = _pick_category()
    time_limit = _get_int("Time limit for entire quiz (seconds, 0 = no limit)", 0)
    randomize = _confirm("Randomize question order?")

    quiz = models.create_quiz(title, desc, cat_id, time_limit, randomize)
    ui.success(f"Quiz '{quiz.title}' created (ID: {quiz.id}).")
    if _confirm("Add questions now?"):
        menu_questions(quiz.id)


def _edit_quiz() -> None:
    ui.section_header("Edit Quiz", "✏️")
    qid = _list_quizzes(return_id=True)
    if not qid:
        return
    quiz = models.get_quiz_by_id(qid)
    if not quiz:
        ui.error("Quiz not found.")
        return
    title = ui.prompt("New title", quiz.title)
    desc = ui.prompt("New description", quiz.description)
    cat_id = _pick_category()
    time_limit = _get_int("New time limit (seconds, 0 = no limit)", quiz.time_limit_seconds)
    randomize = _confirm("Randomize question order?")

    if models.update_quiz(qid, title, desc, cat_id, time_limit, randomize):
        ui.success("Quiz updated.")
    else:
        ui.error("Update failed.")
    ui.press_enter()


def _delete_quiz() -> None:
    ui.section_header("Delete Quiz", "🗑️")
    qid = _list_quizzes(return_id=True)
    if not qid:
        return
    if not _confirm("Delete this quiz and ALL its questions?"):
        return
    if models.delete_quiz(qid):
        ui.success("Quiz deleted.")
    else:
        ui.error("Deletion failed.")
    ui.press_enter()


def _pick_quiz_for_questions() -> None:
    qid = _list_quizzes(return_id=True)
    if qid:
        menu_questions(qid)


# ── Question Management ───────────────────────────────────────────────────────

def menu_questions(quiz_id: int) -> None:
    quiz = models.get_quiz_by_id(quiz_id)
    if not quiz:
        ui.error("Quiz not found.")
        return

    while True:
        choice = ui.menu(f"Questions: {quiz.title}", [
            ("list",   "List all questions"),
            ("add",    "Add new question"),
            ("edit",   "Edit a question"),
            ("delete", "Delete a question"),
        ], icon="❓")

        if choice == "back":
            break
        elif choice == "1":
            _list_questions(quiz_id)
        elif choice == "2":
            _add_question(quiz_id)
        elif choice == "3":
            _edit_question(quiz_id)
        elif choice == "4":
            _delete_question(quiz_id)


def _list_questions(quiz_id: int, return_id: bool = False) -> Optional[int]:
    ui.section_header("Questions", "❓")
    questions = models.get_questions_for_quiz(quiz_id)
    if not questions:
        ui.info("No questions yet.")
        if not return_id:
            ui.press_enter()
        return None

    for i, q in enumerate(questions, 1):
        correct = [a.answer_text for a in q.answers if a.is_correct]
        print(f"  {ui.B_CYAN}{ui.BOLD}[{q.id}]{ui.RESET} Q{i}: {q.question_text[:60]}")
        print(f"        {ui.DIM}Answers: {len(q.answers)}   Correct: {', '.join(correct)[:40]}{ui.RESET}")
        if q.time_limit_seconds:
            print(f"        {ui.DIM}Time limit: {q.time_limit_seconds}s{ui.RESET}")
        print()

    if return_id:
        raw = ui.prompt("Enter question ID (0 to cancel)", "0")
        try:
            qid = int(raw)
            return qid if qid > 0 else None
        except ValueError:
            return None
    ui.press_enter()
    return None


def _add_question(quiz_id: int) -> None:
    ui.section_header("Add Question", "➕")
    text = ui.prompt("Question text")
    if not text:
        ui.error("Question cannot be empty.")
        return
    explanation = ui.prompt("Explanation (shown after answering, optional)")
    time_limit = _get_int("Time limit for this question (seconds, 0 = no limit)", 0)

    question = models.create_question(quiz_id, text, explanation, time_limit)
    ui.success(f"Question created (ID: {question.id}). Now add answers.")
    _manage_answers(question.id)


def _edit_question(quiz_id: int) -> None:
    ui.section_header("Edit Question", "✏️")
    qid = _list_questions(quiz_id, return_id=True)
    if not qid:
        return
    question = models.get_question_by_id(qid)
    if not question:
        ui.error("Question not found.")
        return
    text = ui.prompt("New question text", question.question_text)
    explanation = ui.prompt("New explanation", question.explanation)
    time_limit = _get_int("New time limit (seconds, 0 = no limit)", question.time_limit_seconds)

    if models.update_question(qid, text, explanation, time_limit):
        ui.success("Question updated.")

    if _confirm("Edit answers too?"):
        _manage_answers(qid)
    else:
        ui.press_enter()


def _delete_question(quiz_id: int) -> None:
    ui.section_header("Delete Question", "🗑️")
    qid = _list_questions(quiz_id, return_id=True)
    if not qid:
        return
    if not _confirm("Delete this question and all its answers?"):
        return
    if models.delete_question(qid):
        ui.success("Question deleted.")
    else:
        ui.error("Deletion failed.")
    ui.press_enter()


# ── Answer Management ─────────────────────────────────────────────────────────

def _manage_answers(question_id: int) -> None:
    while True:
        question = models.get_question_by_id(question_id)
        if not question:
            break

        ui.section_header(f"Answers for: {question.question_text[:50]}", "💬")
        for i, a in enumerate(question.answers, 1):
            correct_tag = f" {ui.B_GREEN}✔ CORRECT{ui.RESET}" if a.is_correct else ""
            print(f"  {ui.B_YELLOW}[{a.id}]{ui.RESET} {a.answer_text}{correct_tag}")
        print()

        choice = ui.menu("Answer Options", [
            ("add",    "Add new answer"),
            ("edit",   "Edit an answer"),
            ("delete", "Delete an answer"),
        ], icon="💬")

        if choice == "back":
            break
        elif choice == "1":
            _add_answer(question_id)
        elif choice == "2":
            _edit_answer(question_id)
        elif choice == "3":
            _delete_answer(question_id)


def _add_answer(question_id: int) -> None:
    text = ui.prompt("Answer text")
    if not text:
        ui.error("Answer cannot be empty.")
        return
    is_correct = _confirm("Is this the correct answer?")
    models.add_answer(question_id, text, is_correct)
    ui.success("Answer added.")


def _edit_answer(question_id: int) -> None:
    raw = ui.prompt("Enter answer ID to edit")
    try:
        aid = int(raw)
    except ValueError:
        ui.error("Invalid ID.")
        return
    answers = models.get_answers_for_question(question_id)
    answer = next((a for a in answers if a.id == aid), None)
    if not answer:
        ui.error("Answer not found.")
        return
    text = ui.prompt("New answer text", answer.answer_text)
    is_correct = _confirm("Is this the correct answer?")
    if models.update_answer(aid, text, is_correct):
        ui.success("Answer updated.")
    else:
        ui.error("Update failed.")


def _delete_answer(question_id: int) -> None:
    raw = ui.prompt("Enter answer ID to delete")
    try:
        aid = int(raw)
    except ValueError:
        ui.error("Invalid ID.")
        return
    if _confirm("Delete this answer?"):
        if models.delete_answer(aid):
            ui.success("Answer deleted.")
        else:
            ui.error("Deletion failed.")


# ── Take Quiz ─────────────────────────────────────────────────────────────────

def menu_take_quiz() -> None:
    ui.section_header("Take a Quiz", "🎯")
    player_name = ui.prompt("Enter your name")
    if not player_name:
        ui.error("Name cannot be empty.")
        ui.press_enter()
        return

    qid = _list_quizzes(return_id=True)
    if not qid:
        return

    run_quiz(qid, player_name)


# ── Leaderboard ───────────────────────────────────────────────────────────────

def menu_leaderboard() -> None:
    while True:
        choice = ui.menu("Leaderboard", [
            ("global",  "Global leaderboard (all quizzes)"),
            ("quiz",    "Leaderboard for a specific quiz"),
            ("player",  "My stats (by player name)"),
        ], icon="🏆")

        if choice == "back":
            break
        elif choice == "1":
            _show_leaderboard()
        elif choice == "2":
            _show_leaderboard_for_quiz()
        elif choice == "3":
            _show_player_stats()


def _show_leaderboard(quiz_id: Optional[int] = None, title: str = "Global Leaderboard") -> None:
    ui.section_header(title, "🏆")
    scores = models.get_leaderboard(quiz_id=quiz_id, limit=15)
    if not scores:
        ui.info("No scores recorded yet. Play a quiz first!")
        ui.press_enter()
        return
    ui.table(
        ["Rank", "Player", "Quiz", "Score", "%", "Time", "Date"],
        [
            [
                f"#{i}",
                s.player_name[:18],
                s.quiz_title[:25],
                f"{s.score}/{s.total_questions}",
                f"{s.percentage:.1f}%",
                f"{int(s.time_taken_seconds)}s",
                s.played_at[:10],
            ]
            for i, s in enumerate(scores, 1)
        ],
        col_widths=[6, 22, 28, 10, 10, 10, 14],
    )
    ui.press_enter()


def _show_leaderboard_for_quiz() -> None:
    qid = _list_quizzes(return_id=True)
    if not qid:
        return
    quiz = models.get_quiz_by_id(qid)
    if quiz:
        _show_leaderboard(quiz_id=qid, title=f"Leaderboard: {quiz.title}")


def _show_player_stats() -> None:
    ui.section_header("Player Stats", "👤")
    name = ui.prompt("Enter player name")
    if not name:
        return
    stats = models.get_player_stats(name)
    if not stats or stats["quizzes_taken"] == 0:
        ui.info(f"No stats found for '{name}'.")
        ui.press_enter()
        return

    print(f"\n  {ui.B_WHITE}{ui.BOLD}Stats for: {name}{ui.RESET}\n")
    print(f"  {ui.DIM}Quizzes played  : {ui.CYAN}{stats['quizzes_taken']}{ui.RESET}")
    print(f"  {ui.DIM}Average score   : {ui.CYAN}{stats['avg_percentage']}%{ui.RESET}")
    print(f"  {ui.DIM}Best score      : {ui.CYAN}{stats['best_percentage']}%{ui.RESET}")
    print(f"  {ui.DIM}Total correct   : {ui.CYAN}{stats['total_correct']} / {stats['total_questions']}{ui.RESET}")
    print()
    ui.press_enter()
