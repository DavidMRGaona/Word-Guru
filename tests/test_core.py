"""
Core functionality tests for Word-Guru.

Tests the basic game mechanics, word loading, and color utilities.
"""

import unittest
import tempfile
import os
from typing import List

# Import modules to test
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from game import WordGuruGame
from io_utils import color_letter, load_words, print_colored_word
from persistence import load_scores, save_score


class TestWordGuruGame(unittest.TestCase):
    """Test cases for WordGuruGame class."""

    def test_game_instantiation(self):
        """Test that WordGuruGame can be instantiated without errors with a list of 3 words."""
        test_words = ["APPLE", "GRAPE", "PEACH"]
        game = WordGuruGame(test_words)

        self.assertEqual(game.word_list, test_words)
        self.assertEqual(game.max_attempts, 6)  # default value
        self.assertIsNone(game.current_word)
        self.assertEqual(game.attempts, [])
        self.assertFalse(game.game_over)
        self.assertFalse(game.won)

    def test_game_instantiation_custom_attempts(self):
        """Test game instantiation with custom max attempts."""
        test_words = ["APPLE", "GRAPE", "PEACH"]
        game = WordGuruGame(test_words, max_attempts=8)

        self.assertEqual(game.max_attempts, 8)

    def test_start_game(self):
        """Test that start_game initializes the game properly."""
        test_words = ["APPLE", "GRAPE", "PEACH"]
        game = WordGuruGame(test_words)

        game.start_game()

        self.assertIsNotNone(game.current_word)
        self.assertIn(game.current_word, test_words)
        self.assertEqual(game.attempts, [])
        self.assertFalse(game.game_over)
        self.assertFalse(game.won)

    def test_start_game_empty_word_list(self):
        """Test that game initialization raises error with empty word list."""
        with self.assertRaises(ValueError) as context:
            game = WordGuruGame([])
        self.assertIn("Word list cannot be empty", str(context.exception))

    def test_invalid_word_validation(self):
        """Test that game initialization validates word format."""
        # Test words with wrong length
        with self.assertRaises(ValueError) as context:
            game = WordGuruGame(["CAT", "ELEPHANT"])
        self.assertIn("Invalid words found", str(context.exception))
        self.assertIn("CAT", str(context.exception))
        self.assertIn("length 3", str(context.exception))

        # Test words with non-alphabetic characters
        with self.assertRaises(ValueError) as context:
            game = WordGuruGame(["12345", "ABC-D"])
        self.assertIn("non-alphabetic characters", str(context.exception))

    def test_check_guess_without_start(self):
        """Test that check_guess raises error when game not started."""
        test_words = ["APPLE", "GRAPE", "PEACH"]
        game = WordGuruGame(test_words)

        with self.assertRaises(RuntimeError) as context:
            game.check_guess("APPLE")
        self.assertIn("Game not started", str(context.exception))

    def test_check_guess_returns_proper_types(self):
        """Test that check_guess returns two lists with appropriate length."""
        test_words = ["APPLE"]
        game = WordGuruGame(test_words)
        game.start_game()

        letter_statuses, feedback_summary = game.check_guess("GRAPE")

        self.assertIsInstance(letter_statuses, list)
        self.assertIsInstance(feedback_summary, list)
        self.assertEqual(len(letter_statuses), 5)  # Should match word length
        self.assertEqual(len(feedback_summary), 5)  # Should match word length
        self.assertTrue(all(isinstance(status, str) for status in letter_statuses))
        self.assertTrue(all(isinstance(feedback, str) for feedback in feedback_summary))

    def test_check_guess_exact_match(self):
        """Test check_guess with exact word match."""
        test_words = ["APPLE"]
        game = WordGuruGame(test_words)
        game.current_word = "APPLE"  # Force specific word for testing
        game.attempts = []

        letter_statuses, feedback_summary = game.check_guess("APPLE")

        self.assertEqual(len(letter_statuses), 5)  # All letters have status
        self.assertTrue(all(status == "correct" for status in letter_statuses))  # All correct
        self.assertEqual(len(feedback_summary), 5)  # All letters have feedback
        self.assertTrue(game.won)
        self.assertTrue(game.game_over)

    def test_check_guess_partial_match(self):
        """Test check_guess with partial matches."""
        test_words = ["APPLE"]
        game = WordGuruGame(test_words)
        game.current_word = "APPLE"
        game.attempts = []

        letter_statuses, feedback_summary = game.check_guess("PLANE")

        # P is present but wrong position (P is at index 1 in APPLE, guessed at index 0)
        # L is present but wrong position (L is at index 3 in APPLE, guessed at index 1)
        # A is present but wrong position (A is at index 0 in APPLE, guessed at index 2)
        # N is absent (not in APPLE)
        # E is correct position (E is at index 4 in both APPLE and PLANE)
        self.assertEqual(letter_statuses[0], "present")  # P present but wrong position
        self.assertEqual(letter_statuses[1], "present")  # L present but wrong position
        self.assertEqual(letter_statuses[2], "present")  # A present but wrong position
        self.assertEqual(letter_statuses[3], "absent")   # N not in word
        self.assertEqual(letter_statuses[4], "correct")  # E in correct position
        self.assertFalse(game.won)
        self.assertFalse(game.game_over)

    def test_max_attempts_reached(self):
        """Test that game ends when max attempts reached."""
        test_words = ["APPLE"]
        game = WordGuruGame(test_words, max_attempts=2)
        game.start_game()

        # Make two wrong guesses
        game.check_guess("WRONG")
        self.assertFalse(game.game_over)

        game.check_guess("AGAIN")
        self.assertTrue(game.game_over)
        self.assertFalse(game.won)

    def test_is_finished(self):
        """Test is_finished method."""
        test_words = ["APPLE"]
        game = WordGuruGame(test_words)
        game.start_game()

        self.assertFalse(game.is_finished())

        # Win the game
        game.check_guess(game.current_word)
        self.assertTrue(game.is_finished())

    def test_get_current_state(self):
        """Test get_current_state returns proper dictionary."""
        test_words = ["APPLE", "GRAPE", "PEACH"]
        game = WordGuruGame(test_words, max_attempts=6)
        game.start_game()

        state = game.get_current_state()

        self.assertIsInstance(state, dict)
        self.assertIn("current_word", state)
        self.assertIn("attempts", state)
        self.assertIn("attempts_remaining", state)
        self.assertIn("game_over", state)
        self.assertIn("won", state)
        self.assertIn("total_attempts", state)

        self.assertEqual(state["attempts_remaining"], 6)
        self.assertEqual(state["total_attempts"], 0)
        self.assertFalse(state["game_over"])
        self.assertFalse(state["won"])


