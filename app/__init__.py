# app/__init__.py
import logging
from flask import Flask
from app.config import init_app
from .routes.llm_routes import llm_bp
from .routes.tools_routes import tools_bp
from app.services.vector_service import init_vector_service
# from .routes.health_routes import health_bp

def create_app():
    app = Flask(__name__)
    logging.basicConfig(level=logging.INFO)

    init_app(app)

    init_vector_service(app)

    # # register routes
    # app.register_blueprint(health_bp, url_prefix="/api")
    app.register_blueprint(llm_bp, url_prefix="/api/llm")
    app.register_blueprint(tools_bp, url_prefix="/api/tools")
    return app
