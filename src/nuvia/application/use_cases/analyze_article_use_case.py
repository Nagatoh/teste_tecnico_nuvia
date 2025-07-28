# application/use_cases/analyze_article_use_case.py
from nuvia.domain.entities.article import Article
from nuvia.application.services.bias_detection_service import BiasDetectionService

class AnalyzeArticleUseCase:
    def __init__(self, detector: BiasDetectionService):
        self.detector = detector

    def execute(self, article: Article):
        segments = self.detector.detect(article.content)
        for seg in segments:
            article.add_bias_segment(seg)
        return article
