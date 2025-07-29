from typing import List
from transformers import pipeline
from sentence_transformers import SentenceTransformer, util
from nltk.tokenize import sent_tokenize,word_tokenize

from nuvia.application.services.bias_detection_service import BiasDetectionService
from nuvia.domain.value_objects.bias_segment import BiasSegment



class HybridBiasDetector(BiasDetectionService):
    """
    Uma classe para detectar viés em texto usando uma abordagem híbrida:
    1. Um modelo de ML (BERT) para classificação de subjetividade.
    2. Léxicos para identificar "Peacock" e "Weasel words".
    """
    def __init__(self,threshold=0.4):
        """
        Inicializa o detector, carregando o modelo de ML e os léxicos.
        
        Args:
            _threshold: O limiar de confiança (entre 0 e 1) para 
                                    sinalizar uma sentença como subjetiva.
        """
        print("Initializing HybridBiasDetector...")
        try:
            print("Loading subjectivity classification model (this may take a moment)...")
            # Modelo treinado para classificar texto como SUBJETIVO ou NEUTRO
            self.subjectivity_model = pipeline(
                "text-classification",
                model="cffl/bert-base-styleclassification-subjective-neutral",
                framework="pt", # 'pt' para PyTorch
                return_all_scores=True # Garante que a saída seja consistente
            )
            print("Model loaded successfully.")
        except Exception as e:
            print(f"Error loading Hugging Face model: {e}")
            print("Please ensure 'torch' and 'transformers' are installed (`pip install torch transformers`)")
            self.subjectivity_model = None
            
        # NLTK downloads (necessário na primeira execução)
        # Listas de palavras em INGLÊS
        self.peacock_words = self._get_peacock_words()
        self.weasel_words = self._get_weasel_words()
        self._threshold = threshold
        
    @property
    def threshold(self):
        return self._threshold
        
        print("HybridBiasDetector is ready.")

    def _get_peacock_words(self) -> set:
        """Retorna um conjunto de 'Peacock terms' (termos grandiosos)."""
        return {
            "acclaimed", "award-winning", "best", "breathtaking", "classic",
            "celebrated", "critically acclaimed", "epic", "essential", "excellent",
            "extraordinary", "famous", "finest", "groundbreaking", "iconic",
            "important", "impressive", "innovative", "landmark", "legendary",
            "masterpiece", "monumental", "outstanding", "perfect", "prestigious",
            "remarkable", "revolutionary", "seminal", "significant", "stunning",
            "timeless", "unforgettable", "visionary", "world-class"
        }

    def _get_weasel_words(self) -> set:
        """Retorna um conjunto de 'Weasel words' (palavras evasivas)."""
        return {
            "allegedly", "arguably", "apparently", "can be seen as", "reportedly",
            "could", "debatably", "effective", "efficiently", "reportedly",
            "in some respects", "is considered", "is seen as", "it is said",
            "it seems", "it appears", "many", "may", "might", "often", "perhaps",
            "possibly", "reportedly", "seems", "some", "sometimes", "suggests"
        }

    def detect(self, text: str) -> List[BiasSegment]:
        """
        Analisa o texto para detectar diferentes tipos de viés.
        """
        if self.subjectivity_model is None:
            print("Detector is not available due to a model loading error.")
            return []

        segments = []
        sentences = sent_tokenize(text, language='english')

        for sent in sentences:
            # Etapa 1: Detecção com Modelo de Machine Learning
            try:
                model_output = self.subjectivity_model(sent)
                if model_output and model_output[0]:
                    subjectivity_dict = model_output[0][0] # Extrai o dicionário correto
                    
                    is_subjective = subjectivity_dict["label"] == "SUBJECTIVE"
                    is_above_threshold = subjectivity_dict["score"] > self._threshold

                    if is_subjective and is_above_threshold:
                        score = round(subjectivity_dict['score'], 2)
                        reason = f"Subjective Language (Model Confidence: {score})"
                        segments.append(BiasSegment(text=sent, reason=reason, score=score))
                        continue
            except Exception as e:
                print(f"Error processing sentence with ML model: {sent}\nError: {e}")

            # Etapa 2: Detecção com Léxicos
            tokens = {word.lower() for word in word_tokenize(sent, language='english')}

            found_peacock_words = tokens.intersection(self.peacock_words)
            if found_peacock_words:
                word = found_peacock_words.pop()
                reason = f"Use of 'Peacock Term': '{word}'"
                segments.append(BiasSegment(text=sent, reason=reason, score=0.75))
                continue

            found_weasel_words = tokens.intersection(self.weasel_words)
            if found_weasel_words:
                word = found_weasel_words.pop()
                reason = f"Use of 'Weasel Word': '{word}'"
                segments.append(BiasSegment(text=sent, reason=reason, score=0.70))
                continue
                
        return segments

    def summarize_bias(self, segments: List[BiasSegment]) -> str:
        """
        Resume os achados de viés em uma string interpretável.
        """
        if not segments:
            return "Based on the criteria, the article appears to be neutral."

        total = len(segments)
        scores = [s.score for s in segments]
        avg_score = sum(scores) / total if total > 0 else 0

        if total >= 10 and avg_score > 0.3:
            return "The article shows many passages with strong subjective language."
        elif total >= 5 and avg_score > 0.2:
            return "The article has a considerable presence of subjective language."
        elif total >= 2:
            return "The article contains moderate traces of subjective bias."
        else:
            return "The article has few signs of subjective language."
