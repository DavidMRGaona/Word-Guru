"""
Tests for persistence functionality in Word-Guru.

Tests JSON score loading, saving, and ranking functionality.
"""

import unittest
import tempfile
import pathlib
import json
import os
from datetime import datetime, timedelta, timezone

# Import modules to test
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from persistence import (
    load_scores, save_score, get_top_scores, create_score
)


class TestLoadScores(unittest.TestCase):
    """Test cases for load_scores function."""

    def test_load_scores_nonexistent_file(self):
        """Test that load_scores returns empty list if JSON file doesn't exist."""
        with tempfile.TemporaryDirectory() as tmp_dir:
            non_existent_path = pathlib.Path(tmp_dir) / "nonexistent.json"
            scores = load_scores(non_existent_path)

            self.assertEqual(scores, [])
            self.assertIsInstance(scores, list)

    def test_load_scores_empty_file(self):
        """Test loading from an empty JSON file."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as tmp_file:
            json.dump([], tmp_file)
            tmp_file_path = tmp_file.name

        try:
            scores = load_scores(tmp_file_path)
            self.assertEqual(scores, [])
        finally:
            os.unlink(tmp_file_path)

    def test_load_scores_valid_data(self):
        """Test loading valid score data from JSON file."""
        test_scores = [
            {
                "player": "alice",
                "word": "APPLE",
                "attempts": 3,
                "won": True,
                "date": "2024-01-01T12:00:00Z"
            },
            {
                "player": "bob",
                "word": "GRAPE",
                "attempts": 6,
                "won": False,
                "date": "2024-01-01T13:00:00Z"
            }
        ]

        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as tmp_file:
            json.dump(test_scores, tmp_file)
            tmp_file_path = tmp_file.name

        try:
            scores = load_scores(tmp_file_path)
            self.assertEqual(scores, test_scores)
        finally:
            os.unlink(tmp_file_path)

    def test_load_scores_invalid_json(self):
        """Test that load_scores raises RuntimeError for invalid JSON."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as tmp_file:
            tmp_file.write("invalid json content")
            tmp_file_path = tmp_file.name

        try:
            with self.assertRaises(RuntimeError) as context:
                load_scores(tmp_file_path)
            self.assertIn("Error loading scores", str(context.exception))
        finally:
            os.unlink(tmp_file_path)

    def test_load_scores_wrong_data_type(self):
        """Test that load_scores raises RuntimeError if file contains non-list."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as tmp_file:
            json.dump({"not": "a list"}, tmp_file)
            tmp_file_path = tmp_file.name

        try:
            with self.assertRaises(RuntimeError) as context:
                load_scores(tmp_file_path)
            self.assertIn("should contain a list", str(context.exception))
        finally:
            os.unlink(tmp_file_path)


class TestSaveScore(unittest.TestCase):
    """Test cases for save_score function."""

    def test_save_score_new_file(self):
        """Test saving score creates new file and can be loaded back."""
        test_score = {
            "player": "testuser",
            "word": "TIGER",
            "attempts": 4,
            "won": True,
            "date": "2024-01-01T14:00:00Z"
        }

        with tempfile.TemporaryDirectory() as tmp_dir:
            scores_path = pathlib.Path(tmp_dir) / "test_scores.json"

            # Save score
            save_score(scores_path, test_score)

            # Verify file was created and contains our score
            self.assertTrue(scores_path.exists())
            scores = load_scores(scores_path)
            self.assertEqual(len(scores), 1)
            self.assertEqual(scores[0], test_score)

    def test_save_score_append_to_existing(self):
        """Test that save_score appends to existing file."""
        existing_score = {
            "player": "existing",
            "word": "HORSE",
            "attempts": 2,
            "won": True,
            "date": "2024-01-01T10:00:00Z"
        }

        new_score = {
            "player": "newuser",
            "word": "WHALE",
            "attempts": 5,
            "won": False,
            "date": "2024-01-01T15:00:00Z"
        }

        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as tmp_file:
            json.dump([existing_score], tmp_file)
            tmp_file_path = tmp_file.name

        try:
            # Save new score
            save_score(tmp_file_path, new_score)

            # Verify both scores are there
            scores = load_scores(tmp_file_path)
            self.assertEqual(len(scores), 2)
            self.assertEqual(scores[0], existing_score)
            self.assertEqual(scores[1], new_score)
        finally:
            os.unlink(tmp_file_path)

    def test_save_score_validation_missing_fields(self):
        """Test that save_score validates required fields."""
        incomplete_score = {
            "player": "test",
            "word": "APPLE"
            # Missing: attempts, won, date
        }

        with tempfile.TemporaryDirectory() as tmp_dir:
            scores_path = pathlib.Path(tmp_dir) / "test.json"

            with self.assertRaises(ValueError) as context:
                save_score(scores_path, incomplete_score)
            self.assertIn("missing required fields", str(context.exception))

    def test_save_score_validation_wrong_types(self):
        """Test that save_score validates field types."""
        invalid_scores = [
            {
                "player": 123,  # Should be string
                "word": "APPLE",
                "attempts": 3,
                "won": True,
                "date": "2024-01-01T12:00:00Z"
            },
            {
                "player": "test",
                "word": "APPLE",
                "attempts": "three",  # Should be int
                "won": True,
                "date": "2024-01-01T12:00:00Z"
            },
            {
                "player": "test",
                "word": "APPLE",
                "attempts": 3,
                "won": "yes",  # Should be bool
                "date": "2024-01-01T12:00:00Z"
            }
        ]

        with tempfile.TemporaryDirectory() as tmp_dir:
            scores_path = pathlib.Path(tmp_dir) / "test.json"

            for invalid_score in invalid_scores:
                with self.assertRaises(ValueError):
                    save_score(scores_path, invalid_score)

    def test_save_score_negative_attempts(self):
        """Test that save_score rejects negative attempts."""
        invalid_score = {
            "player": "test",
            "word": "APPLE",
            "attempts": -1,
            "won": False,
            "date": "2024-01-01T12:00:00Z"
        }

        with tempfile.TemporaryDirectory() as tmp_dir:
            scores_path = pathlib.Path(tmp_dir) / "test.json"

            with self.assertRaises(ValueError) as context:
                save_score(scores_path, invalid_score)
            self.assertIn("non-negative integer", str(context.exception))


class TestGetTopScores(unittest.TestCase):
    """Test cases for get_top_scores function."""

    def test_get_top_scores_empty_list(self):
        """Test get_top_scores with empty score list."""
        result = get_top_scores([])
        self.assertEqual(result, [])

    def test_get_top_scores_sorting(self):
        """Test that get_top_scores sorts correctly."""
        # Create scores with different outcomes
        base_date = datetime(2024, 1, 1, 12, 0, 0)

        scores = [
            {
                "player": "loser",
                "word": "APPLE",
                "attempts": 6,
                "won": False,
                "date": base_date.isoformat() + "Z"
            },
            {
                "player": "winner_slow",
                "word": "GRAPE",
                "attempts": 5,
                "won": True,
                "date": base_date.isoformat() + "Z"
            },
            {
                "player": "winner_fast",
                "word": "PEACH",
                "attempts": 2,
                "won": True,
                "date": base_date.isoformat() + "Z"
            }
        ]

        top_scores = get_top_scores(scores)

        # Should be ordered: winner_fast, winner_slow, loser
        self.assertEqual(len(top_scores), 3)
        self.assertEqual(top_scores[0]["player"], "winner_fast")
        self.assertEqual(top_scores[1]["player"], "winner_slow")
        self.assertEqual(top_scores[2]["player"], "loser")

    def test_get_top_scores_limit(self):
        """Test that get_top_scores respects limit parameter."""
        scores = [
            {"player": f"player{i}", "word": "APPLE", "attempts": i, "won": True, "date": "2024-01-01T12:00:00Z"}
            for i in range(1, 6)  # 5 scores
        ]

        top_3 = get_top_scores(scores, limit=3)
        self.assertEqual(len(top_3), 3)

        # Should get the ones with fewest attempts (1, 2, 3)
        self.assertEqual(top_3[0]["attempts"], 1)
        self.assertEqual(top_3[1]["attempts"], 2)
        self.assertEqual(top_3[2]["attempts"], 3)

    def test_get_top_scores_recent_wins_prioritized(self):
        """Test that more recent wins are prioritized when attempts are equal."""
        old_date = datetime(2024, 1, 1, 12, 0, 0)
        new_date = old_date + timedelta(hours=1)

        scores = [
            {
                "player": "older",
                "word": "APPLE",
                "attempts": 3,
                "won": True,
                "date": old_date.isoformat() + "Z"
            },
            {
                "player": "newer",
                "word": "APPLE",
                "attempts": 3,
                "won": True,
                "date": new_date.isoformat() + "Z"
            }
        ]

        top_scores = get_top_scores(scores)

        # Newer should come first due to more recent date
        self.assertEqual(top_scores[0]["player"], "newer")
        self.assertEqual(top_scores[1]["player"], "older")


class TestCreateScore(unittest.TestCase):
    """Test cases for create_score function."""

    def test_create_score_structure(self):
        """Test that create_score returns properly structured score."""
        player = "testplayer"
        word = "APPLE"
        attempts = 4
        won = True

        score = create_score(player, word, attempts, won)

        # Check structure
        expected_fields = {"player", "word", "attempts", "won", "date"}
        self.assertEqual(set(score.keys()), expected_fields)

        # Check values
        self.assertEqual(score["player"], player)
        self.assertEqual(score["word"], word)
        self.assertEqual(score["attempts"], attempts)
        self.assertEqual(score["won"], won)

        # Check date format (should be ISO format with Z)
        self.assertIsInstance(score["date"], str)
        self.assertTrue(score["date"].endswith("Z"))

        # Should be parseable as datetime
        date_obj = datetime.fromisoformat(score["date"].replace('Z', '+00:00'))
        self.assertIsInstance(date_obj, datetime)

    def test_create_score_timestamp_recent(self):
        """Test that create_score generates recent timestamp."""
        before = datetime.now(timezone.utc)
        score = create_score("test", "APPLE", 3, True)
        after = datetime.now(timezone.utc)

        # Parse the timestamp from the score
        score_time_str = score["date"].replace('Z', '+00:00')
        score_time = datetime.fromisoformat(score_time_str)

        # Should be between before and after
        self.assertGreaterEqual(score_time, before)
        self.assertLessEqual(score_time, after)


if __name__ == "__main__":
    unittest.main(verbosity=2)
