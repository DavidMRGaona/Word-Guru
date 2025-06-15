"""
Project structure validation tests for Word-Guru.

Tests that verify the project structure, file existence,
and basic content validation.
"""

import os
import sys
import unittest
from pathlib import Path

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


class TestProjectStructure(unittest.TestCase):
    """Test cases for project structure validation."""

    def setUp(self):
        """Set up test fixtures."""
        self.project_root = Path(__file__).parent.parent

    def test_required_files_exist(self):
        """Test that all required files are present."""
        required_files = [
            '__init__.py',
            '__main__.py',
            'game.py',
            'io_utils.py',
            'persistence.py',
            'daily.py',
            'play.py',
            'run.py',
            'words.txt',
            'README.md'
        ]

        for filename in required_files:
            file_path = self.project_root / filename
            self.assertTrue(file_path.exists(), f"Required file {filename} not found")

    def test_python_files_syntax(self):
        """Test that Python files have valid syntax."""
        python_files = [
            '__init__.py',
            '__main__.py',
            'game.py',
            'io_utils.py',
            'persistence.py',
            'daily.py',
            'play.py',
            'run.py'
        ]

        for filename in python_files:
            file_path = self.project_root / filename
            if file_path.exists():
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()

                try:
                    compile(content, filename, 'exec')
                except SyntaxError as e:
                    self.fail(f"Syntax error in {filename}: {e}")

    def test_module_imports(self):
        """Test that modules can be imported without errors."""
        modules_to_test = [
            'game',
            'io_utils',
            'persistence',
            'daily'
        ]

        for module_name in modules_to_test:
            try:
                __import__(module_name)
            except ImportError as e:
                self.fail(f"Failed to import {module_name}: {e}")

    def test_main_classes_exist(self):
        """Test that main classes and functions are defined."""
        # Test WordGuruGame class exists
        try:
            from game import WordGuruGame
            self.assertTrue(callable(WordGuruGame))
        except ImportError as e:
            self.fail(f"Failed to import WordGuruGame: {e}")

        # Test main utility functions exist
        try:
            from io_utils import color_letter, load_words
            self.assertTrue(callable(color_letter))
            self.assertTrue(callable(load_words))
        except ImportError as e:
            self.fail(f"Failed to import io_utils functions: {e}")

    def test_words_file_format(self):
        """Test that words.txt exists and is loadable."""
        words_file = self.project_root / 'words.txt'
        self.assertTrue(words_file.exists(), "words.txt file not found")

        # Test that the file can be loaded without errors
        try:
            from io_utils import load_words
            words = load_words(words_file)
            self.assertIsInstance(words, list, "load_words should return a list")
            self.assertGreater(len(words), 0, "words.txt should contain at least some words")
        except Exception as e:
            self.fail(f"words.txt file could not be loaded: {e}")

    def test_readme_content(self):
        """Test that README.md has basic content."""
        readme_file = self.project_root / 'README.md'
        self.assertTrue(readme_file.exists(), "README.md file not found")

        with open(readme_file, 'r', encoding='utf-8') as f:
            content = f.read()

        # Check for updated title
        self.assertIn('# Word-Guru', content)
        self.assertIn('customizable', content.lower())
        self.assertIn('wordle', content.lower())


class TestGameClass(unittest.TestCase):
    """Test cases for game class instantiation."""

    def test_game_initialization(self):
        """Test that WordGuruGame can be instantiated correctly."""
        try:
            from game import WordGuruGame

            # Test with simple word list
            test_words = ["APPLE", "GRAPE", "PEACH"]
            game = WordGuruGame(test_words)

            self.assertIsNotNone(game)
            self.assertEqual(game.word_list, test_words)
            self.assertEqual(game.max_attempts, 6)

        except Exception as e:
            self.fail(f"Failed to instantiate WordGuruGame: {e}")


if __name__ == "__main__":
    unittest.main(verbosity=2)
