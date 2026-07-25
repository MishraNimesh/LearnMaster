from dotenv import load_dotenv
import os
from tavily import TavilyClient

load_dotenv()

client = TavilyClient(api_key=os.getenv("TAVILY_API_KEY"))

def search(query):
    response = client.search(query=query)
    return response["results"]