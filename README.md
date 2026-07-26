# StudyMate AI

A resource-first course engine. Each topic has saved chapters, source-grounded lessons, chapter quizzes, chapter-specific resources, notes, and sequential unlocks.

## Run it

1. Create a `.env` file using `.env.example` and add your Google and Tavily keys.
2. Install packages: `pip install -r requirements.txt`
3. Start the app: `streamlit run app.py`

Build course library searches for official documentation, university notes, open textbooks, and tutorials. It tags source chunks by topic, source type, quality, and chapter before saving the outline, lessons, concept maps, and five-question quizzes locally. The Course Assistant retrieves only chunks for the active chapter.
