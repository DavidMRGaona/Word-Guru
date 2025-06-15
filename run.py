#!/usr/bin/env python3
"""
Word-Guru - Simple launcher script
Run this file to start the game!
"""

if __name__ == "__main__":
    import sys
    import os

    # Add current directory to path to import __main__.py
    current_dir = os.path.dirname(os.path.abspath(__file__))
    sys.path.insert(0, current_dir)

    # Import and run main from __main__.py
    import importlib.util
    spec = importlib.util.spec_from_file_location("main_module", os.path.join(current_dir, "__main__.py"))
    main_module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(main_module)

    sys.exit(main_module.main())
