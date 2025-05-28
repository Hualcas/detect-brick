# config.py
import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'your_secret_key'
    MONGODB_SETTINGS = {
        'db': 'databas',
        'host': 'localhost',
        'port': 27017
    }
