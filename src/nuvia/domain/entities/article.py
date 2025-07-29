# domain/entities/article.py
from typing import List
from nuvia.domain.value_objects.bias_segment import BiasSegment

class Article:
    def __init__(self, title: str, content: str):
        self.title = title
        self.content = content
        self.bias_segments: List[BiasSegment] = []
        self.total_score = 0.0

    def add_bias_segment(self, segment: BiasSegment):
        self.bias_segments.append(segment)
