import re

import nltk
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer

_stop_words = None
_lemmatizer = None


def _has_resource(*paths):
    for p in paths:
        try:
            nltk.data.find(p)
            return True
        except LookupError:
            continue
    return False


def _init():
    """Load NLTK resources once (downloads them if missing)."""
    global _stop_words, _lemmatizer
    if _stop_words is not None:
        return
    if not _has_resource("corpora/stopwords", "corpora/stopwords.zip"):
        nltk.download("stopwords", quiet=True)
    if not _has_resource("corpora/wordnet", "corpora/wordnet.zip"):
        nltk.download("wordnet", quiet=True)
    _stop_words = set(stopwords.words("english"))
    _lemmatizer = WordNetLemmatizer()


def clean_text(text):
    """lowercase -> remove HTML -> keep letters -> tokenize -> remove stopwords -> lemmatize -> join"""
    _init()
    text = str(text).lower()
    text = re.sub(r"<[^>]+>", " ", text)
    text = re.sub(r"[^a-z\s]", " ", text)
    tokens = text.split()
    tokens = [_lemmatizer.lemmatize(t) for t in tokens if t not in _stop_words]
    return " ".join(tokens)
