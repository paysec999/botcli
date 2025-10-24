import unittest
from src.cli import main

class TestCLI(unittest.TestCase):

    def test_cli_initialization(self):
        # Test if the CLI initializes correctly
        result = main.initialize_cli()
        self.assertIsNotNone(result)

    def test_user_input_processing(self):
        # Test if user input is processed correctly
        user_input = "Hello, how can I help you?"
        response = main.process_input(user_input)
        self.assertIn("response", response)

if __name__ == '__main__':
    unittest.main()