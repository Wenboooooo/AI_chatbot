import unittest
from smart_chatbot import SmartChatbot

class TestSmartChatbot(unittest.TestCase):
    def setUp(self):
        """Set up test fixtures before each test method."""
        self.chatbot = SmartChatbot()

    def test_web_search(self):
        """Test the web search functionality"""
        # Test with a query that should return results
        query = "What is the latest news about SpaceX?"
        result = self.chatbot.web_search(query)
        self.assertIsNotNone(result)
        self.assertIsInstance(result, str)
        self.assertTrue(len(result) > 0)

        # Test with an empty query
        empty_result = self.chatbot.web_search("")
        self.assertIsNone(empty_result)

    def test_should_use_web_search(self):
        """Test the web search decision functionality"""
        # Test with queries that should trigger web search
        current_events_query = "What are the latest developments in AI technology?"
        self.assertTrue(self.chatbot.should_use_web_search(current_events_query))

        # Test with queries that might not need web search
        basic_query = "What is 2 + 2?"
        result = self.chatbot.should_use_web_search(basic_query)
        self.assertIsInstance(result, bool)

    def test_get_response(self):
        """Test the main response generation functionality"""
        # Test with a simple query
        simple_query = "Hello, how are you?"
        response = self.chatbot.get_response(simple_query)
        self.assertIsNotNone(response)
        self.assertIsInstance(response, str)
        self.assertTrue(len(response) > 0)

        # Test with a query that might trigger web search
        complex_query = "What are the current global climate change statistics?"
        response = self.chatbot.get_response(complex_query)
        self.assertIsNotNone(response)
        self.assertIsInstance(response, str)
        self.assertTrue(len(response) > 0)

    def test_error_handling(self):
        """Test error handling in various scenarios"""
        # Test with invalid API keys (temporarily modify the keys)
        original_gpt4_key = self.chatbot.gpt4_api_key
        self.chatbot.gpt4_api_key = "invalid_key"
        
        response = self.chatbot.get_response("Test query")
        self.assertTrue("Error" in response)
        
        # Restore the original key
        self.chatbot.gpt4_api_key = original_gpt4_key

def run_interactive_test():
    """Run an interactive test session with the chatbot"""
    chatbot = SmartChatbot()
    print("\n=== Interactive Test Session ===")
    print("This will run a series of predefined test queries.")
    print("Press Enter after each response to continue, or type 'quit' to exit.")

    test_queries = [
        "What is artificial intelligence?",
        "What are the latest developments in quantum computing?",
        "Tell me a joke about programming.",
        "What is the current situation in global economics?",
        "Explain the concept of machine learning in simple terms."
    ]

    for query in test_queries:
        input("\nPress Enter to test next query (or type 'quit'): ")
        if input().lower() == 'quit':
            break
            
        print(f"\nTest Query: {query}")
        print("\nProcessing...")
        response = chatbot.get_response(query)
        print(f"\nChatbot Response:\n{response}")

if __name__ == '__main__':
    # First run unit tests
    print("Running unit tests...")
    unittest.main(argv=['first-arg-is-ignored'], exit=False)
    
    # Then offer to run interactive tests
    while True:
        choice = input("\nWould you like to run interactive tests? (yes/no): ").lower()
        if choice in ['yes', 'y']:
            run_interactive_test()
            break
        elif choice in ['no', 'n']:
            break
        else:
            print("Please enter 'yes' or 'no'") 