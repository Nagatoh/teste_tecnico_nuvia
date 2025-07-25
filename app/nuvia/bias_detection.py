import nltk
from nltk.tokenize import sent_tokenize, word_tokenize
from nltk.corpus import opinion_lexicon, stopwords
from nltk.stem import WordNetLemmatizer
import string

nltk.download("punkt")
nltk.download("opinion_lexicon")
nltk.download("stopwords")
nltk.download("wordnet")

stop_words = set(stopwords.words("english"))
positive_words = set(opinion_lexicon.positive())
negative_words = set(opinion_lexicon.negative())
lemmatizer = WordNetLemmatizer()

def preprocess_text(text):
    sentences = sent_tokenize(text)
    return [word_tokenize(sent) for sent in sentences]

def detect_subjectivity(tokens):
    tokens_clean = [
        lemmatizer.lemmatize(word.lower())
        for word in tokens
        if word.lower() not in stop_words and word.isalpha()
    ]
    pos_count = sum(1 for w in tokens_clean if w in positive_words)
    neg_count = sum(1 for w in tokens_clean if w in negative_words)
    subj_score = (pos_count + neg_count) / (len(tokens_clean) + 1)
    return subj_score

def analyze_bias(text, threshold=0.15):
    results = []
    sentences = sent_tokenize(text)
    for sent in sentences:
        tokens = word_tokenize(sent)
        score = detect_subjectivity(tokens)
        if score > threshold:
            results.append({"sentence": sent, "bias_score": round(score, 3)})
    return results
