import os

import joblib

from ml.preprocess import clean_text

MODEL_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "ml", "models")
MODEL_PATH = os.path.join(MODEL_DIR, "sentiment_model.pkl")
VECTORIZER_PATH = os.path.join(MODEL_DIR, "vectorizer.pkl")
NEUTRAL_THRESHOLD = 0.60

_model = None
_vectorizer = None


class ModelNotFoundError(RuntimeError):
    pass


def _load():
    """Load the saved model once (lazy). The app never trains the model."""
    global _model, _vectorizer
    if _model is None:
        if not (os.path.exists(MODEL_PATH) and os.path.exists(VECTORIZER_PATH)):
            raise ModelNotFoundError("Model files not found. Run 'python ml/train_model.py' first.")
        _model = joblib.load(MODEL_PATH)
        _vectorizer = joblib.load(VECTORIZER_PATH)


def predict_sentiment(text):
    _load()
    features = _vectorizer.transform([clean_text(text)])
    prediction = int(_model.predict(features)[0])
    confidence = float(_model.predict_proba(features)[0].max())
    if confidence < NEUTRAL_THRESHOLD:
        sentiment = "Neutral"
    else:
        sentiment = "Positive" if prediction == 1 else "Negative"
    return {"sentiment": sentiment, "confidence": round(confidence * 100, 2)}
