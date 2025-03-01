from typing import *
import os
import json
from openai import OpenAI
from openai.types.chat.chat_completion import Choice
import requests
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

# 从环境变量获取 API 密钥
api_key = os.getenv("KIMI_API_KEY")

client = OpenAI(
    base_url="https://api.moonshot.cn/v1",
    api_key=api_key
)

# search 工具的具体实现，这里我们只需要返回参数即可
def search_impl(arguments: Dict[str, Any]) -> Any:
    """
    在使用 Moonshot AI 提供的 search 工具的场合，只需要原封不动返回 arguments 即可，
    不需要额外的处理逻辑。

    但如果你想使用其他模型，并保留联网搜索的功能，那你只需要修改这里的实现（例如调用搜索
    和获取网页内容等），函数签名不变，依然是 work 的。

    这最大程度保证了兼容性，允许你在不同的模型间切换，并且不需要对代码有破坏性的修改。
    """
    return arguments


def chat(messages) -> Choice:
    completion = client.chat.completions.create(
        model="moonshot-v1-128k",
        messages=messages,
        temperature=0.3,
        tools=[
            {
                "type": "builtin_function",  # <-- 使用 builtin_function 声明 $web_search 函数，请在每次请求都完整地带上 tools 声明
                "function": {
                    "name": "$web_search",
                },
            }
        ]
    )
    return completion.choices[0]


def kimi_search(query, num=3):
    # 从环境变量获取 API 密钥
    api_key = os.getenv("KIMI_API_KEY")
    
    url = "https://api.moonshot.cn/v1/chat/completions"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}"
    }
    
    data = {
        "model": "moonshot-v1-128k",
        "messages": [
            {
                "role": "system",
                "content": f"你是一个联网搜索助手，请根据用户的问题，返回{num}条相关的搜索结果，每条结果包含标题和内容摘要。"
            },
            {
                "role": "user",
                "content": query
            }
        ],
        "tools": [
            {
                "type": "web_search"
            }
        ]
    }
    
    try:
        response = requests.post(url, headers=headers, json=data)
        response.raise_for_status()
        result = response.json()
        return result["choices"][0]["message"]["content"]
    except Exception as e:
        return f"搜索出错: {str(e)}"


if __name__ == "__main__":
    print(kimi_search("什么是JetBay?"))
