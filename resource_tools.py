import requests
import xml.etree.ElementTree as ET
from tools.search_tool import search


def _tavily_resources(query, exclude_youtube=False):
    results = []
    try:
        raw_results = search(query, max_results=12)
        for item in raw_results:
            url = item.get("url", "")
            if exclude_youtube and ("youtube.com" in url.lower() or "youtu.be" in url.lower()):
                continue
            results.append({
                "title": item.get("title", "Resource"),
                "description": item.get("content", ""),
                "url": url,
                "extra": "Web Result"
            })
            if len(results) >= 8:
                break
    except Exception as e:
        print(f"Tavily search error: {e}")
    return results


def _github_resources(topic):
    try:
        response = requests.get(
            "https://api.github.com/search/repositories",
            params={"q": topic, "sort": "stars", "order": "desc", "per_page": 8},
            timeout=10,
            headers={"Accept": "application/vnd.github+json"}
        )
        response.raise_for_status()
        return [{
            "title": item["full_name"],
            "description": item.get("description") or "No description available.",
            "url": item["html_url"],
            "extra": f"★ {item['stargazers_count']} · {item.get('language') or 'Mixed languages'}"
        } for item in response.json().get("items", [])]
    except Exception as e:
        print(f"GitHub search error: {e}")
        return _tavily_resources(f"{topic} github repository site:github.com", exclude_youtube=True)


def _book_resources(topic):
    resources = []
    try:
        response = requests.get("https://openlibrary.org/search.json", params={"q": topic, "limit": 8}, timeout=10)
        if response.status_code == 200:
            for item in response.json().get("docs", []):
                if item.get("title"):
                    author = ", ".join(item.get("author_name", [])[:2]) or "Unknown author"
                    year = item.get("first_publish_year", "")
                    extra = f"Published {year}" if year else "Reference Book"
                    resources.append({
                        "title": item["title"],
                        "description": f"By {author}. Authoritative academic & reference text.",
                        "url": f"https://openlibrary.org{item.get('key', '')}",
                        "extra": extra
                    })
    except Exception as e:
        print(f"OpenLibrary error: {e}")

    if len(resources) < 4:
        tavily_books = _tavily_resources(f"{topic} textbook OR book site:openstax.org OR site:archive.org", exclude_youtube=True)
        for tb in tavily_books:
            tb["extra"] = "Open Textbook"
            resources.append(tb)

    return resources[:8]


def _arxiv_pdf_resources(topic):
    pdfs = []
    try:
        url = f"https://export.arxiv.org/api/query?search_query=all:{topic}&start=0&max_results=6"
        resp = requests.get(url, timeout=8)
        if resp.status_code == 200:
            root = ET.fromstring(resp.text)
            ns = {'atom': 'http://www.w3.org/2005/Atom'}
            for entry in root.findall('atom:entry', ns):
                title_elem = entry.find('atom:title', ns)
                summary_elem = entry.find('atom:summary', ns)
                title = title_elem.text.strip().replace('\n', ' ') if title_elem is not None else "PDF Paper"
                summary = summary_elem.text.strip().replace('\n', ' ') if summary_elem is not None else ""

                pdf_url = ""
                for link in entry.findall('atom:link', ns):
                    if link.attrib.get('title') == 'pdf' or link.attrib.get('type') == 'application/pdf':
                        pdf_url = link.attrib.get('href')
                        break
                if not pdf_url:
                    id_elem = entry.find('atom:id', ns)
                    if id_elem is not None:
                        pdf_url = id_elem.text.replace('/abs/', '/pdf/') + ".pdf"

                authors = [a.find('atom:name', ns).text for a in entry.findall('atom:author', ns) if a.find('atom:name', ns) is not None]
                author_str = ", ".join(authors[:2]) if authors else "Academic Researchers"

                if pdf_url:
                    pdfs.append({
                        "title": title,
                        "description": summary[:250] + ("..." if len(summary) > 250 else ""),
                        "url": pdf_url,
                        "extra": f"PDF Research Paper · By {author_str}"
                    })
    except Exception as e:
        print(f"ArXiv search error: {e}")
    return pdfs


def _pdf_resources(topic):
    arxiv_results = _arxiv_pdf_resources(topic)
    tavily_results = _tavily_resources(f"{topic} filetype:pdf OR site:arxiv.org OR site:openstax.org OR site:researchgate.net", exclude_youtube=True)

    pdf_tavily = []
    for item in tavily_results:
        url_lower = item["url"].lower()
        if ".pdf" in url_lower or "arxiv.org" in url_lower or "researchgate" in url_lower or "openstax" in url_lower:
            item["extra"] = "PDF Document"
            pdf_tavily.append(item)

    combined = arxiv_results + pdf_tavily
    if not combined:
        for item in tavily_results:
            item["extra"] = "Technical Guide"
            combined.append(item)

    return combined[:8]


def find_resources(topic, kind):
    try:
        k = kind.lower().strip()
        if k in ("projects", "github", "github repositories", "repo", "repos"):
            return _github_resources(topic)
        if k in ("book", "books", "books & textbooks", "book & textbooks"):
            return _book_resources(topic)
        if k in ("video", "videos", "youtube", "youtube videos"):
            return _tavily_resources(f"{topic} tutorial explanation site:youtube.com", exclude_youtube=False)
        if k in ("pdf", "pdfs", "pdf documents", "pdf document"):
            return _pdf_resources(topic)
        # Default / Web search
        return _tavily_resources(f"{topic} comprehensive guide OR tutorial", exclude_youtube=True)
    except Exception as error:
        return [{"title": f"Search fallback for {topic}", "description": str(error), "url": f"https://www.google.com/search?q={topic}", "extra": "Direct search link"}]
