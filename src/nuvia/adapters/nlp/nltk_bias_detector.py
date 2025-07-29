# infrastructure/nlp/nltk_bias_detector.py
import nltk
from nltk.tokenize import sent_tokenize, word_tokenize
from nltk.corpus import opinion_lexicon, stopwords
from nltk.stem import WordNetLemmatizer
import string
from typing import List
from nuvia.application.services.bias_detection_service import BiasDetectionService
from nuvia.domain.value_objects.bias_segment import BiasSegment
nltk.download("punkt")
nltk.download("opinion_lexicon")
nltk.download("stopwords")
nltk.download("wordnet")

stop_words = set(stopwords.words("english"))
positive_words = set(opinion_lexicon.positive())
negative_words = set(opinion_lexicon.negative())
lemmatizer = WordNetLemmatizer()

class NltkBiasDetector(BiasDetectionService):
    def __init__(self,threshold=0.15):
        self._threshold = threshold

    @property
    def threshold(self):
        return self._threshold
        
    def detect(self,text):
        results = []
        sentences = sent_tokenize(text)
        for sent in sentences:
            tokens = word_tokenize(sent)
            score = self.detect_subjectivity(tokens)
            if score > self.threshold:
                results.append(BiasSegment(text=sent, score=round(score, 3)))
        return results
    
    def detect_subjectivity(self,tokens):
        tokens_clean = [
            lemmatizer.lemmatize(word.lower())
            for word in tokens
            if word.lower() not in stop_words and word.isalpha()
        ]
        pos_count = sum(1 for w in tokens_clean if w in positive_words)
        neg_count = sum(1 for w in tokens_clean if w in negative_words)
        subj_score = (pos_count + neg_count) / (len(tokens_clean) + 1)
        return subj_score

    def summarize_bias(self, segments: List[BiasSegment]) -> str:
        if not segments:
            return "Artigo parece neutro com base nos critérios de subjetividade."

        total = len(segments)
        scores = []

        for s in segments:
            # 'score' aqui é o score (float) ou string numérica
            score = float(s.score) if isinstance(s.score, (str, float, int)) else 0.0
            scores.append(score)

        avg_score = sum(scores) / total

        if total >= 10 and avg_score > 0.3:
            return "Artigo apresenta muitos trechos com forte linguagem subjetiva."
        elif total >= 5 and avg_score > 0.2:
            return "Artigo tem presença considerável de linguagem subjetiva."
        elif total >= 2:
            return "Artigo contém traços moderados de viés subjetivo."
        else:
            return "Artigo tem poucos sinais de linguagem subjetiva."
