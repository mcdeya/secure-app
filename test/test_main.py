"""
Unit test for the secure Flask microservice.
All tests are self-contained and use Flask's built-in test client.
"""

from __future__ import annotations

import pytest
from app.main import create_app


@pytest.fixture()
def client():
    app = create_app()
    app.config["TESTING"] = True
    with app.test_client() as c:
        yield c


# -------------------------
# HEALTH CHECK TESTS
# -------------------------
class TestHealth:
    def test_health_returns_200(self, client):
        response = client.get("/health")

        assert response.status_code == 200
        assert response.is_json is True
        assert response.get_json() == {"status": "ok"}


# -------------------------
# ECHO ENDPOINT TESTS
# -------------------------
class TestEcho:

    def test_valid_echo(self, client):
        response = client.post("/echo", json={"message": "hello world"})

        assert response.status_code == 200
        assert response.get_json()["echo"] == "hello world"

    def test_missing_body_returns_400(self, client):
        response = client.post("/echo", data="invalid", content_type="text/plain")

        assert response.status_code == 400
        assert "error" in response.get_json()

    def test_missing_message_key_returns_400(self, client):
        response = client.post("/echo", json={"text": "oops"})

        assert response.status_code == 400
        assert "message" in response.get_json()["error"].lower()

    def test_empty_message_returns_400(self, client):
        response = client.post("/echo", json={"message": "   "})

        assert response.status_code == 400

    def test_non_string_message_returns_400(self, client):
        response = client.post("/echo", json={"message": 42})

        assert response.status_code == 400

    def test_max_length_boundary(self, client):
        message = "x" * 280
        response = client.post("/echo", json={"message": message})

        assert response.status_code == 200
        assert response.get_json()["echo"] == message

    def test_exceeding_max_length_returns_400(self, client):
        message = "x" * 281
        response = client.post("/echo", json={"message": message})

        assert response.status_code == 400
        assert "280" in response.get_json()["error"]


# -------------------------
# ITEM CREATION TESTS
# -------------------------
class TestCreateItem:

    def test_valid_item_creation(self, client):
        response = client.post("/items", json={"name": "Widget-01"})

        assert response.status_code == 201
        data = response.get_json()

        assert data["name"] == "Widget-01"
        assert data["status"] == "created"

    def test_missing_name_returns_400(self, client):
        response = client.post("/items", json={"label": "bad"})

        assert response.status_code == 400

    def test_sql_injection_like_input_rejected(self, client):
        response = client.post("/items", json={"name": "drop table; --"})

        assert response.status_code == 400

    def test_name_too_long_rejected(self, client):
        response = client.post("/items", json={"name": "a" * 65})

        assert response.status_code == 400

    def test_valid_characters_allowed(self, client):
        response = client.post("/items", json={"name": "My Item_A-1"})

        assert response.status_code == 201

    def test_non_string_name_rejected(self, client):
        response = client.post("/items", json={"name": ["list"]})

        assert response.status_code == 400


# -------------------------
# ERROR HANDLER TESTS
# -------------------------
class TestErrorHandlers:

    def test_404_returns_error_json(self, client):
        response = client.get("/nonexistent")

        assert response.status_code == 404
        assert "error" in response.get_json()

    def test_405_returns_error_json(self, client):
        response = client.get("/echo")

        assert response.status_code == 405
        assert "error" in response.get_json()
