"""
Tests for daily word functionality in Word-Guru.

Tests deterministic word selection, completion tracking,
and time-based utilities.
"""

import unittest
import tempfile
import json
import os
from datetime import datetime, date, timezone, timedelta

# Import modules to test
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from daily import (
    select_daily_word, is_daily_completed, get_next_daily_reset,
    time_until_next_daily
)


class TestSelectDailyWord(unittest.TestCase):
    """Test cases for select_daily_word function."""

    def setUp(self):
        """Set up test fixtures."""
        self.test_words = ["APPLE", "GRAPE", "PEACH", "LEMON"]
        self.test_date = date(2024, 6, 15)

    def test_same_date_same_word(self):
        """Test that same date always returns same word."""
        word1 = select_daily_word(self.test_words, self.test_date)
        word2 = select_daily_word(self.test_words, self.test_date)

        self.assertEqual(word1, word2)
        self.assertIn(word1, self.test_words)

    def test_different_dates_can_have_different_words(self):
        """Test that different dates can produce different words."""
        date1 = date(2024, 6, 15)
        date2 = date(2024, 6, 16)

        word1 = select_daily_word(self.test_words, date1)
        word2 = select_daily_word(self.test_words, date2)

        # Both should be valid words
        self.assertIn(word1, self.test_words)
        self.assertIn(word2, self.test_words)

        # They might be different (not guaranteed, but likely with enough words)
        # This test mainly ensures the function works with different dates

    def test_deterministic_across_multiple_calls(self):
        """Test deterministic behavior across multiple calls."""
        results = []
        for _ in range(10):
            word = select_daily_word(self.test_words, self.test_date)
            results.append(word)

        # All results should be identical
        self.assertTrue(all(word == results[0] for word in results))

    def test_empty_word_list_raises_error(self):
        """Test that empty word list raises ValueError."""
        with self.assertRaises(ValueError) as context:
            select_daily_word([], self.test_date)
        self.assertIn("cannot be empty", str(context.exception))

    def test_single_word_list(self):
        """Test behavior with single word list."""
        single_word = ["TIGER"]
        word = select_daily_word(single_word, self.test_date)

        self.assertEqual(word, "TIGER")

    def test_word_normalization(self):
        """Test that words are properly normalized to uppercase."""
        mixed_case_words = ["apple", "Grape", "PEACH"]
        word = select_daily_word(mixed_case_words, self.test_date)

        # Result should be uppercase
        self.assertTrue(word.isupper())
        self.assertIn(word, ["APPLE", "GRAPE", "PEACH"])

    def test_different_word_lists_same_date(self):
        """Test that different word lists can produce different results."""
        list1 = ["APPLE", "GRAPE"]
        list2 = ["TIGER", "WHALE"]

        word1 = select_daily_word(list1, self.test_date)
        word2 = select_daily_word(list2, self.test_date)

        self.assertIn(word1, list1)
        self.assertIn(word2, list2)

    def test_default_date_uses_today(self):
        """Test that default date parameter uses today."""
        # This test just ensures the function doesn't crash when no date provided
        word = select_daily_word(self.test_words)
        self.assertIn(word, self.test_words)


class TestDailyTimeUtils(unittest.TestCase):
    """Test cases for daily time utility functions."""

    def test_get_next_daily_reset(self):
        """Test that next daily reset is calculated correctly."""
        next_reset = get_next_daily_reset()

        # Should be a datetime object
        self.assertIsInstance(next_reset, datetime)

        # Should be in the future
        now = datetime.now(timezone.utc)
        self.assertGreater(next_reset, now)

        # Should be at midnight UTC
        self.assertEqual(next_reset.hour, 0)
        self.assertEqual(next_reset.minute, 0)
        self.assertEqual(next_reset.second, 0)
        self.assertEqual(next_reset.microsecond, 0)

    def test_time_until_next_daily_format(self):
        """Test time formatting returns valid format."""
        time_str = time_until_next_daily()

        # Should be a non-empty string
        self.assertIsInstance(time_str, str)
        self.assertGreater(len(time_str), 0)

        # Should contain time units (h, m, or s)
        self.assertTrue(any(unit in time_str for unit in ['h', 'm', 's']))


class TestDailyCompletion(unittest.TestCase):
    """Test cases for daily completion tracking."""

    def test_is_daily_completed_no_scores_path(self):
        """Test completion check when scores_path is None."""
        result = is_daily_completed("testplayer", None)
        self.assertFalse(result)

    def test_is_daily_completed_no_file(self):
        """Test completion check when scores file doesn't exist."""
        with tempfile.TemporaryDirectory() as tmp_dir:
            non_existent_path = os.path.join(tmp_dir, "nonexistent.json")
            result = is_daily_completed("testplayer", non_existent_path)
            self.assertFalse(result)

    def test_is_daily_completed_empty_file(self):
        """Test completion check with empty scores file."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as tmp_file:
            json.dump([], tmp_file)
            tmp_file_path = tmp_file.name

        try:
            result = is_daily_completed("testplayer", tmp_file_path)
            self.assertFalse(result)
        finally:
            os.unlink(tmp_file_path)

    def test_is_daily_completed_no_scores_for_player(self):
        """Test completion check when player has no scores."""
        other_player_score = {
            "player": "otherplayer",
            "word": "APPLE",
            "attempts": 3,
            "won": True,
            "date": datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z')
        }

        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as tmp_file:
            json.dump([other_player_score], tmp_file)
            tmp_file_path = tmp_file.name

        try:
            result = is_daily_completed("testplayer", tmp_file_path)
            self.assertFalse(result)
        finally:
            os.unlink(tmp_file_path)

    def test_is_daily_completed_with_today_score(self):
        """Test completion check with today's score."""
        today_score = {
            "player": "testplayer",
            "word": "APPLE",
            "attempts": 4,
            "won": True,
            "date": datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z')
        }

        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as tmp_file:
            json.dump([today_score], tmp_file)
            tmp_file_path = tmp_file.name

        try:
            result = is_daily_completed("testplayer", tmp_file_path)
            self.assertTrue(result)
        finally:
            os.unlink(tmp_file_path)

    def test_is_daily_completed_with_old_score(self):
        """Test completion check with old score."""
        yesterday = datetime.now(timezone.utc) - timedelta(days=1)
        old_score = {
            "player": "testplayer",
            "word": "APPLE",
            "attempts": 3,
            "won": True,
            "date": yesterday.isoformat().replace('+00:00', 'Z')
        }

        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as tmp_file:
            json.dump([old_score], tmp_file)
            tmp_file_path = tmp_file.name

        try:
            result = is_daily_completed("testplayer", tmp_file_path)
            self.assertFalse(result)
        finally:
            os.unlink(tmp_file_path)

    def test_is_daily_completed_invalid_json(self):
        """Test completion check with invalid JSON file."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as tmp_file:
            tmp_file.write("invalid json")
            tmp_file_path = tmp_file.name

        try:
            # Should not crash, should return False
            result = is_daily_completed("testplayer", tmp_file_path)
            self.assertFalse(result)
        finally:
            os.unlink(tmp_file_path)


if __name__ == "__main__":
    unittest.main(verbosity=2)
