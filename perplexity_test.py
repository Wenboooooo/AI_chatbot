import json
from openai import OpenAI
import os
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

def perplexity_search(Query):
    # 从环境变量获取 API 密钥
    YOUR_API_KEY = os.getenv("PERPLEXITY_API_KEY")

    messages = [
        {
            "role": "system",
            "content": (
                "你是Avigo旗下的Base-DO模型的AI联网搜索工具，请你根据用户的提问，以JSON的形式返回你从互联网上搜索到的至少3个相关内容，以title、abstract、text三个内容进行返回"
            ),
        },
        {
            "role": "user",
            "content": (
                Query
            ),
        },
    ]

    client = OpenAI(api_key=YOUR_API_KEY, base_url="https://api.perplexity.ai")

    # chat completion without streaming
    response = client.chat.completions.create(
        model="llama-3.1-sonar-large-128k-online",
        messages=messages,
    )
    data = response.model_dump_json()
    data = json.loads(data)
    return data['choices'][0]['message']['content']


if __name__ == "__main__":
    print(perplexity_search("什么是Avigo？"))
