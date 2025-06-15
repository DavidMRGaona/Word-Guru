"""
Word-Guru - Command Line Interface

A customizable Wordle-style word guessing game with daily word mode,
score tracking, and customizable gameplay options.
"""

import argparse
import pathlib
import sys

from daily import is_daily_completed, time_until_next_daily
from game import WordGuruGame
from io_utils import color_letter, load_words
from persistence import get_top_scores, load_scores


def show_stats(scores_path: str, limit: int = 10) -> None:
    """Display top scores from the scores file."""
    try:
        scores = load_scores(scores_path)
        top_scores = get_top_scores(scores, limit)

        if not top_scores:
            print("📊 No scores found yet. Play some games to see stats!")
            return

        print(f"📊 Top {len(top_scores)} Scores:")
        print("=" * 60)
        print(f"{'Rank':<4} {'Player':<15} {'Word':<8} {'Attempts':<8} {'Won':<5} {'Date':<12}")
        print("-" * 60)

        for i, score in enumerate(top_scores, 1):
            won_symbol = "✅" if score["won"] else "❌"
            date_str = score["date"][:10]  # Just the date part
            print(f"{i:<4} {score['player']:<15} {score['word']:<8} {score['attempts']:<8} {won_symbol:<5} {date_str:<12}")

    except Exception as e:
        print(f"❌ Error loading stats: {e}")


def play_interactive_game(game: WordGuruGame) -> None:
    """Run an interactive game session with user input."""
    game.start_game()

    while not game.is_finished():
        try:
            # Get user input
            guess = input(f"Enter your guess ({len(game.attempts) + 1}/{game.max_attempts}): ").strip()

            if not guess:
                continue

            # Process guess
            letter_statuses, feedback_summary = game.check_guess(guess)

            # Display colored feedback
            colored_letters = []
            for i, (letter, status) in enumerate(zip(guess, letter_statuses)):
                colored_letters.append(color_letter(letter, status))

            print("".join(colored_letters))

            # Show win/lose message
            if game.is_finished():
                if game.won:
                    print(f"🎉 Congratulations! You guessed '{game.current_word}' in {len(game.attempts)} attempts!")
                else:
                    print(f"💔 Game over! The word was '{game.current_word}'")

                # Show daily mode specific messages
                if game.daily_mode:
                    print(f"⏰ Next daily word in: {time_until_next_daily()}")

        except ValueError as e:
            print(f"❌ Invalid guess: {e}")
        except KeyboardInterrupt:
            print("\n👋 Thanks for playing!")
            break
        except EOFError:
            print("\n👋 Thanks for playing!")
            break


def main() -> None:
    """Main entry point for Word-Guru CLI."""
    parser = argparse.ArgumentParser(
        description="Word-Guru - A customizable Wordle-style word guessing game",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s                          # Play with default word list
  %(prog)s --daily                  # Play today's daily word
  %(prog)s --player Alice           # Set player name for scores
  %(prog)s --max-attempts 8         # Allow 8 attempts instead of 6
  %(prog)s --stats                  # Show top 10 scores
  %(prog)s --words animals.txt      # Use custom word list (animals)
  %(prog)s --words countries.txt    # Use custom word list (countries)
        """
    )

    # Game mode options
    parser.add_argument(
        "--daily", "-d",
        action="store_true",
        help="Play daily word mode (same word for all players each day)"
    )

    # Configuration options
    parser.add_argument(
        "--words",
        type=pathlib.Path,
        default="words.txt",
        help="Path to word list file (default: words.txt)"
    )

    parser.add_argument(
        "--player",
        type=str,
        default="anonymous",
        help="Player name for score tracking (default: anonymous)"
    )

    parser.add_argument(
        "--max-attempts",
        type=int,
        default=6,
        help="Maximum number of guess attempts (default: 6)"
    )

    parser.add_argument(
        "--scores-path",
        type=str,
        default="scores.json",
        help="Path to scores file (default: scores.json)"
    )

    # Action options
    parser.add_argument(
        "--stats",
        action="store_true",
        help="Show top 10 scores and exit"
    )

    args = parser.parse_args()

    # Validate arguments
    if args.max_attempts < 1:
        print("❌ Error: max-attempts must be at least 1")
        return 1

    if not args.words.exists():
        print(f"❌ Error: Word file '{args.words}' not found")
        return 1

    # Handle stats display
    if args.stats:
        show_stats(args.scores_path)
        return 0

    # Load words
    try:
        words = load_words(args.words)
        if not words:
            print(f"❌ Error: No valid words found in '{args.words}'")
            return 1
    except Exception as e:
        print(f"❌ Error loading words: {e}")
        return 1

    # Check daily mode restrictions
    if args.daily:
        if is_daily_completed(args.player, args.scores_path):
            print("🎯 Daily Word Already Completed!")
            print(f"You've already played today's daily word, {args.player}.")
            print(f"⏰ Next daily word available in: {time_until_next_daily()}")
            print("\n💡 Try playing without --daily flag for random words!")
            return 0

    # Create and run game
    try:
        game = WordGuruGame(
            word_list=words,
            max_attempts=args.max_attempts,
            scores_path=args.scores_path,
            player=args.player,
            daily_mode=args.daily
        )

        play_interactive_game(game)
        return 0

    except Exception as e:
        print(f"❌ Error starting game: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
