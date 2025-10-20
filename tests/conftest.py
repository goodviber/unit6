import os
import importlib
import pytest

@pytest.fixture(scope="session")
def app():
    # Ensure Flask runs in testing mode
    os.environ["FLASK_ENV"] = "testing"
    os.environ["FLASK_DEBUG"] = "0"

    # Import the Flask app object from app.py
    mod = importlib.import_module("app")
    flask_app = getattr(mod, "app")
    
    assert flask_app is not None, "Could not find Flask app in app.py"
    flask_app.config.update(TESTING=True, WTF_CSRF_ENABLED=False)
    return flask_app

@pytest.fixture()
def client(app):
    return app.test_client()

@pytest.fixture()
def runner(app):
    return app.test_cli_runner()
