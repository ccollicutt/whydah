from flask import Flask
from .routes import config_bp
from .config import GIT_REPO_URL, GIT_TOKEN
from .config_manager import ConfigManager
from .logging_config import setup_logging


def create_app():
    """
    Create a Flask app and register the config blueprint
    """

    if not GIT_REPO_URL:
        raise ValueError("GIT_REPO_URL environment variable is not set")

    app = Flask(__name__)

    config_manager = ConfigManager(GIT_REPO_URL, GIT_TOKEN)
    app.register_blueprint(config_bp(config_manager))

    # Set up logging
    setup_logging()

    return app


if __name__ == "__main__":
    app = create_app()
    app.run()
