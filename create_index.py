import openai
import numpy as np
import faiss
import json
from docx import Document
import asyncio
import os
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

# 从环境变量获取 API 密钥
api_key = os.getenv("OPENAI_API_KEY")
client = openai.AsyncOpenAI(api_key=api_key)

async def get_embedding(text):
    response = await client.embeddings.create(input=[text], model="text-embedding-ada-002")
    return np.array(response.data[0].embedding)

def extract_text_from_docx(file_path):
    doc = Document(file_path)
    return "\n".join([para.text.strip() for para in doc.paragraphs if para.text.strip()])

async def create_faiss_index():
    # 加载文档
    ai_doc_text = extract_text_from_docx("AI Doc.docx")
    workflow_text = extract_text_from_docx("jetbay_workflow.docx")
    workflow_en_text = extract_text_from_docx("jetbay_workflow_EN.docx")
    
    # 加载 FAQ 数据
    with open("jetbay-intro.json", "r", encoding="utf-8") as f:
        faq_data = json.load(f)
    
    # 合并所有数据源
    data = [
        {"text": ai_doc_text, "source": "ai_doc"},
        {"text": workflow_text, "source": "workflow_cn"},
        {"text": workflow_en_text, "source": "workflow_en"},
    ] + [{"text": item["question"] + " " + item["answer"], "source": "json"} for item in faq_data]
    
    # 获取所有文本的嵌入
    embeddings = []
    print("Creating embeddings...")
    for i, item in enumerate(data):
        print(f"Processing document {i+1}/{len(data)}")
        embedding = await get_embedding(item["text"])
        embeddings.append(embedding)
    
    # 创建 FAISS 索引
    dimension = len(embeddings[0])
    index = faiss.IndexFlatL2(dimension)
    
    # 将嵌入添加到索引中
    embeddings_array = np.array(embeddings).astype('float32')
    index.add(embeddings_array)
    
    # 保存索引和数据
    faiss.write_index(index, "jetbay_faiss.index")
    
    # 保存数据以供后续使用
    with open("knowledge_base_data.json", "w", encoding="utf-8") as f:
        json.dump([{"text": item["text"], "source": item["source"]} for item in data], f, ensure_ascii=False, indent=2)

    print("Index created successfully!")

if __name__ == "__main__":
    asyncio.run(create_faiss_index()) 