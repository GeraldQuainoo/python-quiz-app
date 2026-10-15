# 🧠 Quiz Master

A **feature-rich command-line quiz application** built with Python and SQLite. Create quizzes, add questions with multiple-choice answers, track scores, and compete on the leaderboard — all from your terminal.

---

## ✨ Features

| Feature | Description |
|---|---|
| 📚 **Quiz Management** | Create, edit, and delete quizzes |
| ❓ **Question Builder** | Add multiple-choice questions with up to 6 answer options |
| ✅ **Correct Answers** | Mark one (or more) answers as correct |
| 💡 **Explanations** | Add explanations shown after each answer |
| 🗂 **Categories** | Organise quizzes by topic/category |
| ⏱ **Timers** | Set time limits per-question or per-quiz |
| 🔀 **Randomisation** | Shuffle question and answer order each time |
| 🏆 **Leaderboard** | Global and per-quiz leaderboards with rankings |
| 👤 **Player Stats** | Track individual player performance across quizzes |
| 🎨 **Rich CLI UI** | Colourful, animated terminal interface |
| 💾 **SQLite Storage** | Persistent local database — no server required |

---

## 🚀 Getting Started

### Prerequisites
- Python **3.10+**

### Installation

```bash
# 1. Clone the repository
git clone https://github.com/YOUR_USERNAME/quiz-master.git
cd quiz-master

# 2. (Optional) Create a virtual environment
python -m venv venv
source venv/bin/activate        # macOS/Linux
venv\Scripts\activate           # Windows

# 3. Install dependencies
pip install -r requirements.txt
```

### Running the App

```bash
python main.py
```

### Loading Sample Data (Optional)

```bash
python seed.py
```

This will create 4 categories and 4 sample quizzes (Science, History, Technology, Geography) ready to play.

---

## 🎮 Usage

```
╔══════════════════════════════════════════════════════╗
║          🧠  QUIZ MASTER  — Main Menu                ║
╚══════════════════════════════════════════════════════╝

  [1]  🎯  Take a Quiz
  [2]  📚  Manage Quizzes
  [3]  🗂   Manage Categories
  [4]  🏆  Leaderboard & Stats
  [0]  ← Exit
```

### Creating a Quiz
1. Go to **Manage Quizzes → Create new quiz**
2. Set a title, description, category, time limit, and shuffle option
3. Then go to **Manage Questions → Add new question**
4. For each question, add 2–6 answer choices and mark the correct one
5. Optionally add an explanation

### Taking a Quiz
1. Go to **Take a Quiz**
2. Enter your player name
3. Choose a quiz from the list
4. Answer each question within the time limit (if set)
5. View your results and explanation after each question

---

## 🧪 Running Tests

```bash
python -m pytest tests/ -v
```

Tests cover all CRUD operations for categories, quizzes, questions, answers, and score tracking.

---

## 📁 Project Structure

```
quiz-master/
├── main.py               # Entry point
├── seed.py               # Sample data loader
├── requirements.txt      # Dependencies
├── pyproject.toml        # Project config & pytest settings
├── quiz_app/
│   ├── __init__.py
│   ├── database.py       # SQLite connection & schema
│   ├── models.py         # Data classes & CRUD operations
│   ├── engine.py         # Quiz session runner & timer
│   ├── menus.py          # All interactive CLI menus
│   └── display.py        # ANSI colour UI helpers
└── tests/
    ├── __init__.py
    └── test_models.py    # Unit tests
```

---

## 🗄 Database Schema

```
categories  ──< quizzes ──< questions ──< answers
                     │
                     └──< scores
```

- **categories**: Topic groupings for quizzes
- **quizzes**: Quiz metadata (title, time limit, shuffle)
- **questions**: Individual questions linked to a quiz
- **answers**: Multiple-choice options linked to a question
- **scores**: Player results for leaderboard tracking

---

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/my-feature`)
3. Commit your changes (`git commit -m 'Add my feature'`)
4. Push to the branch (`git push origin feature/my-feature`)
5. Open a Pull Request

---

## 📄 License

This project is licensed under the [MIT License](LICENSE).
