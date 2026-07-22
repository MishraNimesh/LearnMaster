from pipeline import research_pipeline

user = input("Enter a research topic: ")

articles = research_pipeline(user)

for i, article in enumerate(articles, start=1):
    print(f"\nArticle {i}")
    print(f"Title : {article['title']}")
    print(f"URL   : {article['url']}")
    print("-" * 80)
    print(article["content"][:800])