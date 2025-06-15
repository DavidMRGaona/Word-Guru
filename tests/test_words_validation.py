"""
Test suite for word list validation functionality.

Tests validate the format and structure of word files without depending
on specific content, ensuring tests work with any valid custom word list.
"""

import unittest
import os
import sys
from pathlib import Path

# Add the parent directory to the path so we can import our modules
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from io_utils import load_words


class TestWordFileFormat(unittest.TestCase):
    """Test word file format validation - works with any valid content."""

    def setUp(self):
        """Set up test fixtures."""
        self.project_root = Path(__file__).parent.parent
        self.words_file = self.project_root / 'words.txt'

    def test_words_file_exists(self):
        """Test that words.txt file exists."""
        self.assertTrue(self.words_file.exists(),
                       "words.txt file must exist (this is the default word list)")

    def test_words_file_loadable(self):
        """Test that words.txt file can be loaded without errors."""
        try:
            words = load_words(self.words_file)
            self.assertIsInstance(words, list, "load_words should return a list")
            self.assertGreater(len(words), 0, "words.txt should contain at least some words")
        except Exception as e:
            self.fail(f"words.txt file could not be loaded: {e}")

    def test_all_words_exactly_5_letters(self):
        """Test that all words have exactly 5 letters."""
        words = load_words(self.words_file)

        invalid_words = []
        for word in words:
            if len(word) != 5:
                invalid_words.append(f"'{word}' (length: {len(word)})")

        if invalid_words:
            error_msg = f"Found {len(invalid_words)} words that don't have exactly 5 letters:\n"
            error_msg += "\n".join(f"  {word}" for word in invalid_words[:10])  # Show first 10
            if len(invalid_words) > 10:
                error_msg += f"\n  ... and {len(invalid_words) - 10} more"
            self.fail(error_msg)

    def test_all_words_uppercase(self):
        """Test that all words are in uppercase."""
        words = load_words(self.words_file)

        invalid_words = []
        for word in words:
            if not word.isupper():
                invalid_words.append(f"'{word}'")

        if invalid_words:
            error_msg = f"Found {len(invalid_words)} words that are not in uppercase:\n"
            error_msg += "\n".join(f"  {word}" for word in invalid_words[:10])  # Show first 10
            if len(invalid_words) > 10:
                error_msg += f"\n  ... and {len(invalid_words) - 10} more"
            self.fail(error_msg)

    def test_all_words_alphabetic(self):
        """Test that all words contain only alphabetic characters."""
        words = load_words(self.words_file)

        invalid_words = []
        for word in words:
            if not word.isalpha():
                invalid_words.append(f"'{word}'")

        if invalid_words:
            error_msg = f"Found {len(invalid_words)} words with non-alphabetic characters:\n"
            error_msg += "\n".join(f"  {word}" for word in invalid_words[:10])  # Show first 10
            if len(invalid_words) > 10:
                error_msg += f"\n  ... and {len(invalid_words) - 10} more"
            self.fail(error_msg)

    def test_no_duplicate_words(self):
        """Test that there are no duplicate words."""
        words = load_words(self.words_file)

        duplicates = []
        seen = set()

        for word in words:
            if word in seen:
                duplicates.append(word)
            else:
                seen.add(word)

        if duplicates:
            unique_duplicates = list(set(duplicates))
            error_msg = f"Found {len(unique_duplicates)} duplicate words: {', '.join(unique_duplicates[:10])}"
            if len(unique_duplicates) > 10:
                error_msg += f" ... and {len(unique_duplicates) - 10} more"
            self.fail(error_msg)

    def test_minimum_word_count(self):
        """Test that we have a reasonable number of words for gameplay."""
        words = load_words(self.words_file)
        self.assertGreaterEqual(len(words), 10,
                               "Should have at least 10 words for meaningful gameplay")

    def test_words_file_format_consistency(self):
        """Test that the raw file format is consistent."""
        with open(self.words_file, 'r', encoding='utf-8') as f:
            lines = f.readlines()

        issues = []

        for line_num, line in enumerate(lines, 1):
            original_line = line
            line = line.strip()

            # Skip comments and empty lines
            if not line or line.startswith('#'):
                continue

            # Check for common formatting issues
            if original_line != line + '\n' and original_line != line:
                issues.append(f"Line {line_num}: Extra whitespace around '{line}'")

            if line != line.upper():
                issues.append(f"Line {line_num}: '{line}' should be uppercase")

            if len(line) != 5:
                issues.append(f"Line {line_num}: '{line}' should be exactly 5 letters")

            if not line.isalpha():
                issues.append(f"Line {line_num}: '{line}' should contain only letters")

        if issues:
            error_msg = f"Found {len(issues)} formatting issues:\n"
            error_msg += "\n".join(f"  {issue}" for issue in issues[:10])  # Show first 10
            if len(issues) > 10:
                error_msg += f"\n  ... and {len(issues) - 10} more"
            self.fail(error_msg)


class TestControlledWordList(unittest.TestCase):
    """Test validation logic using a controlled test word list."""

    def setUp(self):
        """Set up test fixtures."""
        self.test_dir = Path(__file__).parent
        self.test_words_file = self.test_dir / 'test_words.txt'

    def test_test_words_file_exists(self):
        """Test that test_words.txt file exists for validation testing."""
        self.assertTrue(self.test_words_file.exists(),
                       "test_words.txt file must exist for testing validation logic")

    def test_validation_logic_with_known_good_data(self):
        """Test that validation logic works correctly with known good data."""
        words = load_words(self.test_words_file)

        # All words should pass validation
        self.assertGreater(len(words), 0, "Test file should have words")

        for word in words:
            self.assertEqual(len(word), 5, f"Test word '{word}' should have 5 letters")
            self.assertTrue(word.isupper(), f"Test word '{word}' should be uppercase")
            self.assertTrue(word.isalpha(), f"Test word '{word}' should be alphabetic")

        # No duplicates in test file
        self.assertEqual(len(words), len(set(words)), "Test file should have no duplicates")


if __name__ == '__main__':
    unittest.main(verbosity=2)
