from unittest.mock import patch

from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_us_chat():
    with patch(
        "app.services.legal_service.generate_ai_answer",
        return_value="General information about US immigration."
    ):
        response = client.post(
            "/api/chat",
            json={
                "question": "Explain H-1B visa basics.",
                "jurisdiction": "US",
                "category": "immigration",
                "state": "Texas",
            },
        )

    assert response.status_code == 200
    data = response.json()
    assert data["jurisdiction"] == "US"
    assert data["status"] == "ai_generated_unverified"
    assert data["sources"] == []


def test_india_chat():
    with patch(
        "app.services.legal_service.generate_ai_answer",
        return_value="General information about property law."
    ):
        response = client.post(
            "/api/chat",
            json={
                "question": "Explain property registration.",
                "jurisdiction": "IN",
                "category": "property",
                "state": "Telangana",
            },
        )

    assert response.status_code == 200
    assert response.json()["jurisdiction"] == "IN"


def test_invalid_jurisdiction():
    response = client.post(
        "/api/chat",
        json={
            "question": "Explain contract law.",
            "jurisdiction": "UK",
            "category": "contracts",
        },
    )
    assert response.status_code == 422


def test_short_question():
    response = client.post(
        "/api/chat",
        json={
            "question": "Hi",
            "jurisdiction": "US",
            "category": "civil",
        },
    )
    assert response.status_code == 422


def test_missing_api_key():
    with patch(
        "app.services.legal_service.generate_ai_answer",
        side_effect=RuntimeError("API key missing"),
    ):
        response = client.post(
            "/api/chat",
            json={
                "question": "Explain employment contracts.",
                "jurisdiction": "US",
                "category": "employment",
            },
        )

    assert response.status_code == 503