from tools.search_tool import search
from tools.scraper import scrape
from utils.cleaner import clean_text
from utils.chunker import chunk_text
from vectorstore.chroma_db import store_chunks
from vectorstore.retriever import retrieve
from llm import llm

def research_pipeline(topic):
    results = search(topic)

    articles = []

    for result in results:
        try:
            if "youtube.com" in result["url"] or "youtu.be" in result["url"]:
                continue
            article = scrape(result["url"])
            article = clean_text(article)

            chunks = chunk_text(article)

            if not chunks:
                print(f"Skipping {result['url']} because no chunks were generated.")
                continue

            store_chunks(
                chunks,
                metadata={
                    "title": result["title"],
                    "url": result["url"]
                }
            )

            articles.append({
                "title": result["title"],
                "url": result["url"],
                "content": article
            })
        except Exception as e:
            print(f"Error processing {result.get('url', 'unknown')}: {e}")
            continue

    return articles

def ask_question(question):
    docs = retrieve(question)

    if not docs:
        return "I couldn't find any relevant information in the knowledge base."

    context = "\n\n".join(doc.page_content for doc in docs)

    prompt = f"""
You are an AI research assistant.

Answer the user's question using ONLY the provided context.

If the answer is not available in the context, say:
"I couldn't find the answer in the available research."

Do not make up facts or use outside knowledge.

Context:
{context}

Question:
{question}

Answer:
"""

    response = llm.invoke(prompt)

    if isinstance(response.content, list):
        return "\n".join(
            block["text"]
            for block in response.content
            if isinstance(block, dict) and block.get("type") == "text"
        )

    return str(response.content)