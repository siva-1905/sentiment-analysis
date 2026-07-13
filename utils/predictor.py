import joblib

from utils.preprocessing import clean_text

model = joblib.load("models/sentiment_model.pkl")
vectorizer = joblib.load("models/vectorizer.pkl")


def predict_sentiment(text):

    cleaned_text = clean_text(text)

    vector = vectorizer.transform([cleaned_text])

    prediction = model.predict(vector)[0]

    probability = model.predict_proba(vector)[0]

    confidence = max(probability)

    if confidence < 0.60:
        sentiment = "Neutral"
    elif prediction == 1:
        sentiment = "Positive"
    else:
        sentiment = "Negative"

    return sentiment, round(confidence * 100, 2)