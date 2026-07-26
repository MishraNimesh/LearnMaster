from tools.search_tool import search
from tools.scraper import scrape
from utils.cleaner import clean_text
from utils.chunker import chunk_text
from vectorstore.chroma_db import store_chunks
from vectorstore.retriever import retrieve
from llm import llm


def source_details(url):
    url = url.lower()
    if ".edu" in url or "ocw." in url:
        return "university_notes", "University source"
    if "docs." in url or "developer." in url or "documentation" in url:
        return "official_documentation", "Official documentation"
    if "openstax" in url or "archive.org" in url:
        return "open_textbook", "Open textbook"
    return "article", "Web article"


_qa_cache = {}


def research_pipeline(topic):
    queries = [
        f"{topic} official documentation",
        f"{topic} university course notes",
        f"{topic} open textbook",
        f"{topic} tutorial guide",
    ]
    results = []
    seen_urls = set()
    for query in queries:
        for result in search(query, max_results=3):
            if result["url"] not in seen_urls:
                results.append(result)
                seen_urls.add(result["url"])
    articles = []
    target_articles = 4

    for result in results:
        if len(articles) >= target_articles:
            break
        try:
            if "youtube.com" in result["url"] or "youtu.be" in result["url"]:
                continue

            article = clean_text(scrape(result["url"]))
            chunks = chunk_text(article)
            if not chunks:
                continue

            resource_type, source_quality = source_details(result["url"])
            store_chunks(chunks, {"title": result["title"], "url": result["url"], "topic": topic, "resource_type": resource_type, "source_quality": source_quality})
            articles.append({"title": result["title"], "url": result["url"], "resource_type": resource_type})
        except Exception as error:
            print(f"Skipping {result['url']}: {error}")
    return articles


def retrieve_topic_context(topic, max_results=5):
    context_parts = []
    try:
        docs = retrieve(topic, topic)
        if docs:
            context_parts.append("Saved Resources Context:\n" + "\n".join(doc.page_content[:500] for doc in docs[:4]))
    except Exception as e:
        print(f"Vector store retrieve failed: {e}")

    try:
        search_results = search(f"{topic} core concepts architecture tutorial guide documentation", max_results=max_results)
        if search_results:
            snippets = [f"- {r.get('title', '')}: {r.get('content', r.get('snippet', ''))}" for r in search_results if r.get('content') or r.get('snippet')]
            if snippets:
                context_parts.append("Live Web Search Retrieved Snippets:\n" + "\n".join(snippets))
    except Exception as e:
        print(f"Live web search failed: {e}")

    return "\n\n".join(context_parts) if context_parts else f"Topic study reference: {topic}"


def generate_source_grounded_intro(topic):
    context = retrieve_topic_context(topic, max_results=4)
    prompt = (
        f"You are an expert AI study tutor.\n"
        f"Provide a brief, engaging 2-3 paragraph introduction to studying '{topic}'.\n\n"
        f"CRITICAL REQUIREMENT: Synthesize and ground this introduction in the following retrieved sources and search snippets:\n\n"
        f"--- RETRIEVED SOURCES CONTEXT ---\n"
        f"{context}\n"
        f"--- END CONTEXT ---\n\n"
        f"Explain what '{topic}' is, its core fundamentals, and key goals for a student based on these retrieved sources. Use clean markdown formatting."
    )
    res = llm.invoke(prompt)
    intro_text = res.content if hasattr(res, "content") else str(res)
    if isinstance(intro_text, list):
        intro_text = "\n".join(b.get("text", "") for b in intro_text if isinstance(b, dict))
    return str(intro_text)


def generate_source_grounded_detailed(topic):
    context = retrieve_topic_context(topic, max_results=5)
    prompt = (
        f"You are an expert AI study tutor.\n"
        f"Write a comprehensive, step-by-step detailed breakdown of '{topic}'.\n\n"
        f"CRITICAL REQUIREMENT: Summarize and synthesize the following retrieved document chunks and web snippets to construct this detailed explanation:\n\n"
        f"--- RETRIEVED CHUNKS & SOURCES ---\n"
        f"{context}\n"
        f"--- END RETRIEVED CHUNKS ---\n\n"
        f"Structure the explanation with clear markdown headings:\n"
        f"1. Core Architecture & High-Level Concept\n"
        f"2. Step-by-Step Fundamentals\n"
        f"3. Key Principles & Best Practices\n"
        f"4. Real-World Applications and Examples"
    )
    res = llm.invoke(prompt)
    content = res.content if hasattr(res, "content") else str(res)
    if isinstance(content, list):
        content = "\n".join(b.get("text", "") for b in content if isinstance(b, dict))
    return str(content)


def ask_question(question, topic=None, chapter=None):
    cache_key = (question.strip().lower(), topic, chapter)
    if cache_key in _qa_cache:
        return _qa_cache[cache_key]

    docs = retrieve(question, topic, chapter)
    resource_context = "\n\n".join(doc.page_content[:600] for doc in docs) if docs else ""

    search_context = ""
    try:
        search_query = f"{topic} {question}".strip() if topic else question
        search_results = search(search_query, max_results=3)
        if search_results:
            snippets = [f"- {r.get('title', '')}: {r.get('content', r.get('snippet', ''))}" for r in search_results]
            search_context = "\n".join(snippets[:3])
    except Exception as e:
        print(f"Web search skipped/failed: {e}")

    prompt_parts = [
        "You are an expert AI study tutor.",
        "Answer the user's question clearly, thoroughly, and accurately.",
        "Combine information from saved study resources, live web search results, and your general AI knowledge to provide a comprehensive response."
    ]
    if topic:
        prompt_parts.append(f"Topic: {topic}")
    if resource_context:
        prompt_parts.append(f"Saved Study Resources Context:\n{resource_context}")
    if search_context:
        prompt_parts.append(f"Live Web Search Context:\n{search_context}")
    prompt_parts.append(f"User Question: {question}")

    prompt = "\n\n".join(prompt_parts)

    response = llm.invoke(prompt)
    if hasattr(response, "content"):
        answer = response.content
        if isinstance(answer, list):
            answer = "\n".join(block["text"] for block in answer if isinstance(block, dict) and block.get("type") == "text")
        else:
            answer = str(answer)
    else:
        answer = str(response)

    _qa_cache[cache_key] = answer
    return answer
