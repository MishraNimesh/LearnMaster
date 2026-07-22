from tavily import TavilyClient
from config import TAVILY_API_KEY

client=TavilyClient(api_key=TAVILY_API_KEY)

def search(query):
     response=client.search(query=query)
     return response["results"]