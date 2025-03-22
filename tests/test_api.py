from fastapi.testclient import TestClient
from src.main import app

client = TestClient(app)

def test_read_root():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "Welcome to the AI Blog Summarizer API!"}

def test_summarize_endpoint():
    # This is a basic test; adjust the URL or expected output as needed.
    response = client.post("/summarize", json={"url": "https://example.com/sample-blog-post"})
    assert response.status_code == 200
    data = response.json()
    
    # Check that the response contains the expected keys
    assert "bullet_points" in data
    assert "references" in data
    assert "image_suggestion" in data