from sentence_transformers import SentenceTransformer, util
from nuvia.application.services.bias_detection_service import BiasDetectionService
from nuvia.domain.value_objects.bias_segment import BiasSegment
from nltk.tokenize import sent_tokenize
from typing import List

class EmbeddingBiasDetector(BiasDetectionService):
    def __init__(self, threshold=0.6):
        self.model = SentenceTransformer("paraphrase-MiniLM-L6-v2")
        self.biased_refs = self.model.encode(biased_examples, convert_to_tensor=True)
        self.neutral_refs = self.model.encode(neutral_examples, convert_to_tensor=True)
        self._threshold = threshold
        
    @property
    def threshold(self):
        return self._threshold
        

    def detect(self, text: str) -> List[BiasSegment]:
        segments = []
        sentences = sent_tokenize(text)
        embeddings = self.model.encode(sentences, convert_to_tensor=True)

        for i, sent_vec in enumerate(embeddings):
            sim_biased = util.max_cos_sim(sent_vec, self.biased_refs).item()
            sim_neutral = util.max_cos_sim(sent_vec, self.neutral_refs).item()

            # Score é o quanto a frase se parece mais com frases opinionadas do que neutras
            bias_score = sim_biased - sim_neutral
            if bias_score > self.threshold:
                reason = f"Embedding bias score: {round(bias_score, 3)}"
                segments.append(BiasSegment(text=sentences[i], reason=reason))
        return segments
    
    
    def summarize_bias(self, segments: List[BiasSegment]) -> str:
        if not segments:
            return "O artigo parece neutro com base em análise semântica."

        total = len(segments)
        scores = [s.score for s in segments if s.score is not None]

        if not scores:
            return "Trechos enviesados foram encontrados, mas sem score confiável."

        avg_score = sum(scores) / len(scores)

        # Lógica interpretável baseada em quantidade e intensidade
        if total >= 10 and avg_score > 0.6:
            return "Artigo contém várias frases semanticamente tendenciosas com viés forte."
        elif total >= 5 and avg_score > 0.4:
            return "Artigo tem viés significativo em várias passagens."
        elif total >= 2:
            return "Artigo tem alguns traços de viés semântico."
        else:
            return "Artigo apresenta viés leve ou pontual."