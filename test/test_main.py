import pytest
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from app.main import app

@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

def test_health_check(client):
    rv = client.get('/health')
    assert rv.status_code == 200
    assert rv.get_json() == {"status": "healthy"}

def test_hello_default(client):
    rv = client.get('/hello')
    assert rv.status_code == 200
    assert rv.get_json() == {"message": "Hello, World!"}

def test_hello_name(client):
    rv = client.get('/hello?name=DevSecOps')
    assert rv.status_code == 200
    assert rv.get_json() == {"message": "Hello, DevSecOps!"}
