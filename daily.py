"""
Daily word functionality for Word-Guru.

This module provides deterministic word selection based on date,
ensuring all players get the same word each day.
"""

__all__ = [
    'select_daily_word', 'is_daily_completed', 'get_next_daily_reset',
    'time_until_next_daily'
]

import datetime
import hashlib
from datetime import timezone
from typing import List, Optional


def select_daily_word(words: List[str], date: Optional[datetime.date] = None) -> str:
    """
    Select a deterministic word based on the given date.

    Uses SHA-256 hash of the date string as a seed to ensure
    all players get the same word for the same date.

    Args:
        words: List of available words
        date: Date to use for selection (defaults to today UTC)

    Returns:
        Selected word for the given date

    Raises:
        ValueError: If words list is empty

    Examples:
        >>> words = ["APPLE", "GRAPE", "PEACH"]
        >>> word1 = select_daily_word(words, datetime.date(2024, 6, 15))
        >>> word2 = select_daily_word(words, datetime.date(2024, 6, 15))
        >>> word1 == word2  # Always True for same date
        True
    """
    if not words:
        raise ValueError("Words list cannot be empty")

    # Use today's date if none provided
    if date is None:
        date = datetime.datetime.now(timezone.utc).date()

    # Create deterministic seed from date
    date_string = str(date)  # Format: YYYY-MM-DD
    hash_object = hashlib.sha256(date_string.encode())
    hash_hex = hash_object.hexdigest()

    # Convert first 8 characters of hash to integer for indexing
    seed = int(hash_hex[:8], 16)

    # Select word using modulo to ensure valid index
    word_index = seed % len(words)

    return words[word_index].upper().strip()


def get_next_daily_reset() -> datetime.datetime:
    """
    Get the next daily reset time (midnight UTC).

    Returns:
        Next midnight UTC as datetime object
    """
    now = datetime.datetime.now(timezone.utc)
    tomorrow = now.date() + datetime.timedelta(days=1)
    next_reset = datetime.datetime.combine(tomorrow, datetime.time.min, timezone.utc)

    return next_reset


def time_until_next_daily() -> str:
    """
    Get human-readable time until next daily word.

    Returns:
        Formatted string like "5h 23m" or "23m 45s"
    """
    now = datetime.datetime.now(timezone.utc)
    next_reset = get_next_daily_reset()
    delta = next_reset - now

    hours = delta.seconds // 3600
    minutes = (delta.seconds % 3600) // 60
    seconds = delta.seconds % 60

    if hours > 0:
        return f"{hours}h {minutes}m"
    elif minutes > 0:
        return f"{minutes}m {seconds}s"
    else:
        return f"{seconds}s"


def is_daily_completed(player: str, scores_path: Optional[str] = "scores.json") -> bool:
    """
    Check if player has already completed today's daily word.

    Args:
        player: Player name to check
        scores_path: Path to scores file

    Returns:
        True if player completed today's word, False otherwise
    """
    if not scores_path:
        return False

    try:
        from persistence import load_scores
        scores = load_scores(scores_path)

        today = datetime.datetime.now(timezone.utc).date()
        today_str = str(today)

        # Check if player has a score from today
        for score in reversed(scores):  # Check recent scores first
            if score.get("player") == player:
                score_date = score.get("date", "")
                if score_date.startswith(today_str):
                    return True

        return False

    except Exception:
        # If we can't load scores, assume not completed
        return False
