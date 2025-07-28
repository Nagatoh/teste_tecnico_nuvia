# interface/web/main.py
from fastapi import FastAPI
from pydantic import BaseModel
from domain.entities.article import Article
from nuvia.application.use_cases.analyze_article_use_case import AnalyzeArticleUseCase
from nuvia.infrastructure.nlp.spacy_bias_detector import SpacyBiasDetector

app = FastAPI()
use_case = AnalyzeArticleUseCase(SpacyBiasDetector())

class ArticleRequest(BaseModel):
    title: str
    content: str

@app.post("/analyze")
def analyze_article(request: ArticleRequest):
    article = Article(title=request.title, content=request.content)
    result = use_case.execute(article)
    return {
        "title": result.title,
        "bias_segments": [{"text": s.text, "reason": s.reason} for s in result.bias_segments]
    }
