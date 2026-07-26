import os

from dotenv import load_dotenv
from tavily import TavilyClient

load_dotenv()


def search(query, max_results=15):
    client = TavilyClient(api_key=os.getenv("TAVILY_API_KEY"))
    return client.search(query=query, max_results=max_results)["results"]
