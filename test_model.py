from utils.predictor import predict_sentiment

text = "This movie was absolutely amazing and inspiring."

sentiment, confidence = predict_sentiment(text)

print("Sentiment:", sentiment)
print("Confidence:", confidence)