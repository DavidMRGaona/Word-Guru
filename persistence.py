"""
Persistence layer for Word-Guru.

Handles saving and loading of game statistics, scores,
and player progress using JSON storage.
"""

__all__ = [
    'load_scores', 'save_score', 'get_top_scores', 'create_score'
]

import json
import pathlib
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Union


def load_scores(path: Union[str, pathlib.Path]) -> List[Dict[str, Any]]:
    """
    Load game scores from JSON file.

    Args:
        path: Path to the scores JSON file

    Returns:
        List of score dictionaries. Returns empty list if file doesn't exist.

    Raises:
        RuntimeError: If file exists but contains invalid JSON
    """
    path = pathlib.Path(path)

    if not path.exists():
        return []

    try:
        with open(path, 'r', encoding='utf-8') as f:
            content = f.read().strip()

        # Handle empty file
        if not content:
            return []

        scores = json.loads(content)

        # Validate that we got a list
        if not isinstance(scores, list):
            raise ValueError("Score file should contain a list of scores")

        return scores

    except (json.JSONDecodeError, ValueError) as e:
        raise RuntimeError(f"Error loading scores from {path}: {e}")
    except Exception as e:
        raise RuntimeError(f"Unexpected error loading scores from {path}: {e}")


def save_score(path: Union[str, pathlib.Path], score: Dict[str, Any]) -> None:
    """
    Save a game score to JSON file.

    Creates the file if it doesn't exist and appends the score to the list.

    Args:
        path: Path to the scores JSON file
        score: Score dictionary to save with structure:
               {
                   "player": str,     # player name or alias
                   "word": str,       # target word
                   "attempts": int,   # number of attempts used
                   "won": bool,       # True if player won
                   "date": str        # ISO 8601 timestamp
               }

    Raises:
        RuntimeError: If unable to save the score
        ValueError: If score structure is invalid
    """
    path = pathlib.Path(path)

    # Validate score structure
    required_fields = {"player", "word", "attempts", "won", "date"}
    if not isinstance(score, dict):
        raise ValueError("Score must be a dictionary")

    missing_fields = required_fields - set(score.keys())
    if missing_fields:
        raise ValueError(f"Score missing required fields: {missing_fields}")

    # Validate field types
    if not isinstance(score["player"], str):
        raise ValueError("Score 'player' must be a string")
    if not isinstance(score["word"], str):
        raise ValueError("Score 'word' must be a string")
    if not isinstance(score["attempts"], int) or score["attempts"] < 0:
        raise ValueError("Score 'attempts' must be a non-negative integer")
    if not isinstance(score["won"], bool):
        raise ValueError("Score 'won' must be a boolean")
    if not isinstance(score["date"], str):
        raise ValueError("Score 'date' must be a string")

    try:
        # Load existing scores
        scores = load_scores(path)

        # Add new score
        scores.append(score)

        # Create parent directory if needed
        path.parent.mkdir(parents=True, exist_ok=True)

        # Save back to file
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(scores, f, indent=2, ensure_ascii=False)

    except Exception as e:
        raise RuntimeError(f"Error saving score to {path}: {e}")


def get_top_scores(scores: List[Dict[str, Any]], limit: int = 10) -> List[Dict[str, Any]]:
    """
    Get top scores sorted by best performance.

    Args:
        scores: List of score dictionaries
        limit: Maximum number of scores to return

    Returns:
        List of top scores sorted by:
        1. Won games first (won=True)
        2. Fewer attempts (ascending)
        3. More recent date (descending)
    """
    if not scores:
        return []

    def score_key(score: Dict[str, Any]) -> tuple:
        """Sort key function for ranking scores."""
        won = score.get("won", False)
        attempts = score.get("attempts", float('inf'))
        date_str = score.get("date", "")

        # Parse date for sorting (more recent first)
        try:
            date_obj = datetime.fromisoformat(date_str.replace('Z', '+00:00'))
        except (ValueError, AttributeError):
            date_obj = datetime.min

        # Return tuple for sorting:
        # - Won games first (False < True, so negate for reverse)
        # - Fewer attempts first (ascending)
        # - More recent date first (negate timestamp for reverse)
        return (not won, attempts, -date_obj.timestamp())

    # Sort and limit
    sorted_scores = sorted(scores, key=score_key)
    return sorted_scores[:limit]


def create_score(player: str, word: str, attempts: int, won: bool) -> Dict[str, Any]:
    """
    Create a score dictionary with current timestamp.

    Args:
        player: Player name or alias
        word: Target word that was guessed
        attempts: Number of attempts used
        won: Whether the player won

    Returns:
        Score dictionary ready for saving
    """
    return {
        "player": player,
        "word": word,
        "attempts": attempts,
        "won": won,
        "date": datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z')
    }



