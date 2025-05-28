import os

class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY", "default_secret_key")
    MONGODB_SETTINGS = {
        'host': os.environ.get("MONGODB_URI", "mongodb://localhost/ladrillos_db")
    }
