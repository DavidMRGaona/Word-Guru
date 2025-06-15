"""
Main game logic for Word-Guru.

This module contains the core game mechanics, word validation,
and game state management for the customizable Wordle-style game.
"""

__all__ = ['WordGuruGame']

import datetime
import pathlib
import random
from datetime import timezone
from typing import Any, Dict, List, Optional, Tuple, Union

from daily import select_daily_word
from persistence import create_score, save_score


class WordGuruGame:
    """
    Main game class for Word-Guru.

    Manages game state, word validation, and user interactions
    for the customizable Wordle-style word guessing game.
    """

    def __init__(self, word_list: List[str], max_attempts: int = 6,
                 scores_path: Union[str, pathlib.Path, None] = "scores.json",
                 player: str = "anonymous", daily_mode: bool = False):
        """
        Initialize the game with word dictionary.

        Args:
            word_list: List of valid words for the game
            max_attempts: Maximum number of guess attempts (default: 6)
            scores_path: Path to scores JSON file, None to disable persistence
            player: Player name for score tracking
            daily_mode: If True, use daily word selection
        """
        self.word_list = [word.upper().strip() for word in word_list]
        self.max_attempts = max_attempts
        self.scores_path = scores_path
        self.player = player
        self.daily_mode = daily_mode
        self.current_word: Optional[str] = None
        self.attempts: List[str] = []
        self.game_over: bool = False
        self.won: bool = False

    def start_game(self) -> None:
        """
        Start a new game session.

        Selects word based on mode (daily or random) and initializes game state.
        """
        if not self.word_list:
            raise ValueError("No words available for the game")

        # Select word based on mode
        if self.daily_mode:
            self.current_word = select_daily_word(self.word_list)
            mode_text = "daily"
        else:
            self.current_word = random.choice(self.word_list)
            mode_text = "random"

        self.attempts = []
        self.game_over = False
        self.won = False

        print("🎯 Word-Guru Started!")
        if self.daily_mode:
            today = datetime.datetime.now(timezone.utc).date()
            print(f"📅 Daily word for {today}")
        print(f"Guess the {len(self.current_word)}-letter word in {self.max_attempts} attempts!")
        print("Letters will be colored: 🟩 Correct position, 🟨 Wrong position, ⬜ Not in word\n")

    def check_guess(self, guess: str) -> Tuple[List[str], List[str]]:
        """
        Process a player's guess and return detailed feedback.

        Args:
            guess: The player's word guess (will be normalized to uppercase)

        Returns:
            Tuple of (letter_statuses, feedback_summary)
            - letter_statuses: List of status for each letter ("correct", "present", "absent")
            - feedback_summary: List of letters with their positions for display

        Raises:
            RuntimeError: If game not started
            ValueError: If guess length doesn't match word length
        """
        if self.current_word is None:
            raise RuntimeError("Game not started. Call start_game() first.")

        guess = guess.upper().strip()

        # Validate guess length
        if len(guess) != len(self.current_word):
            raise ValueError(f"Guess must be {len(self.current_word)} letters long")

        # Validate guess contains only letters
        if not guess.isalpha():
            raise ValueError("Guess must contain only letters")

        # Add guess to attempts
        self.attempts.append(guess)

        # Calculate detailed letter feedback
        letter_statuses = []
        feedback_summary = []

        # Track letter counts in target word for accurate "present" detection
        target_letter_counts = {}
        for letter in self.current_word:
            target_letter_counts[letter] = target_letter_counts.get(letter, 0) + 1

        # First pass: mark correct positions
        used_target_letters = {}
        for i, letter in enumerate(guess):
            if letter == self.current_word[i]:
                letter_statuses.append("correct")
                feedback_summary.append(f"{letter}✓")
                used_target_letters[letter] = used_target_letters.get(letter, 0) + 1
            else:
                letter_statuses.append("pending")  # Will be updated in second pass
                feedback_summary.append(f"{letter}?")

        # Second pass: mark present/absent for non-correct letters
        for i, letter in enumerate(guess):
            if letter_statuses[i] == "pending":
                available_count = target_letter_counts.get(letter, 0) - used_target_letters.get(letter, 0)
                if available_count > 0:
                    letter_statuses[i] = "present"
                    feedback_summary[i] = f"{letter}~"
                    used_target_letters[letter] = used_target_letters.get(letter, 0) + 1
                else:
                    letter_statuses[i] = "absent"
                    feedback_summary[i] = f"{letter}✗"

        # Check win condition
        if guess == self.current_word:
            self.won = True
            self.game_over = True

        # Check max attempts reached
        if len(self.attempts) >= self.max_attempts:
            self.game_over = True

        # Save score when game ends
        if self.game_over:
            self._save_game_score()

        return letter_statuses, feedback_summary

    def _save_game_score(self) -> None:
        """
        Save the current game score to persistent storage.

        Called automatically when the game ends.
        """
        if self.scores_path is None or self.current_word is None:
            return

        try:
            score = create_score(
                player=self.player,
                word=self.current_word,
                attempts=len(self.attempts),
                won=self.won
            )
            save_score(self.scores_path, score)

            print(f"💾 Score saved for player '{self.player}'")

        except Exception as e:
            print(f"⚠️  Warning: Could not save score: {e}")

    def is_finished(self) -> bool:
        """
        Check if the game is finished (won or max attempts reached).

        Returns:
            True if game is over, False otherwise
        """
        return self.game_over

    def get_current_state(self) -> Dict[str, Any]:
        """
        Get current game state for display/testing.

        Returns:
            Dictionary containing detailed current game state information
        """
        state = {
            "current_word": self.current_word,  # For testing/debugging only
            "attempts": self.attempts.copy(),
            "attempts_remaining": self.max_attempts - len(self.attempts),
            "game_over": self.game_over,
            "won": self.won,
            "total_attempts": len(self.attempts),
            "player": self.player,
            "scores_path": str(self.scores_path) if self.scores_path else None,
            "daily_mode": self.daily_mode,
            "max_attempts": self.max_attempts
        }

        # Add daily-specific information
        if self.daily_mode:
            from daily import time_until_next_daily, is_daily_completed
            state["time_until_next_daily"] = time_until_next_daily()
            state["daily_completed"] = is_daily_completed(self.player, self.scores_path)
            state["today_date"] = str(datetime.datetime.now(timezone.utc).date())

        return state


def main():
    """
    Legacy main entry point for the game.

    Note: CLI functionality is available in __main__.py.
    """
    print("Word-Guru")
    print("Customizable Wordle-style word guessing game!")
    print("Use: python3 play.py --help for all options")


if __name__ == "__main__":
    main()
