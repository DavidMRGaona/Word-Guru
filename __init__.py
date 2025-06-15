"""
Word-Guru: A customizable Wordle-style word guessing game.

A terminal-based word guessing game inspired by Wordle, designed to work
with any custom word list. Features daily word mode, score tracking,
and customizable gameplay options.
"""

__version__ = "1.0.0"
__author__ = "David Manuel Ramos Gaona"
__description__ = "A customizable Wordle-style word guessing game"

__all__ = ['WordGuruGame']

from .game import WordGuruGame
