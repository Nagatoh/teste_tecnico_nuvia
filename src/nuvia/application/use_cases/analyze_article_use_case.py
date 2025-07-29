# application/use_cases/analyze_article_use_case.py
from nuvia.domain.entities.article import Article
from nuvia.application.services.bias_detection_service import BiasDetectionService

from dataclasses import dataclass
from typing import List
from nuvia.domain.entities.article import BiasSegment # Importa apenas o que precisa

@dataclass(frozen=True)
class AnalysisResult:
    """Um objeto para encapsular os resultados da análise de viés."""
    segments: List[BiasSegment]
    overall_score: float
    article_title: str
    
class AnalyzeArticleUseCase:
    def __init__(self, detector: BiasDetectionService):
        self.detector = detector

    def execute(self, article: Article) -> AnalysisResult:
        """
        Executa a análise de viés em um artigo e retorna um objeto de resultado completo.

        Args:
            article: O objeto Article a ser analisado.

        Returns:
            Um objeto AnalysisResult contendo os segmentos de viés e a pontuação geral.
        """
        # 1. Detectar os segmentos de viés no conteúdo do artigo
        segments = self.detector.detect(article.content)

        # 2. Calcular o 'Overall Bias Score' de forma mais robusta
        overall_score = 0.0
        if segments:
            # Abordagem Híbrida (Recomendada): Soma dos scores normalizada pelo tamanho do texto.
            # Isso penaliza tanto a gravidade quanto a frequência do viés.
            num_words = len(article.content.split())
            if num_words > 0:
                total_score = sum(seg.score for seg in segments)
                # Multiplicamos por 1000 para obter um score "por 1000 palavras", que é mais fácil de interpretar.
                overall_score = (total_score / num_words) * 1000

            # Se preferir a média simples (sua abordagem original corrigida):
            # total_score = sum(seg.score for seg in segments)
            # overall_score = total_score / len(segments)

        # 3. Criar e retornar um objeto de resultado imutável, sem modificar o 'article' original
        return AnalysisResult(
            segments=segments,
            overall_score=overall_score,
            article_title=article.title
        )
