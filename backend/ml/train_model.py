"""Train the sentiment model once and save it.

Usage (from the backend folder):
    python ml/train_model.py
    python ml/train_model.py "path/to/IMDB Dataset.csv"

Default dataset location: backend/ml/IMDB Dataset.csv
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import joblib
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, confusion_matrix, precision_recall_fscore_support
from sklearn.model_selection import train_test_split

from ml.preprocess import clean_text

ML_DIR = os.path.dirname(os.path.abspath(__file__))
MODEL_DIR = os.path.join(ML_DIR, "models")


def main():
    dataset = sys.argv[1] if len(sys.argv) > 1 else os.path.join(ML_DIR, "IMDB Dataset.csv")
    if not os.path.exists(dataset):
        sys.exit(f"Dataset not found: {dataset}\nDownload 'IMDB Dataset.csv' and put it in backend/ml/")

    df = pd.read_csv(dataset)
    if not {"review", "sentiment"}.issubset(df.columns):
        sys.exit("Dataset must contain the columns: review, sentiment")
    df = df.dropna(subset=["review", "sentiment"])
    print(f"Loaded {len(df)} reviews")

    print("Cleaning text (this takes a few minutes)...")
    df["clean"] = df["review"].apply(clean_text)
    y = (df["sentiment"].str.lower() == "positive").astype(int)  # 1 = Positive, 0 = Negative

    X_train, X_test, y_train, y_test = train_test_split(
        df["clean"], y, test_size=0.2, random_state=42, stratify=y
    )

    vectorizer = TfidfVectorizer(max_features=30000, ngram_range=(1, 2))
    X_train_vec = vectorizer.fit_transform(X_train)
    X_test_vec = vectorizer.transform(X_test)

    model = LogisticRegression(max_iter=1000)
    model.fit(X_train_vec, y_train)

    pred = model.predict(X_test_vec)
    precision, recall, f1, _ = precision_recall_fscore_support(y_test, pred, average="binary")
    print("\n===== Evaluation on 20% test set =====")
    print(f"Accuracy : {accuracy_score(y_test, pred):.4f}")
    print(f"Precision: {precision:.4f}")
    print(f"Recall   : {recall:.4f}")
    print(f"F1-score : {f1:.4f}")
    print("Confusion matrix (rows = actual, cols = predicted; order: negative, positive):")
    print(confusion_matrix(y_test, pred))

    os.makedirs(MODEL_DIR, exist_ok=True)
    joblib.dump(model, os.path.join(MODEL_DIR, "sentiment_model.pkl"))
    joblib.dump(vectorizer, os.path.join(MODEL_DIR, "vectorizer.pkl"))
    print(f"\nSaved model + vectorizer to {MODEL_DIR}")


if __name__ == "__main__":
    main()
