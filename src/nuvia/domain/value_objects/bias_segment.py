# domain/value_objects/bias_segment.py
class BiasSegment:
    def __init__(self, text: str,reason: str, score: float = None, ):
        self.text = text
        self.score = score
        self.reason = reason
