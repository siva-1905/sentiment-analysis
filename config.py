import os

class Config:
    SECRET_KEY = "sentiment_analysis_secret_key"

    SQLALCHEMY_DATABASE_URI = "sqlite:///sentiment.db"

    SQLALCHEMY_TRACK_MODIFICATIONS = False