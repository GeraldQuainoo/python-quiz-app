"""
Quiz Engine - handles the interactive quiz-taking session with timer,
scoring, and result display.
"""

import time
import threading
import random
from typing import Optional

from quiz_app import models, display as ui


# ── Timer helper ─────────────────────────────────────────────────────────────

class QuizTimer:
    """Non-blocking countdown timer that signals when time is up."""

    def __init__(self, seconds: int):
        self.seconds = seconds
        self.remaining = seconds
        self.expired = False
        self._stop_event = threading.Event()
        self._thread = threading.Thread(target=self._run, daemon=True)

    def start(self) -> None:
        self._thread.start()

    def stop(self) -> None:
        self._stop_event.set()

    def _run(self) -> None:
        while self.remaining > 0 and not self._stop_event.is_set():
            time.sleep(1)
            if not self._stop_event.is_set():
                self.remaining -= 1
        if self.remaining <= 0:
            self.expired = True

    def display_remaining(self) -> str:
        mins, secs = divmod(self.remaining, 60)
        color = ui.B_RED if self.remaining <= 10 else ui.B_YELLOW
        return f"{color}{ui.BOLD}⏱  {mins:02d}:{secs:02d}{ui.RESET}"


# ── Core engine ──────────────────────────────────────────────────────────────

def run_quiz(quiz_id: int, player_name: str) -> None:
    """Run a complete quiz session for the given player."""
    quiz = models.get_quiz_by_id(quiz_id)
    if not quiz:
        ui.error("Quiz not found.")
        return

    questions = models.get_questions_for_quiz(quiz_id)
    if not questions:
        ui.error("This quiz has no questions yet. Add some questions first!")
        return

    # Validate that each question has at least 2 answers and one correct
    valid_questions = []
    for q in questions:
        if len(q.answers) >= 2 and any(a.is_correct for a in q.answers):
            valid_questions.append(q)

    if not valid_questions:
        ui.error("No valid questions found (each question needs ≥2 answers and 1 correct answer).")
        return

    if quiz.randomize_questions:
        random.shuffle(valid_questions)

    # ── Quiz intro screen ────────────────────────────────────────────────────
    ui.clear()
    ui.banner()
    ui.section_header(f"Quiz: {quiz.title}", "🎯")
    print(f"  {ui.WHITE}{quiz.description}{ui.RESET}" if quiz.description else "")
    print(f"  {ui.DIM}Category : {ui.CYAN}{quiz.category_name}{ui.RESET}")
    print(f"  {ui.DIM}Questions: {ui.CYAN}{len(valid_questions)}{ui.RESET}")
    if quiz.time_limit_seconds:
        mins, secs = divmod(quiz.time_limit_seconds, 60)
        print(f"  {ui.DIM}Quiz Time: {ui.B_YELLOW}{mins:02d}:{secs:02d}{ui.RESET}")
    print(f"  {ui.DIM}Shuffle  : {'Yes' if quiz.randomize_questions else 'No'}{ui.RESET}")
    print()
    print(f"  {ui.B_CYAN}{ui.BOLD}Player: {player_name}{ui.RESET}")
    print()
    ui.hr()
    ui.countdown(3)

    # ── Session timers ───────────────────────────────────────────────────────
    quiz_timer: Optional[QuizTimer] = None
    if quiz.time_limit_seconds:
        quiz_timer = QuizTimer(quiz.time_limit_seconds)
        quiz_timer.start()

    session_start = time.time()
    score = 0
    results = []  # list of (question, chosen_answer, is_correct)

    # ── Question loop ────────────────────────────────────────────────────────
    for q_index, question in enumerate(valid_questions, 1):
        # Check if overall quiz timer expired
        if quiz_timer and quiz_timer.expired:
            ui.warning("⏰ Time's up! Quiz ended early.")
            break

        ui.clear()
        ui.banner()

        # Progress bar
        progress_pct = (q_index - 1) / len(valid_questions)
        print(f"  {ui.progress_bar(q_index - 1, len(valid_questions))}")
        print(f"  {ui.DIM}Question {q_index} of {len(valid_questions)}{ui.RESET}")
        if quiz_timer:
            print(f"  {quiz_timer.display_remaining()}")
        print()
        ui.hr()

        # Question text
        print(f"\n  {ui.BOLD}{ui.B_WHITE}Q{q_index}. {question.question_text}{ui.RESET}\n")

        # Shuffle answers if quiz has randomize on
        answers = list(question.answers)
        if quiz.randomize_questions:
            random.shuffle(answers)

        # Per-question timer
        q_timer: Optional[QuizTimer] = None
        if question.time_limit_seconds:
            q_timer = QuizTimer(question.time_limit_seconds)
            q_timer.start()
            mins, secs = divmod(question.time_limit_seconds, 60)
            print(f"  {ui.B_YELLOW}⏱ Time for this question: {mins:02d}:{secs:02d}{ui.RESET}\n")

        # Display answer options
        labels = ["A", "B", "C", "D", "E", "F"]
        for i, answer in enumerate(answers):
            label = labels[i] if i < len(labels) else str(i + 1)
            print(f"  {ui.B_YELLOW}{ui.BOLD}[{label}]{ui.RESET}  {answer.answer_text}")
        print()
        ui.hr()

        # Get user input
        valid_labels = [labels[i].lower() for i in range(len(answers))]
        valid_nums   = [str(i + 1) for i in range(len(answers))]
        chosen_answer = None

        while True:
            if q_timer and q_timer.expired:
                print(f"\n  {ui.B_RED}{ui.BOLD}⏰ Time's up for this question!{ui.RESET}")
                break
            if quiz_timer and quiz_timer.expired:
                break

            raw = ui.prompt("Your answer (e.g. A, B, C...)").lower().strip()
            if not raw:
                continue
            if raw in valid_labels:
                idx = valid_labels.index(raw)
                chosen_answer = answers[idx]
                break
            if raw in valid_nums:
                idx = int(raw) - 1
                chosen_answer = answers[idx]
                break
            ui.error("Invalid choice. Please enter a letter (A, B, C...).")

        if q_timer:
            q_timer.stop()

        # Evaluate answer
        is_correct = chosen_answer.is_correct if chosen_answer else False
        if is_correct:
            score += 1

        results.append((question, chosen_answer, is_correct))

        # Show immediate feedback
        print()
        if chosen_answer is None:
            ui.warning("No answer submitted.")
        elif is_correct:
            ui.success("Correct! ✨")
        else:
            correct_texts = [a.answer_text for a in question.answers if a.is_correct]
            ui.error(f"Wrong! The correct answer was: {', '.join(correct_texts)}")

        # Show explanation if available
        if question.explanation:
            print(f"  {ui.ITALIC}{ui.CYAN}💡 Explanation: {question.explanation}{ui.RESET}\n")

        ui.press_enter()

    if quiz_timer:
        quiz_timer.stop()

    session_duration = time.time() - session_start

    # ── Results screen ───────────────────────────────────────────────────────
    _show_results(player_name, quiz, valid_questions, results, score, session_duration)


