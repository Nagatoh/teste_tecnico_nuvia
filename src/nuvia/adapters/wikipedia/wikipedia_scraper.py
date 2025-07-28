# infrastructure/wikipedia/wikipedia_scraper.py
import wikipediaapi
import requests

class WikipediaScraper:
    def __init__(self, language: str = 'en'):
        # Inicializa a API com user agent apropriado
        self.wiki = wikipediaapi.Wikipedia(
            user_agent='BiasDetectorApp (your_email@example.com)',
            language=language,
            extract_format=wikipediaapi.ExtractFormat.WIKI)
        
    def fetch_article(self, title: str) -> str:
        page = self.wiki.page(title)
        if page.exists():
            return {
                "title": page.title,
                "summary": page.summary,
                "text": page.text,
                "url": page.fullurl
            }
        else:
            return None
        
    def search_articles(self,keyword, limit=5):
        """
        Usa a Wikipedia Search API via `requests` para retornar títulos relevantes.
        """
        url = "https://en.wikipedia.org/w/api.php"
        params = {
            "action": "query",
            "list": "search",
            "srsearch": keyword,
            "format": "json",
            "srlimit": limit
        }

        response = requests.get(url, params=params)
        if response.status_code == 200:
            data = response.json()
            titles = [entry["title"] for entry in data["query"]["search"]]
            return titles
        else:
            return []
