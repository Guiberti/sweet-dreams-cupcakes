import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app import create_app  # noqa: E402
from app.db import init_db  # noqa: E402


@pytest.fixture
def app(tmp_path):
    app = create_app({"TESTING": True, "DATABASE": str(tmp_path / "teste.sqlite"),
                      "UPLOAD_FOLDER": str(tmp_path), "SECRET_KEY": "teste"})
    with app.app_context():
        init_db()
    yield app


@pytest.fixture
def client(app):
    return app.test_client()


@pytest.fixture
def ctx(app):
    with app.app_context():
        yield


def login(client, email, senha):
    return client.post("/login", data={"email": email, "senha": senha})


@pytest.fixture
def cliente_logado(client):
    login(client, "cliente@teste.com", "Cliente@123")
    return client


@pytest.fixture
def admin_logado(client):
    login(client, "admin@sweetdreams.com", "Admin@123")
    return client
