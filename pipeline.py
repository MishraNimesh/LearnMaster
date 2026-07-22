from tools.search_tool import search
from tools.scraper import scrape
from utils.cleaner import clean_text


def research_pipeline(topic):
    results = search(topic)

    articles = []

    for result in results:
        try:
            article = scrape(result["url"])
            article = clean_text(article)

            articles.append({
                "title": result["title"],
                "url": result["url"],
                "content": article
            })

        except Exception:
            continue

    return articles