# Word-Guru 🎯

A customizable Wordle-style word guessing game that works with any theme! Create your own word lists for animals, countries, technology, food, or any topic you love.

## Features ✨

- **🎲 Multiple Game Modes**: Random words or daily challenges
- **📊 Score Tracking**: Persistent statistics and leaderboards
- **🎨 Colorful Interface**: Visual feedback with colored letters
- **🔧 Fully Customizable**: Use any word list you want
- **📅 Daily Word Mode**: Same word for all players each day
- **🏆 Player Statistics**: Track wins, attempts, and progress
- **🚀 Zero Dependencies**: Pure Python, no external packages needed

## Quick Start 🚀

### Option 1: Simple Launch
```bash
python3 play.py
```

### Option 2: Alternative Launcher
```bash
python3 run.py
```

### Option 3: Direct Main Module
```bash
python3 __main__.py
```

## Game Modes 🎮

### Random Mode (Default)
```bash
python3 play.py
```
Play with a random word from your word list.

### Daily Mode
```bash
python3 play.py --daily
```
Everyone gets the same word each day. Perfect for competing with friends!

## Custom Word Lists 📝

The magic of Word-Guru is its flexibility. Create themed word lists for any topic:

### Creating Your Own Word List

1. **Create a text file** (e.g., `animals.txt`)
2. **Add 5-letter words**, one per line, in UPPERCASE
3. **Use comments** with `#` for organization
4. **Play with your list**: `python3 play.py --words animals.txt`

### Example Word Lists

**Animals Theme (`animals.txt`):**
```
# Wild Animals
TIGER
WHALE
EAGLE
SHARK
ZEBRA

# Farm Animals
HORSE
SHEEP
GOOSE
```

**Countries Theme (`countries.txt`):**
```
# European Countries
SPAIN
ITALY
FRANCE

# Asian Countries
JAPAN
CHINA
INDIA
```

**Food Theme (`food.txt`):**
```
# Italian Food
PIZZA
PASTA

# Fruits
APPLE
GRAPE
LEMON
```

## Command Line Options 🛠️

```bash
# Basic gameplay
python3 play.py                          # Random word from default list
python3 play.py --daily                  # Today's daily word
python3 play.py --player Alice           # Set player name for scores

# Custom word lists
python3 play.py --words animals.txt      # Use animal words
python3 play.py --words countries.txt    # Use country names
python3 play.py --words food.txt         # Use food terms

# Game settings
python3 play.py --max-attempts 8         # Allow 8 attempts instead of 6
python3 play.py --scores-path my_scores.json  # Custom scores file

# Statistics
python3 play.py --stats                  # Show top 10 scores
```

## How to Play 🎯

1. **Guess the 5-letter word** in 6 attempts or less
2. **Get color-coded feedback** after each guess:
   - 🟩 **Green**: Letter is correct and in the right position
   - 🟨 **Yellow**: Letter is in the word but wrong position
   - ⬜ **White**: Letter is not in the word
3. **Use the clues** to narrow down your next guess
4. **Win by guessing** the word within the attempt limit!

## Example Game Session 🎮

```
🎯 Word-Guru Started!
Guess the 5-letter word in 6 attempts!

Enter your guess (1/6): HOUSE
🟨 H 🟩 O ⬜ U ⬜ S 🟨 E

Enter your guess (2/6): PHONE
⬜ P 🟩 H 🟩 O ⬜ N 🟩 E

Enter your guess (3/6): THOSE
⬜ T 🟩 H 🟩 O ⬜ S 🟩 E

Enter your guess (4/6): WHOLE
⬜ W 🟩 H 🟩 O ⬜ L 🟩 E

Enter your guess (5/6): CHORE
🟩 C 🟩 H 🟩 O 🟩 R 🟩 E

🎉 Congratulations! You guessed 'CHORE' in 5 attempts!
💾 Score saved for player 'anonymous'
```

## Theme Ideas 💡

Get creative with your word lists! Here are some theme ideas:

- **🐾 Animals**: TIGER, WHALE, EAGLE, SHARK, HORSE
- **🌍 Geography**: SPAIN, ITALY, JAPAN, EGYPT, CHILE
- **🍕 Food**: PIZZA, BREAD, APPLE, GRAPE, HONEY
- **🎨 Colors**: BLACK, WHITE, GREEN, BROWN, CORAL
- **⚽ Sports**: RUGBY, CHESS, GOLF, TRACK, SKATE
- **🔬 Science**: ATOMS, LASER, ORBIT, GENES, VIRUS
- **🎵 Music**: PIANO, DRUMS, FLUTE, OPERA, BLUES
- **🌊 Nature**: OCEAN, RIVER, STORM, FIELD, BEACH
- **🚀 Space**: EARTH, VENUS, COMET, LUNAR, SOLAR
- **💻 Technology**: CLOUD, LINUX, REACT, SWIFT, MYSQL
- **🏛️ History**: ROMAN, GREEK, AZTEC, MAYAN, VIKING
- **🎭 Movies**: DRAMA, COMIC, ACTOR, SCENE, STAGE

## Statistics & Scoring 📊

View your performance and compete with others:

```bash
python3 play.py --stats
```

```
📊 Top 10 Scores:
============================================================
Rank Player          Word     Attempts Won   Date
------------------------------------------------------------
1    Alice           TIGER    2        ✅    2024-01-15
2    Bob             WHALE    3        ✅    2024-01-15
3    Charlie         EAGLE    4        ✅    2024-01-14
```

## Technical Details 🔧

- **Python Version**: 3.9+
- **Dependencies**: None! Pure Python standard library
- **File Format**: Simple text files with one word per line
- **Score Storage**: JSON format for easy portability
- **Cross-Platform**: Works on Windows, macOS, and Linux

## File Structure 📁

```
word-guru/
├── __init__.py          # Package initialization
├── __main__.py          # CLI interface
├── game.py              # Core game logic
├── io_utils.py          # Input/output utilities
├── persistence.py       # Score saving/loading
├── daily.py             # Daily word functionality
├── play.py              # Simple launcher
├── run.py               # Alternative launcher
├── words.txt            # Default multi-theme word list
├── scores.json          # Player statistics (auto-created)
└── tests/               # Test suite
    ├── test_core.py
    ├── test_daily.py
    └── test_persistence.py
```

## Contributing 🤝

Word-Guru is designed to be simple and extensible. Feel free to:

- Create and share interesting word lists
- Suggest new features or improvements
- Report bugs or issues
- Add support for different word lengths
- Implement new game modes

## License 📄

GPL v3 License - This program is free software: you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.

This ensures Word-Guru remains free and open source forever! 🔓

---

**Happy word guessing! 🎯✨**

*Create your own themed Wordle experience with Word-Guru!*
