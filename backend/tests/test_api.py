import pytest
from fastapi.testclient import TestClient
from app import app

client = TestClient(app)

def test_verify_empty():
    response = client.post("/verify", json={"article": ""})
    # Since fastAPI pydantic validation might pass but our logic handles empty string,
    # or Pydantic might reject it if it's empty string vs missing.
    # We should get a 200 with UNVERIFIED or a 422 depending on pydantic rules.
    assert response.status_code in [200, 422]

def test_verify_claim():
    # Mocking external calls is recommended for unit tests,
    # but here we just test the endpoint structure.
    response = client.post("/verify", json={"article": "The earth is flat."})
    assert response.status_code == 200
    data = response.json()
    assert "final_verdict" in data
    assert "confidence" in data
