import requests
from bs4 import BeautifulSoup


def scrape(url):
    headers = {
    "User-Agent": "Mozilla/5.0"
}
    
    response = requests.get(url, headers=headers, timeout=10)
    response.raise_for_status()

    soup = BeautifulSoup(response.text, "html.parser")

    text = soup.get_text(separator="\n")

    return text