def _show_results(player_name, quiz, questions, results, score, session_duration) -> None:
    """Render the final results screen and save score."""
    total = len(results)
    percentage = (score / total * 100) if total > 0 else 0.0

    ui.clear()
    ui.banner()
    ui.section_header("Quiz Results", "🏁")

    print(f"  {ui.B_WHITE}{ui.BOLD}Player  : {player_name}{ui.RESET}")
    print(f"  {ui.DIM}Quiz    : {quiz.title}{ui.RESET}")
    mins, secs = divmod(session_duration, 60)
    print(f"  {ui.DIM}Time    : {int(mins):02d}:{int(secs):02d}{ui.RESET}")
    print()
    print(f"  Score   : {ui.B_CYAN}{ui.BOLD}{score} / {total}{ui.RESET}")
    print(f"  Rating  : {ui.score_badge(percentage)}")
    print()
    print(f"  {ui.progress_bar(score, total, width=40)}")
    print()
    ui.hr()

    # Per-question breakdown
    print(f"\n  {ui.BOLD}{ui.WHITE}QUESTION BREAKDOWN{ui.RESET}\n")
    for i, (question, chosen, is_correct) in enumerate(results, 1):
        icon = f"{ui.B_GREEN}✔{ui.RESET}" if is_correct else f"{ui.B_RED}✖{ui.RESET}"
        print(f"  {icon}  Q{i}. {question.question_text[:60]}{'...' if len(question.question_text) > 60 else ''}")
        if chosen:
            clabel = "Your answer : " + chosen.answer_text[:50]
        else:
            clabel = "Your answer : (none)"
        print(f"       {ui.DIM}{clabel}{ui.RESET}")
        if not is_correct:
            correct_texts = [a.answer_text for a in question.answers if a.is_correct]
            print(f"       {ui.B_GREEN}Correct     : {', '.join(correct_texts)[:50]}{ui.RESET}")
        print()

    ui.hr()

    # Save score
    saved = models.save_score(
        player_name=player_name,
        quiz_id=quiz.id,
        quiz_title=quiz.title,
        score=score,
        total_questions=total,
        time_taken_seconds=session_duration,
    )
    ui.success(f"Score saved! You scored {percentage:.1f}%.")
    ui.press_enter("Press ENTER to return to the main menu...")
