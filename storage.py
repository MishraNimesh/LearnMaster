import sqlite3
from datetime import datetime
from pathlib import Path

DATABASE = Path("learnmaster.db")


def _connection():
    con = sqlite3.connect(DATABASE)
    con.row_factory = sqlite3.Row
    con.execute("CREATE TABLE IF NOT EXISTS topics (topic TEXT PRIMARY KEY, introduction TEXT, difficulty TEXT, estimated_time TEXT, prerequisites TEXT)")
    con.execute("CREATE TABLE IF NOT EXISTS resources (topic TEXT, url TEXT, title TEXT, completed_at TEXT, PRIMARY KEY (topic, url))")
    con.execute("CREATE TABLE IF NOT EXISTS notes (id INTEGER PRIMARY KEY AUTOINCREMENT, topic TEXT, content TEXT, created_at TEXT)")
    con.execute("CREATE TABLE IF NOT EXISTS chapters (topic TEXT, chapter_number INTEGER, title TEXT, goal TEXT, PRIMARY KEY (topic, chapter_number))")
    con.execute("CREATE TABLE IF NOT EXISTS chapter_content (topic TEXT, title TEXT, lesson TEXT, quiz TEXT, PRIMARY KEY (topic, title))")
    con.execute("CREATE TABLE IF NOT EXISTS chapter_progress (topic TEXT, title TEXT, completed_at TEXT, PRIMARY KEY (topic, title))")
    columns = {row[1] for row in con.execute("PRAGMA table_info(chapter_content)").fetchall()}
    if "visual" not in columns:
        con.execute("ALTER TABLE chapter_content ADD COLUMN visual TEXT")
    return con


def save_topic(course):
    with _connection() as con:
        con.execute("INSERT OR REPLACE INTO topics VALUES (?, ?, ?, ?, ?)", (course["topic"], course["introduction"], course["difficulty"], course["estimated_time"], "|".join(course["prerequisites"])))


def get_topic(topic):
    with _connection() as con: row = con.execute("SELECT * FROM topics WHERE topic = ?", (topic,)).fetchone()
    if not row: return None
    return {"topic": row["topic"], "introduction": row["introduction"], "difficulty": row["difficulty"], "estimated_time": row["estimated_time"], "prerequisites": row["prerequisites"].split("|")}


def mark_resource(topic, resource):
    with _connection() as con: con.execute("INSERT OR REPLACE INTO resources VALUES (?, ?, ?, ?)", (topic, resource["url"], resource["title"], datetime.now().strftime("%d %b %Y")))


def get_completed_urls(topic):
    with _connection() as con: rows = con.execute("SELECT url FROM resources WHERE topic = ?", (topic,)).fetchall()
    return {row["url"] for row in rows}


def add_note(topic, content):
    with _connection() as con: con.execute("INSERT INTO notes (topic, content, created_at) VALUES (?, ?, ?)", (topic, content, datetime.now().strftime("%d %b %Y, %H:%M")))


def get_notes(topic):
    with _connection() as con: return con.execute("SELECT content, created_at FROM notes WHERE topic = ? ORDER BY id DESC", (topic,)).fetchall()


def save_chapters(topic, chapters):
    with _connection() as con:
        con.execute("DELETE FROM chapters WHERE topic = ?", (topic,))
        con.executemany("INSERT INTO chapters VALUES (?, ?, ?, ?)", [(topic, index + 1, chapter["title"], chapter["goal"]) for index, chapter in enumerate(chapters)])


def get_chapters(topic):
    with _connection() as con:
        rows = con.execute("SELECT title, goal FROM chapters WHERE topic = ? ORDER BY chapter_number", (topic,)).fetchall()
    return [{"title": row["title"], "goal": row["goal"]} for row in rows]


def save_chapter_content(topic, title, lesson, quiz, visual):
    import json
    with _connection() as con:
        con.execute("INSERT OR REPLACE INTO chapter_content (topic, title, lesson, quiz, visual) VALUES (?, ?, ?, ?, ?)", (topic, title, lesson, json.dumps(quiz), visual))


def get_chapter_content(topic, title):
    import json
    with _connection() as con:
        row = con.execute("SELECT lesson, quiz, visual FROM chapter_content WHERE topic = ? AND title = ?", (topic, title)).fetchone()
    if not row:
        return None
    return {"lesson": row["lesson"], "quiz": json.loads(row["quiz"]), "visual": row["visual"]}


def complete_chapter(topic, title):
    with _connection() as con:
        con.execute("INSERT OR REPLACE INTO chapter_progress VALUES (?, ?, ?)", (topic, title, datetime.now().strftime("%d %b %Y")))


def completed_chapters(topic):
    with _connection() as con:
        rows = con.execute("SELECT title FROM chapter_progress WHERE topic = ?", (topic,)).fetchall()
    return {row["title"] for row in rows}
