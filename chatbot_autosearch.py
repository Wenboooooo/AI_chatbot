import openai
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
import faiss
import numpy as np
import json
from docx import Document
from typing import Dict, List
from starlette.websockets import WebSocketState
# from perplexity_test import kimi_search
from kimi_test import kimi_search
import websockets
import asyncio
import os
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

# 从环境变量获取 API 密钥
api_key = os.getenv("OPENAI_API_KEY")

# **使用 OpenAI 的异步客户端**
client = openai.AsyncOpenAI(api_key=api_key)

# **FastAPI 应用**
app = FastAPI()

# **存储每个用户的聊天历史**
user_chat_histories: Dict[str, List[Dict[str, str]]] = {}


class FAISSRetriever:
    def __init__(self, index_path, data):
        self.index = faiss.read_index(index_path)
        self.data = data
    
    async def search(self, query, top_k=2):
        query_embedding = await get_embedding(query)
        query_embedding = query_embedding.reshape(1, -1)
        D, I = self.index.search(query_embedding, top_k)
        results = [self.data[i]["text"] for i in I[0]]
        return results


# **获取文本嵌入**
async def get_embedding(text):
    response = await client.embeddings.create(input=[text], model="text-embedding-ada-002")
    return np.array(response.data[0].embedding)

# **加载知识库**
def extract_text_from_docx(file_path):
    doc = Document(file_path)
    return "\n".join([para.text.strip() for para in doc.paragraphs if para.text.strip()])

docx_text = extract_text_from_docx("AI Doc.docx")

with open("jetbay-intro.json", "r", encoding="utf-8") as f:
    faq_data = json.load(f)

data = [{"text": docx_text, "source": "docx"}] + [{"text": item["question"] + " " + item["answer"], "source": "json"} for item in faq_data]

retriever = FAISSRetriever("jetbay_faiss.index", data)


@app.websocket("/chat/{user_id}")
async def websocket_endpoint(websocket: WebSocket, user_id: str):
    await websocket.accept()
    
    if user_id not in user_chat_histories:
        user_chat_histories[user_id] = []

    try:
        while True:
            try:
                # **接收用户输入**
                user_query = await websocket.receive_text()

                # **检索知识库和联网搜索**
                retrieved_context = await retriever.search(user_query, top_k=3)
                online_search_results = kimi_search(user_query, num=3)

                # **存储用户输入**
                user_chat_histories[user_id].append({"role": "user", "content": user_query})

                # **构造对话历史**
                conversation = [
                    {"role": "system", "content": """
                    You are a JetBay intelligent assistant tasked with answering user queries.
                    Provide precise, relevant, and natural responses based on the available information.
                    Do not mention the source of your information in your response.
                    """},
                    {"role": "system", "content": f"Context: {retrieved_context}"},
                    {"role": "system", "content": f"Additional Information: {online_search_results}"},
                ] + user_chat_histories[user_id]

                # **发送流式响应**
                response_stream = await client.chat.completions.create(
                    model="gpt-4o",
                    messages=conversation,
                    temperature=0.7,
                    stream=True
                )

                ai_response = ""
                async for chunk in response_stream:
                    if chunk.choices and chunk.choices[0].delta and chunk.choices[0].delta.content:
                        token = chunk.choices[0].delta.content
                        ai_response += token
                        await websocket.send_text(token)

                # **存储完整 AI 响应**
                user_chat_histories[user_id].append({"role": "assistant", "content": ai_response})

                # **发送流结束标志**
                await websocket.send_text("END_STREAM")

            except WebSocketDisconnect:
                print(f"WebSocket disconnected for user {user_id}")
                break
            except Exception as e:
                print(f"Error processing message: {e}")
                await websocket.send_text(f"Error: {str(e)}")
                await websocket.send_text("END_STREAM")

    except Exception as e:
        print(f"WebSocket Error: {e}")
    finally:
        if websocket.client_state != WebSocketState.DISCONNECTED:
            await websocket.close()


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        app, 
        host="0.0.0.0", 
        port=8001,
        timeout_keep_alive=0,  # 禁用 keep-alive 超时
        ws_ping_interval=None,  # 禁用 WebSocket ping
        ws_ping_timeout=None,  # 禁用 ping 超时
    ) 