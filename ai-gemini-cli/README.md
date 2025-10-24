# AI Gemini CLI Bot

## Overview
The AI Gemini CLI Bot is a command-line interface application that interacts with the Gemini API to provide AI-driven chat and streaming functionalities. This project is designed to be modular and easy to extend, allowing developers to add new features and commands as needed.

## Project Structure
```
ai-gemini-cli
├── src
│   ├── cli.py
│   └── ai_gemini
│       ├── __init__.py
│       ├── main.py
│       ├── commands
│       │   ├── chat.py
│       │   └── stream.py
│       ├── services
│       │   └── gemini_service.py
│       ├── config
│       │   └── __init__.py
│       └── utils
│           ├── logger.py
│           └── prompt.py
├── tests
│   ├── test_cli.py
│   └── test_services.py
├── pyproject.toml
├── requirements.txt
├── .env.example
└── README.md
```

## Installation
To get started with the AI Gemini CLI Bot, clone the repository and install the required dependencies:

```bash
git clone <repository-url>
cd ai-gemini-cli
pip install -r requirements.txt
```

## Usage
To run the CLI bot, execute the following command:

```bash
python src/cli.py
```

You can interact with the bot by entering commands in the terminal. The bot supports various commands defined in the `commands` module.

## Configuration
Before using the bot, make sure to set up your environment variables. You can find an example in the `.env.example` file. Copy this file to `.env` and fill in the necessary values, such as your Gemini API key.

## Testing
To run the tests for the CLI and services, use the following command:

```bash
pytest tests/
```

## Contributing
Contributions are welcome! Please fork the repository and submit a pull request with your changes. Make sure to include tests for any new features or bug fixes.

## License
This project is licensed under the MIT License. See the LICENSE file for more details.