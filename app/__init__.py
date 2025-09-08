# app/__init__.py
import logging
from flask import Flask
# from .routes.llm_routes import llm_bp
# from .routes.health_routes import health_bp

def create_app():
    app = Flask(__name__)
    logging.basicConfig(level=logging.INFO)

    # # register routes
    # app.register_blueprint(health_bp, url_prefix="/api")
    # app.register_blueprint(llm_bp, url_prefix="/api/llm")

    return app
