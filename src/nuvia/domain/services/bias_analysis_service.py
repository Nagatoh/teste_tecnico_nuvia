# domain/services/biased_words_repository.py
from typing import List, Dict, Any
# Imports the INTERFACE, not the implementation
from nuvia.domain.repositories import BiasedWordsRepository

class BiasAnalysisService:
    def __init__(self, repo: BiasedWordsRepository):
        """
        The service receives a repository implementation via dependency injection.
        It doesn't know or care if the data comes from a file, database, or API.
        """
        self.repo = repo
        # We load the data once for optimization
        self.categories = self.repo.get_categories()

    def analyze_text(self, text: str) -> List[Dict[str, Any]]:
        """
        The main business logic: analyzes the text for biased words.
        """
        results = []
        words_in_text = set(text.lower().replace(',', '').replace('.', '').split())

        for category_name, category_data in self.categories.items():
            biased_words_in_category = category_data["words"]
            
            # Finds the intersection between the words in the text and the category's words
            found_words = words_in_text.intersection(biased_words_in_category)

            for word in found_words:
                results.append({
                    "word": word,
                    "category": category_name,
                    "explanation": category_data["explanation"]
                })
        
        return results