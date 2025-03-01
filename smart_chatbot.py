import os
import requests
import json
from typing import Optional, Dict, Any
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

# 从环境变量获取 API 密钥
api_key = os.getenv("OPENAI_API_KEY")

class SmartChatbot:
    def __init__(self):
        # Initialize API keys
        self.gpt4_api_key = api_key
        self.perplexity_api_key = "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"
        
        # API endpoints
        self.gpt4_endpoint = "https://api.openai.com/v1/chat/completions"
        self.perplexity_search_endpoint = "https://api.perplexity.ai/v1/search"
        
    def web_search(self, query: str) -> Optional[str]:
        """Perform web search using Perplexity API"""
        headers = {
            "Authorization": f"Bearer {self.perplexity_api_key}",
            "Content-Type": "application/json"
        }
        
        data = {
            "query": query,
            "limit": 5  # Get top 5 results
        }
        
        print(f"Sending request to Perplexity API with data: {data}")  # Log the request data
        
        try:
            response = requests.post(self.perplexity_search_endpoint, headers=headers, json=data)
            response.raise_for_status()  # This will raise an error for 4xx and 5xx responses
            results = response.json()
            
            # Format search results into a string
            formatted_results = "\n".join([
                f"Source: {result['url']}\nSummary: {result['snippet']}\n"
                for result in results.get('results', [])
            ])
            
            return formatted_results
        except requests.exceptions.HTTPError as e:
            print(f"Web search error: {str(e)}")
            print(f"Response content: {e.response.text}")  # Print the response content for debugging
            return None
        except requests.exceptions.RequestException as e:
            print(f"Web search error: {str(e)}")
            if 'NameResolutionError' in str(e):
                print("Please check your network connection or the API endpoint.")
            return None

    def should_use_web_search(self, query: str) -> bool:
        """Determine if web search would be beneficial for the query"""
        # Ask GPT-4 to decide if web search would be helpful
        headers = {
            "Authorization": f"Bearer {self.gpt4_api_key}",
            "Content-Type": "application/json"
        }
        
        messages = [
            {"role": "system", "content": "You are a helpful assistant. Your task is to determine if a web search would be beneficial to answer the user's query. Respond with 'Yes' or 'No' only."},
            {"role": "user", "content": f"Would a web search be helpful to answer this query? Query: {query}"}
        ]
        
        try:
            response = requests.post(
                self.gpt4_endpoint,
                headers=headers,
                json={
                    "model": "gpt-4",
                    "messages": messages,
                    "temperature": 0.3
                }
            )
            response.raise_for_status()
            decision = response.json()['choices'][0]['message']['content'].strip().lower()
            return decision == 'yes'
        except Exception as e:
            print(f"Error in decision making: {str(e)}")
            return False

    def get_response(self, user_query: str) -> str:
        """Generate response using GPT-4 and web search if needed"""
        # First, decide if web search is needed
        need_web_search = self.should_use_web_search(user_query)
        
        # Prepare context with web search results if needed
        context = ""
        if need_web_search:
            search_results = self.web_search(user_query)
            if search_results:
                context = f"\nRelevant web search results:\n{search_results}\n"
        
        # Prepare messages for GPT-4
        headers = {
            "Authorization": f"Bearer {self.gpt4_api_key}",
            "Content-Type": "application/json"
        }
        
        system_message = (
            "You are a helpful assistant. Provide accurate and informative responses. "
            "If web search results are provided, incorporate that information into your response."
        )
        
        messages = [
            {"role": "system", "content": system_message},
            {"role": "user", "content": f"{user_query}{context}"}
        ]
        
        try:
            response = requests.post(
                self.gpt4_endpoint,
                headers=headers,
                json={
                    "model": "gpt-4",
                    "messages": messages,
                    "temperature": 0.7
                }
            )
            response.raise_for_status()
            return response.json()['choices'][0]['message']['content']
        except Exception as e:
            return f"Error generating response: {str(e)}"

def main():
    chatbot = SmartChatbot()
    print("Welcome to SmartChatbot! Type 'quit' to exit.")
    
    while True:
        user_input = input("\nYou: ").strip()
        if user_input.lower() == 'quit':
            print("Goodbye!")
            break
            
        response = chatbot.get_response(user_input)
        print("\nChatbot:", response)

if __name__ == "__main__":
    main() 