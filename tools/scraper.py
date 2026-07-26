import requests
from bs4 import BeautifulSoup


HEADERS = {"User-Agent": "Mozilla/5.0", "Accept-Language": "en-US,en;q=0.9"}


def scrape(url):
    response = requests.get(url, headers=HEADERS, timeout=10)
    response.raise_for_status()
    soup = BeautifulSoup(response.text, "html.parser")
    content = soup.find("article") or soup.find("main") or soup.find("body") or soup
    return content.get_text(separator="\n", strip=True)
