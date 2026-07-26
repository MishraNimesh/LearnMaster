# StudyMate AI

StudyMate AI is an AI-powered learning platform that transforms any topic into a structured learning experience using Retrieval-Augmented Generation (RAG).

Instead of relying only on a language model's internal knowledge, StudyMate AI discovers relevant learning resources, builds a searchable knowledge base, and generates grounded explanations from the retrieved content. The goal is to make learning more structured, reliable, and resource-driven.

---

## Features

- Generate structured learning content for any topic
- Build a searchable knowledge base from web resources
- Retrieval-Augmented Generation (RAG) for grounded question answering
- Source-grounded introductions and detailed topic explanations
- AI-generated study plans
- Discover learning resources including GitHub repositories, books, PDFs, and videos
- Local vector search using ChromaDB
- SQLite-based storage for topics, chapters, notes, and progress
- Automatic Gemini model fallback for improved reliability
- Response caching to reduce API usage

---

## How It Works

```
                User Topic
                     │
                     ▼
              Web Search (Tavily)
                     │
                     ▼
               Content Scraping
                     │
                     ▼
            Cleaning & Chunking
                     │
                     ▼
          Gemini Embedding Model
                     │
                     ▼
                 ChromaDB
                     │
          ┌──────────┴──────────┐
          │                     │
          ▼                     ▼
     Context Retrieval    Resource Discovery
          │
          ▼
      Gemini 3.5 Flash
          │
          ▼
   Grounded AI Responses
```

---

## Tech Stack

**Language**

- Python

**Backend**

- Python HTTP Server

**AI**

- Google Gemini
- Gemini Embeddings
- LangChain

**Vector Database**

- ChromaDB

**Database**

- SQLite

**Search & Scraping**

- Tavily API
- BeautifulSoup
- Requests

---

## Installation

Clone the repository

```bash
git clone https://github.com/MishraNimesh/studymate.git
cd studymate
```

Install dependencies

```bash
pip install -r requirements.txt
```

Create a `.env` file

```env
GOOGLE_API_KEY=your_google_api_key
TAVILY_API_KEY=your_tavily_api_key
```

Run the application

```bash
python server.py
```

The server will start on:

```
http://localhost:5000
```

---

## Project Structure

```
StudyMateAI/
│
├── server.py
├── pipeline.py
├── llm.py
├── storage.py
├── resource_tools.py
├── requirements.txt
│
├── vectorstore/
│   ├── chroma_db.py
│   ├── embeddings.py
│   └── retriever.py
│
├── tools/
│   ├── search_tool.py
│   └── scraper.py
│
├── utils/
│   ├── cleaner.py
│   └── chunker.py
│
└── static/
```

---

## Future Improvements

- Flashcards with spaced repetition
- User authentication
- Course analytics
- Source citations for generated responses
- Interactive quizzes
- Frontend enhancements

---

## Why I Built This

When learning a new technology, I often found myself switching between documentation, tutorials, YouTube videos, GitHub repositories, and books. StudyMate AI was built to bring these resources together into a single learning workflow. By combining web search, vector retrieval, and large language models, the platform generates structured, source-grounded explanations instead of relying solely on an LLM's internal knowledge.

---

## Demo

https://github.com/user-attachments/assets/YOUR_VIDEO_ASSET_ID

*(To show the video player on GitHub, drag & drop `Screen Recording 2026-07-26 211757.mp4` into the GitHub web editor for README.md to get your exact CDN link)*

---

## License

This project is licensed under the MIT License.
