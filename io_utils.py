"""
Input/Output utilities for Word-Guru.

Provides ANSI color codes, terminal formatting, and console
interaction utilities for enhanced game presentation.
"""

__all__ = [
    'Colors', 'color_letter', 'print_colored_word', 'load_words',
    'colorize', 'print_colored', 'clear_screen'
]

import sys
from typing import Dict, List, Optional


class Colors:
    """ANSI color codes for terminal output."""

    # Basic colors
    BLACK = '\033[30m'
    RED = '\033[31m'
    GREEN = '\033[32m'
    YELLOW = '\033[33m'
    BLUE = '\033[34m'
    MAGENTA = '\033[35m'
    CYAN = '\033[36m'
    WHITE = '\033[37m'

    # Background colors
    BG_BLACK = '\033[40m'
    BG_RED = '\033[41m'
    BG_GREEN = '\033[42m'
    BG_YELLOW = '\033[43m'
    BG_BLUE = '\033[44m'
    BG_MAGENTA = '\033[45m'
    BG_CYAN = '\033[46m'
    BG_WHITE = '\033[47m'

    # Text formatting
    BOLD = '\033[1m'
    DIM = '\033[2m'
    UNDERLINE = '\033[4m'
    REVERSE = '\033[7m'

    # Reset
    RESET = '\033[0m'

    # Game-specific colors
    CORRECT = '\033[42m\033[30m'      # Green background, black text
    PARTIAL = '\033[43m\033[30m'      # Yellow background, black text
    INCORRECT = '\033[47m\033[30m'    # White background, black text


def color_letter(letter: str, status: str) -> str:
    """
    Apply color formatting to a single letter based on its status.

    Args:
        letter: Single letter to colorize
        status: Status of the letter ("correct", "present", "absent")

    Returns:
        Formatted letter with color codes
    """
    color_map = {
        "correct": Colors.CORRECT,
        "present": Colors.PARTIAL,
        "absent": Colors.INCORRECT
    }

    color = color_map.get(status, Colors.RESET)
    return f"{color} {letter.upper()} {Colors.RESET}"


def print_colored_word(word: str, status: List[str]) -> None:
    """
    Print a word with each letter colored according to its status.

    Args:
        word: Word to print (will be normalized to uppercase)
        status: List of status strings for each letter position
    """
    if len(word) != len(status):
        raise ValueError("Word length must match status list length")

    colored_letters = []
    for letter, letter_status in zip(word.upper(), status):
        colored_letters.append(color_letter(letter, letter_status))

    print("".join(colored_letters))


def load_words(path: str) -> List[str]:
    """
    Load words from a text file, filtering out comments and empty lines.

    Args:
        path: Path to the words file

    Returns:
        List of valid words (uppercase, stripped)

    Raises:
        FileNotFoundError: If the words file doesn't exist
        RuntimeError: If no valid words found or other loading errors
    """
    try:
        with open(path, 'r', encoding='utf-8') as file:
            words = []
            for line in file:
                line = line.strip().upper()
                # Skip empty lines and comments
                if line and not line.startswith('#'):
                    words.append(line)

            if not words:
                raise ValueError(f"No valid words found in {path}")

            return words

    except FileNotFoundError:
        raise FileNotFoundError(f"Words file not found: {path}")
    except Exception as e:
        raise RuntimeError(f"Error loading words from {path}: {e}")


def colorize(text: str, color: str, bg_color: Optional[str] = None) -> str:
    """
    Apply color formatting to text.

    Args:
        text: Text to colorize
        color: Foreground color code
        bg_color: Optional background color code

    Returns:
        Formatted text with color codes
    """
    if bg_color:
        return f"{bg_color}{color}{text}{Colors.RESET}"
    else:
        return f"{color}{text}{Colors.RESET}"


def print_colored(text: str, color: str, bg_color: Optional[str] = None, end: str = '\n') -> None:
    """
    Print text with color formatting.

    Args:
        text: Text to print
        color: Foreground color code
        bg_color: Optional background color code
        end: String appended after the text
    """
    print(colorize(text, color, bg_color), end=end)


def clear_screen() -> None:
    """
    Clear the terminal screen in a cross-platform way.
    """
    import os
    os.system('cls' if os.name == 'nt' else 'clear')



