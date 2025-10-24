#!/usr/bin/env python3
"""
AI Gemini CLI - Main Entry Point
A command-line interface bot using the Gemini API with enhanced features.
"""

import sys
import os

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from ai_gemini.main import main_logic

def main():
    # Default to 'chat' if no command provided
    if len(sys.argv) < 2:
        command = "chat"
        options = ""
    else:
        command = sys.argv[1]
        options = ' '.join(sys.argv[2:])

    result = main_logic(command, options)
    print(result)

if __name__ == "__main__":
    main()
