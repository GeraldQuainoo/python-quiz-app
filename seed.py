"""
Seed script - populates the database with sample quizzes, questions, and answers
for demonstration purposes.

Usage:
    python seed.py
"""

from quiz_app.database import initialize_db
from quiz_app import models


def seed() -> None:
    initialize_db()
    print("🌱 Seeding database with sample data...\n")

    # ── Categories ────────────────────────────────────────────────────────────
    cat_science   = models.create_category("Science",   "Physics, chemistry, biology, and more")
    cat_history   = models.create_category("History",   "World history and civilizations")
    cat_tech      = models.create_category("Technology","Computers, programming, and gadgets")
    cat_geography = models.create_category("Geography", "Countries, capitals, and natural wonders")
    print(f"  ✔ Created {4} categories")

    # ── Quiz 1: General Science ───────────────────────────────────────────────
    quiz1 = models.create_quiz(
        title="General Science Trivia",
        description="Test your knowledge of basic science concepts.",
        category_id=cat_science.id,
        time_limit_seconds=0,
        randomize_questions=True,
    )
    science_data = [
        (
            "What is the chemical symbol for water?",
            "The molecular formula for water is H₂O — two hydrogen atoms and one oxygen atom.",
            [("H2O", True), ("CO2", False), ("NaCl", False), ("O2", False)],
        ),
        (
            "What planet is known as the Red Planet?",
            "Mars has a reddish appearance due to iron oxide (rust) on its surface.",
            [("Mars", True), ("Jupiter", False), ("Venus", False), ("Saturn", False)],
        ),
        (
            "What is the powerhouse of the cell?",
            "The mitochondria produce ATP through cellular respiration.",
            [("Mitochondria", True), ("Nucleus", False), ("Ribosome", False), ("Golgi apparatus", False)],
        ),
        (
            "What is the speed of light in a vacuum (approximately)?",
            "Light travels at approximately 299,792,458 metres per second in a vacuum.",
            [("300,000 km/s", True), ("150,000 km/s", False), ("3,000 km/s", False), ("30,000 km/s", False)],
        ),
        (
            "Which gas do plants absorb from the atmosphere during photosynthesis?",
            "Plants absorb CO₂ and release O₂ during photosynthesis.",
            [("Carbon dioxide", True), ("Oxygen", False), ("Nitrogen", False), ("Hydrogen", False)],
        ),
    ]
    for q_text, explanation, answer_list in science_data:
        q = models.create_question(quiz1.id, q_text, explanation, time_limit_seconds=30)
        for a_text, is_correct in answer_list:
            models.add_answer(q.id, a_text, is_correct)
    print(f"  ✔ Created quiz '{quiz1.title}' with {len(science_data)} questions")

    # ── Quiz 2: World History ─────────────────────────────────────────────────
    quiz2 = models.create_quiz(
        title="World History Challenge",
        description="How well do you know world history?",
        category_id=cat_history.id,
        time_limit_seconds=120,
        randomize_questions=False,
    )
    history_data = [
        (
            "In which year did World War II end?",
            "World War II ended in 1945: V-E Day (May 8) and V-J Day (August 15).",
            [("1945", True), ("1944", False), ("1918", False), ("1939", False)],
        ),
        (
            "Who was the first President of the United States?",
            "George Washington served as the 1st President from 1789 to 1797.",
            [("George Washington", True), ("Abraham Lincoln", False), ("Thomas Jefferson", False), ("John Adams", False)],
        ),
        (
            "The Great Wall of China was primarily built to protect against which group?",
            "The wall was built to defend against raids by nomadic groups from the north, including the Mongols.",
            [("Mongol invasions", True), ("Japanese pirates", False), ("Roman Empire", False), ("Persian armies", False)],
        ),
        (
            "What ancient wonder was located in Alexandria, Egypt?",
            "The Lighthouse of Alexandria was one of the Seven Wonders of the Ancient World.",
            [("The Lighthouse of Alexandria", True), ("The Colossus of Rhodes", False), ("The Hanging Gardens", False), ("The Pyramids of Giza", False)],
        ),
    ]
    for q_text, explanation, answer_list in history_data:
        q = models.create_question(quiz2.id, q_text, explanation, time_limit_seconds=0)
        for a_text, is_correct in answer_list:
            models.add_answer(q.id, a_text, is_correct)
    print(f"  ✔ Created quiz '{quiz2.title}' with {len(history_data)} questions")

    # ── Quiz 3: Tech & Programming ────────────────────────────────────────────
    quiz3 = models.create_quiz(
        title="Tech & Programming Quiz",
        description="For developers and tech enthusiasts.",
        category_id=cat_tech.id,
        time_limit_seconds=0,
        randomize_questions=True,
    )
    tech_data = [
        (
            "What does 'CPU' stand for?",
            "CPU = Central Processing Unit — the primary component that executes program instructions.",
            [("Central Processing Unit", True), ("Core Processing Unit", False), ("Computer Power Unit", False), ("Central Program Utility", False)],
        ),
        (
            "Which programming language is known as the 'language of the web' for front-end development?",
            "JavaScript runs in every major browser and powers interactive web pages.",
            [("JavaScript", True), ("Python", False), ("Java", False), ("PHP", False)],
        ),
        (
            "What does HTTP stand for?",
            "HyperText Transfer Protocol is the foundation of data communication on the World Wide Web.",
            [("HyperText Transfer Protocol", True), ("High Transfer Text Protocol", False), ("Hyper Terminal Transfer Protocol", False), ("Home Transfer Text Protocol", False)],
        ),
        (
            "Which data structure operates on a LIFO (Last In, First Out) basis?",
            "A Stack uses LIFO — the last element pushed is the first one popped.",
            [("Stack", True), ("Queue", False), ("Linked List", False), ("Hash Map", False)],
        ),
        (
            "What is the output of 2 ** 10 in Python?",
            "The ** operator is Python's exponentiation operator: 2¹⁰ = 1024.",
            [("1024", True), ("20", False), ("100", False), ("2048", False)],
        ),
        (
            "What does 'SQL' stand for?",
            "SQL = Structured Query Language, used to manage and query relational databases.",
            [("Structured Query Language", True), ("Simple Query Language", False), ("Sequential Query Logic", False), ("System Query Language", False)],
        ),
    ]
    for q_text, explanation, answer_list in tech_data:
        q = models.create_question(quiz3.id, q_text, explanation, time_limit_seconds=20)
        for a_text, is_correct in answer_list:
            models.add_answer(q.id, a_text, is_correct)
    print(f"  ✔ Created quiz '{quiz3.title}' with {len(tech_data)} questions")

    # ── Quiz 4: Geography ─────────────────────────────────────────────────────
    quiz4 = models.create_quiz(
        title="World Geography",
        description="Capitals, countries, and natural wonders.",
        category_id=cat_geography.id,
        time_limit_seconds=0,
        randomize_questions=False,
    )
    geo_data = [
        (
            "What is the capital city of Australia?",
            "Canberra, not Sydney, is the capital of Australia. It was chosen as a compromise between Sydney and Melbourne.",
            [("Canberra", True), ("Sydney", False), ("Melbourne", False), ("Brisbane", False)],
        ),
        (
            "Which is the longest river in the world?",
            "The Nile River in Africa is generally considered the longest river at ~6,650 km.",
            [("Nile", True), ("Amazon", False), ("Yangtze", False), ("Mississippi", False)],
        ),
        (
            "Which country has the most natural lakes?",
            "Canada has over 60% of the world's lakes — more than any other country.",
            [("Canada", True), ("Russia", False), ("United States", False), ("Finland", False)],
        ),
        (
            "What is the smallest country in the world by area?",
            "Vatican City covers just 0.44 km² and is an independent city-state within Rome.",
            [("Vatican City", True), ("Monaco", False), ("San Marino", False), ("Liechtenstein", False)],
        ),
    ]
    for q_text, explanation, answer_list in geo_data:
        q = models.create_question(quiz4.id, q_text, explanation, time_limit_seconds=0)
        for a_text, is_correct in answer_list:
            models.add_answer(q.id, a_text, is_correct)
    print(f"  ✔ Created quiz '{quiz4.title}' with {len(geo_data)} questions")

    print("\n✅ Seeding complete! Run 'python main.py' to start the app.\n")


if __name__ == "__main__":
    seed()
