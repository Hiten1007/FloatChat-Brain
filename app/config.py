import os
from dotenv import load_dotenv
from flask import Flask

load_dotenv()  # Load .env variables

def init_app(app: Flask):
    """
    Load all env variables into Flask's app.config
    """
    for key, value in os.environ.items():
        app.config[key] = value