class TestIOUtils(unittest.TestCase):
    """Test cases for I/O utility functions."""

    def test_color_letter_returns_string(self):
        """Test that color_letter returns a non-empty string."""
        result = color_letter("A", "correct")

        self.assertIsInstance(result, str)
        self.assertGreater(len(result), 0)
        self.assertIn("A", result)

    def test_color_letter_different_statuses(self):
        """Test color_letter with different status values."""
        statuses = ["correct", "present", "absent"]

        for status in statuses:
            result = color_letter("X", status)
            self.assertIsInstance(result, str)
            self.assertGreater(len(result), 0)

    def test_color_letter_invalid_status(self):
        """Test color_letter with invalid status uses default."""
        result = color_letter("A", "invalid_status")
        self.assertIsInstance(result, str)
        self.assertGreater(len(result), 0)

    def test_print_colored_word_length_mismatch(self):
        """Test that print_colored_word raises error for mismatched lengths."""
        with self.assertRaises(ValueError) as context:
            print_colored_word("HELLO", ["correct", "present"])  # 5 letters, 2 statuses
        self.assertIn("Word length must match status list length", str(context.exception))

    def test_load_words_with_test_data(self):
        """Test load_words function with temporary test file."""
        # Create temporary words file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as tmp_file:
            test_content = """# Test words file
                APPLE
                GRAPE
                # Another comment
                PEACH

                # Empty line above should be ignored
                LEMON
            """
            tmp_file.write(test_content)
            tmp_file_path = tmp_file.name

        try:
            words = load_words(tmp_file_path)
            expected_words = ["APPLE", "GRAPE", "PEACH", "LEMON"]
            self.assertEqual(words, expected_words)
        finally:
            os.unlink(tmp_file_path)  # Clean up

    def test_load_words_file_not_found(self):
        """Test load_words with non-existent file."""
        with self.assertRaises(FileNotFoundError):
            load_words("non_existent_file.txt")

    def test_load_words_empty_file(self):
        """Test load_words with empty file (only comments)."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as tmp_file:
            tmp_file.write("# Only comments\n# No actual words\n")
            tmp_file_path = tmp_file.name

        try:
            with self.assertRaises(RuntimeError) as context:
                load_words(tmp_file_path)
            self.assertIn("No valid words found", str(context.exception))
        finally:
            os.unlink(tmp_file_path)  # Clean up


class TestPersistence(unittest.TestCase):
    """Test cases for persistence module stubs."""

    def test_load_scores_returns_list(self):
        """Test that load_scores returns an empty list (stub behavior)."""
        result = load_scores("dummy_path.json")

        self.assertIsInstance(result, list)
        self.assertEqual(len(result), 0)

    def test_save_score_no_error(self):
        """Test that save_score works with valid score structure."""
        test_score = {
            "player": "testuser",
            "word": "APPLE",
            "attempts": 3,
            "won": True,
            "date": "2024-01-01T12:00:00Z"
        }

        # Use a proper temporary directory to avoid empty file issues
        import tempfile
        import pathlib

        with tempfile.TemporaryDirectory() as tmp_dir:
            scores_path = pathlib.Path(tmp_dir) / "test_scores.json"

            try:
                save_score(scores_path, test_score)
                # Verify the score was saved
                scores = load_scores(scores_path)
                self.assertEqual(len(scores), 1)
                self.assertEqual(scores[0], test_score)
            except Exception as e:
                self.fail(f"save_score raised an unexpected exception: {e}")


if __name__ == "__main__":
    unittest.main(verbosity=2)
