# domain/repositories/biased_words_repository.py
from abc import ABC, abstractmethod
from typing import Dict, Any

class BiasedWordsRepository(ABC):
    """
    This is the interface (contract) required by the Domain.
    Any class that wants to provide biased words to the domain
    MUST implement this interface.
    """
    @abstractmethod
    def get_categories(self) -> Dict[str, Any]:
        """
        Should return a structured dictionary with categories and their words.
        """
        pass