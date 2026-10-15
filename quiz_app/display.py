"""
Display/UI helpers - all terminal rendering using ANSI colors and box drawing.
"""

import os
import sys
import shutil

# ── ANSI color codes ────────────────────────────────────────────────────────

RESET   = "\033[0m"
BOLD    = "\033[1m"
DIM     = "\033[2m"
ITALIC  = "\033[3m"

# Foreground
BLACK   = "\033[30m"
RED     = "\033[31m"
GREEN   = "\033[32m"
YELLOW  = "\033[33m"
BLUE    = "\033[34m"
MAGENTA = "\033[35m"
CYAN    = "\033[36m"
WHITE   = "\033[37m"

# Bright foreground
B_RED     = "\033[91m"
B_GREEN   = "\033[92m"
B_YELLOW  = "\033[93m"
B_BLUE    = "\033[94m"
B_MAGENTA = "\033[95m"
B_CYAN    = "\033[96m"
B_WHITE   = "\033[97m"

# Background
BG_BLUE    = "\033[44m"
BG_GREEN   = "\033[42m"
BG_RED     = "\033[41m"
BG_CYAN    = "\033[46m"
BG_MAGENTA = "\033[45m"
BG_BLACK   = "\033[40m"

# Enable ANSI on Windows
if sys.platform == "win32":
    os.system("")


def term_width() -> int:
    return shutil.get_terminal_size((80, 24)).columns


def clear() -> None:
    os.system("cls" if sys.platform == "win32" else "clear")


def hr(char: str = "─", color: str = DIM) -> None:
    print(color + char * term_width() + RESET)


def banner() -> None:
    """Print the main application banner."""
    clear()
    w = term_width()
    lines = [
        "",
        f"{B_CYAN}{BOLD}{'╔' + '═' * (w - 2) + '╗'}{RESET}",
        f"{B_CYAN}{BOLD}║{RESET}{BG_CYAN}{BLACK}{BOLD}{'  🧠  QUIZ MASTER  — The Ultimate Quiz Platform  '.center(w - 2)}{RESET}{B_CYAN}{BOLD}║{RESET}",
        f"{B_CYAN}{BOLD}{'╚' + '═' * (w - 2) + '╝'}{RESET}",
        "",
    ]
    for line in lines:
        print(line)


def section_header(title: str, icon: str = "▶") -> None:
    w = term_width()
    print()
    print(f"{B_BLUE}{BOLD} {icon}  {title.upper()} {RESET}")
    hr("─", BLUE)


def success(msg: str) -> None:
    print(f"\n{B_GREEN}{BOLD} ✔  {msg}{RESET}\n")


def error(msg: str) -> None:
    print(f"\n{B_RED}{BOLD} ✖  {msg}{RESET}\n")


def warning(msg: str) -> None:
    print(f"\n{B_YELLOW}{BOLD} ⚠  {msg}{RESET}\n")


def info(msg: str) -> None:
    print(f"\n{CYAN} ℹ  {msg}{RESET}\n")


def prompt(label: str, default: str = "") -> str:
    """Styled input prompt."""
    default_hint = f"  [{DIM}{default}{RESET}{B_CYAN}]" if default else ""
    try:
        val = input(f"{B_CYAN}{BOLD}  › {label}{default_hint}: {RESET}").strip()
    except (KeyboardInterrupt, EOFError):
        print()
        return ""
    return val if val else default


def menu(title: str, options: list[tuple[str, str]], icon: str = "☰") -> str:
    """
    Display a numbered menu and return the chosen key.
    options: list of (key, label) tuples
    Returns the key of the chosen option.
    """
    section_header(title, icon)
    for i, (key, label) in enumerate(options, 1):
        print(f"  {B_YELLOW}{BOLD}[{i}]{RESET}  {WHITE}{label}{RESET}")
    print(f"  {DIM}[0]  ← Back / Exit{RESET}")
    print()

    choices = {str(i): key for i, (key, _) in enumerate(options, 1)}
    choices["0"] = "back"

    while True:
        raw = prompt("Choose an option").strip()
        if raw in choices:
            return choices[raw]
        if raw.lower() in [k.lower() for k in choices.values()]:
            return raw.lower()
        error("Invalid choice. Please try again.")


def table(headers: list[str], rows: list[list[str]], col_widths: list[int] = None) -> None:
    """Render a simple bordered table."""
    if not rows:
        info("No records found.")
        return

    # Auto-compute widths
    all_rows = [headers] + rows
    if col_widths is None:
        col_widths = [max(len(str(r[i])) for r in all_rows) + 2 for i in range(len(headers))]

    def row_line(cells, color="", bold=False):
        parts = []
        for i, cell in enumerate(cells):
            w = col_widths[i]
            text = str(cell)[:w - 2].ljust(w - 2)
            parts.append(f" {text} ")
        b = BOLD if bold else ""
        print(f"{color}{b}│{'│'.join(parts)}│{RESET}")

    def sep_line(left, mid, right, fill="─"):
        parts = [fill * w for w in col_widths]
        print(f"{DIM}{left}{mid.join(parts)}{right}{RESET}")

    sep_line("┌", "┬", "┐")
    row_line(headers, color=BG_BLUE + WHITE, bold=True)
    sep_line("├", "┼", "┤")
    for i, row in enumerate(rows):
        color = "" if i % 2 == 0 else DIM
        row_line(row, color=color)
    sep_line("└", "┴", "┘")


def progress_bar(current: int, total: int, width: int = 30) -> str:
    """Return a colored ASCII progress bar string."""
    filled = int(width * current / total) if total > 0 else 0
    pct = int(100 * current / total) if total > 0 else 0
    bar = f"{B_GREEN}{'█' * filled}{DIM}{'░' * (width - filled)}{RESET}"
    return f"[{bar}] {B_YELLOW}{BOLD}{pct}%{RESET}"


def score_badge(percentage: float) -> str:
    """Return a colored badge string based on score percentage."""
    if percentage >= 90:
        return f"{B_GREEN}{BOLD}🏆 EXCELLENT ({percentage:.1f}%){RESET}"
    elif percentage >= 70:
        return f"{B_YELLOW}{BOLD}⭐ GOOD ({percentage:.1f}%){RESET}"
    elif percentage >= 50:
        return f"{B_MAGENTA}{BOLD}📘 AVERAGE ({percentage:.1f}%){RESET}"
    else:
        return f"{B_RED}{BOLD}💪 NEEDS IMPROVEMENT ({percentage:.1f}%){RESET}"


def countdown(seconds: int) -> None:
    """Display a simple countdown."""
    import time
    for i in range(seconds, 0, -1):
        print(f"\r{B_YELLOW}{BOLD}  Starting in {i}...{RESET}", end="", flush=True)
        time.sleep(1)
    print("\r" + " " * 30 + "\r", end="")


def press_enter(msg: str = "Press ENTER to continue...") -> None:
    try:
        input(f"\n{DIM}  {msg}{RESET}")
    except (KeyboardInterrupt, EOFError):
        pass
