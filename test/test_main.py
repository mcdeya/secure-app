"""
Unit tests for the secure Flask microservice.
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

class TestHealth:
    def test_returns_200_and_ok_status(self, client):
        response = client.get("/health")
        assert response.status_code == 200
        assert response.get_json() == {"status": "ok"}

class TestEcho:
    def test_echoes_valid_message(self, client):
        response = client.post("/echo", json={"message": "hello world"})
        assert response.status_code == 200
        assert response.get_json() == {"echo": "hello world"}

    def test_missing_body_returns_400(self, client):
        response = client.post("/echo", data="not json", content_type="text/plain")
        assert response.status_code == 400

    def test_missing_message_key_returns_400(self, client):
        response = client.post("/echo", json={"text": "oops"})
        assert response.status_code == 400
        assert "message" in response.get_json()["error"]

    def test_empty_message_returns_400(self, client):
        response = client.post("/echo", json={"message": "   "})
        assert response.status_code == 400

    def test_non_string_message_returns_400(self, client):
        response = client.post("/echo", json={"message": 42})
        assert response.status_code == 400

    def test_message_at_max_length_is_accepted(self, client):
        message = "x" * 280
        response = client.post("/echo", json={"message": message})
        assert response.status_code == 200
        assert response.get_json()["echo"] == message

    def test_message_exceeding_max_length_returns_400(self, client):
        message = "x" * 281
        response = client.post("/echo", json={"message": message})
        assert response.status_code == 400
        assert "280" in response.get_json()["error"]

class TestCreateItem:
    def test_creates_item_with_valid_name(self, client):
        response = client.post("/items", json={"name": "Widget-01"})
        assert response.status_code == 201
        data = response.get_json()
        assert data["name"] == "Widget-01"
        assert data["status"] == "created"

    def test_missing_name_key_returns_400(self, client):
        response = client.post("/items", json={"label": "bad"})
        assert response.status_code == 400

    def test_name_with_special_chars_returns_400(self, client):
        response = client.post("/items", json={"name": "drop table; --"})
        assert response.status_code == 400

    def test_name_too_long_returns_400(self, client):
        response = client.post("/items", json={"name": "a" * 65})
        assert response.status_code == 400

    def test_name_with_allowed_chars_accepted(self, client):
        response = client.post("/items", json={"name": "My Item_A-1"})
        assert response.status_code == 201

    def test_non_string_name_returns_400(self, client):
        response = client.post("/items", json={"name": ["list"]})
        assert response.status_code == 400


class TestErrorHandlers:
    def test_unknown_route_returns_404(self, client):
        response = client.get("/nonexistent")
        assert response.status_code == 404
        assert "error" in response.get_json()

    def test_wrong_method_returns_405(self, client):
        response = client.get("/echo") 
        assert response.status_code == 405
        assert "error" in response.get_json()
