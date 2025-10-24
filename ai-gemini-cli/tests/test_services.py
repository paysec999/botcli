import unittest
from ai_gemini.services.gemini_service import GeminiService

class TestGeminiService(unittest.TestCase):

    def setUp(self):
        self.service = GeminiService()

    def test_api_connection(self):
        response = self.service.connect()
        self.assertTrue(response['success'])

    def test_get_data(self):
        data = self.service.get_data()
        self.assertIsNotNone(data)
        self.assertIn('result', data)

    def test_handle_error(self):
        with self.assertRaises(Exception):
            self.service.handle_error('Some error')

if __name__ == '__main__':
    unittest.main()