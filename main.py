"""
Quiz Master — Entry Point
Initializes the database and launches the main CLI menu.
"""

import sys
from quiz_app.database import initialize_db
from quiz_app import display as ui
from quiz_app import menus


def main() -> None:
    """Main application loop."""
    # Bootstrap database
    initialize_db()

    while True:
        ui.banner()

        choice = ui.menu("Main Menu", [
            ("play",        "🎯  Take a Quiz"),
            ("quizzes",     "📚  Manage Quizzes"),
            ("categories",  "🗂   Manage Categories"),
            ("leaderboard", "🏆  Leaderboard & Stats"),
        ], icon="🏠")

        if choice == "back":
            ui.clear()
            print(f"\n  {ui.B_CYAN}{ui.BOLD}Thanks for using Quiz Master! Goodbye! 👋{ui.RESET}\n")
            sys.exit(0)
        elif choice == "1":
            menus.menu_take_quiz()
        elif choice == "2":
            menus.menu_quizzes()
        elif choice == "3":
            menus.menu_categories()
        elif choice == "4":
            menus.menu_leaderboard()


if __name__ == "__main__":
    main()
