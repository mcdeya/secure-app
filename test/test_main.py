import app.main as main

def test_home():
    client = main.app.test_client()
    response = client.get("/")
    assert response.status_code == 200
    assert "Secure DevSecOps App Running" in response.get_data(as_text=True)

def test_health():
    client = main.app.test_client()
    response = client.get("/health")
    assert response.status_code == 200
    assert "healthy" in response.get_data(as_text=True)
