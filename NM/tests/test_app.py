import os

os.environ["DATABASE_URL"] = "sqlite:///./test_fitbuddy.db"
os.environ["GOOGLE_API_KEY"] = ""

from fastapi.testclient import TestClient

from app.database import Base, engine
from app.main import app


Base.metadata.drop_all(bind=engine)
Base.metadata.create_all(bind=engine)
client = TestClient(app)


def test_home_page_loads():
    response = client.get("/")
    assert response.status_code == 200
    assert "Build my plan" in response.text


def test_generate_and_update_flow():
    response = client.post("/api/generate-plan", json={"user_id": 7, "name": "Sam", "age": 31, "weight": 68, "goal": "general wellness", "intensity": "medium"})
    assert response.status_code == 201
    assert response.json()["user_id"] == 7
    assert "Day 1" in response.json()["workout_plan"]

    update = client.post("/api/update-plan/7", json={"user_id": 7, "feedback": "Add more mobility work."})
    assert update.status_code == 200
    assert "mobility" in update.json()["updated_plan"].lower()


def test_dashboard_and_validation():
    assert client.get("/view-all-users").status_code == 200
    invalid = client.post("/api/generate-plan", json={"user_id": 8, "name": "", "age": 10, "weight": 2, "goal": "x", "intensity": "medium"})
    assert invalid.status_code == 422
