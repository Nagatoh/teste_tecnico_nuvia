# application/services/bias_detection_service.py
from abc import ABC, abstractmethod
from typing import List
from nuvia.domain.value_objects.bias_segment import BiasSegment

class BiasDetectionService(ABC):
    @property
    @abstractmethod
    def threshold(self) -> float:
        pass

    @abstractmethod
    def detect(self, text: str) -> List[BiasSegment]:
        """
        Detects bias in the given text and returns a list of BiasSegment objects.
        :param text: The text to analyze.
        :return: A list of BiasSegment objects containing biased segments and their reasons.
        """
        pass
    
    @abstractmethod
    def summarize_bias(self, text: str) -> str:
        """
        Summarizes the bias in the given text.
        
        :param text: The text to analyze.
        :return: A summary of the bias detected in the text.
        """
        pass
