# Contents of /ai-gemini-cli/ai-gemini-cli/src/ai_gemini/main.py

import sys
from ai_gemini.commands.chat import ChatCommand
from ai_gemini.commands.stream import StreamCommand
from ai_gemini.services.gemini_service import GeminiService
from ai_gemini.utils.logger import setup_logger

def main_logic(command, options):
    setup_logger()

    # Initialize services and commands
    try:
        gemini_service = GeminiService()
    except ValueError as e:
        return f"Error: {e}"
    chat_command = ChatCommand(gemini_service)
    stream_command = StreamCommand(gemini_service)

    # Command-line interface logic
    if command == "chat":
        chat_command.execute(options.split() if options else [])
        return "Chat command executed"
    elif command == "stream":
        stream_command.execute(options.split() if options else [])
        return "Stream command executed"
    else:
        # If unknown command, treat as chat input
        chat_command.execute([command] + (options.split() if options else []))
        return "Chat command executed"

def main():
    setup_logger()

    # Initialize services and commands
    try:
        gemini_service = GeminiService()
    except ValueError as e:
        print(f"Error: {e}")
        sys.exit(1)
    chat_command = ChatCommand(gemini_service)
    stream_command = StreamCommand(gemini_service)

    # Command-line interface logic
    if len(sys.argv) < 2:
        print("Usage: ai-gemini-cli <command> [options]")
        sys.exit(1)

    command = sys.argv[1]
    options = ' '.join(sys.argv[2:])

    result = main_logic(command, options)
    print(result)

if __name__ == "__main__":
    main()
