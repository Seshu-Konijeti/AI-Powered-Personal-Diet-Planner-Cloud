"""
Automated tests (pytest). Run from the project root with:
    pytest tests/ -v

Uses an isolated in-memory SQLite database and a temp storage bucket so
these tests never touch your real local dev data.
"""
import io
import os
import sys
import tempfile

import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

os.environ["DATABASE_URL"] = "sqlite:///:memory:"
os.environ["JWT_SECRET_KEY"] = "test-secret"
os.environ["STORAGE_BACKEND"] = "local"

from backend.app import create_app
from backend.models.models import db


@pytest.fixture()
def app():
    application = create_app()
    application.config.update(TESTING=True)
    with application.app_context():
        db.drop_all()
        db.create_all()
    yield application


@pytest.fixture()
def client(app):
    return app.test_client()


def register(client, email="alice@example.com", password="Password123"):
    return client.post("/register", json={"name": "Alice", "email": email, "password": password})


def login(client, email="alice@example.com", password="Password123"):
    return client.post("/login", json={"email": email, "password": password})


def auth_header(token):
    return {"Authorization": f"Bearer {token}"}


# ---------- Registration & Login ----------

def test_new_user_registration(client):
    resp = register(client)
    assert resp.status_code == 201
    assert resp.get_json()["user"]["email"] == "alice@example.com"


def test_existing_email_registration_rejected(client):
    register(client)
    resp = register(client)
    assert resp.status_code == 409


def test_valid_login(client):
    register(client)
    resp = login(client)
    assert resp.status_code == 200
    assert "access_token" in resp.get_json()


def test_invalid_login(client):
    register(client)
    resp = login(client, password="WrongPassword")
    assert resp.status_code == 401


def test_unauthorized_dashboard_access(client):
    resp = client.get("/profile")
    assert resp.status_code == 401


# ---------- Profile ----------

def test_profile_update(client):
    register(client)
    token = login(client).get_json()["access_token"]
    resp = client.put(
        "/profile",
        json={"dietary_preference": "vegan", "goal": "fitness", "activity_level": "active"},
        headers=auth_header(token),
    )
    assert resp.status_code == 200
    assert resp.get_json()["user"]["dietary_preference"] == "vegan"


# ---------- Diet Plan Generation ----------

def test_diet_plan_generation_vegetarian(client):
    register(client)
    token = login(client).get_json()["access_token"]
    client.put("/profile", json={"dietary_preference": "vegetarian", "goal": "balanced",
                                  "activity_level": "moderate"}, headers=auth_header(token))
    resp = client.post("/generate-plan", headers=auth_header(token))
    assert resp.status_code == 201
    plan = resp.get_json()["plan"]
    assert plan["breakfast"] and plan["lunch"] and plan["snack"] and plan["dinner"]
    assert plan["source"] in {"rule_based", "ai_api"}


def test_diet_plan_generation_vegan(client):
    register(client)
    token = login(client).get_json()["access_token"]
    resp = client.post(
        "/generate-plan",
        json={"dietary_preference": "vegan", "goal": "weight_management", "activity_level": "light"},
        headers=auth_header(token),
    )
    assert resp.status_code == 201


def test_diet_plan_generation_different_goal(client):
    register(client)
    token = login(client).get_json()["access_token"]
    resp = client.post(
        "/generate-plan",
        json={"dietary_preference": "non_vegetarian", "goal": "fitness", "activity_level": "active"},
        headers=auth_header(token),
    )
    assert resp.status_code == 201
    assert resp.get_json()["plan"]["nutrition_summary"]["goal"] == "fitness"


def test_ai_api_failure_triggers_rule_based_fallback(client, monkeypatch):
    # No AI_API_KEY set in the test environment -> engine must fall back cleanly
    monkeypatch.delenv("AI_API_KEY", raising=False)
    register(client)
    token = login(client).get_json()["access_token"]
    resp = client.post(
        "/generate-plan",
        json={"dietary_preference": "vegetarian", "goal": "balanced", "activity_level": "moderate"},
        headers=auth_header(token),
    )
    assert resp.status_code == 201
    assert resp.get_json()["plan"]["source"] == "rule_based"


# ---------- Plan persistence ----------

def test_save_and_retrieve_plan(client):
    register(client)
    token = login(client).get_json()["access_token"]
    gen = client.post(
        "/generate-plan",
        json={"dietary_preference": "vegetarian", "goal": "balanced", "activity_level": "moderate"},
        headers=auth_header(token),
    )
    plan_id = gen.get_json()["plan"]["plan_id"]

    resp = client.get(f"/plans/{plan_id}", headers=auth_header(token))
    assert resp.status_code == 200
    assert resp.get_json()["plan_id"] == plan_id

    resp_list = client.get("/plans", headers=auth_header(token))
    assert resp_list.status_code == 200
    assert len(resp_list.get_json()["plans"]) == 1


# ---------- Files (Cloud Object Storage) ----------

def test_upload_and_retrieve_file(client):
    register(client)
    token = login(client).get_json()["access_token"]

    data = {"file": (io.BytesIO(b"fake image bytes"), "meal.png")}
    resp = client.post("/upload", data=data, headers=auth_header(token), content_type="multipart/form-data")
    assert resp.status_code == 201

    resp_list = client.get("/files", headers=auth_header(token))
    assert resp_list.status_code == 200
    assert len(resp_list.get_json()["files"]) == 1


def test_invalid_file_type_rejected(client):
    register(client)
    token = login(client).get_json()["access_token"]
    data = {"file": (io.BytesIO(b"binary"), "virus.exe")}
    resp = client.post("/upload", data=data, headers=auth_header(token), content_type="multipart/form-data")
    assert resp.status_code == 400


# ---------- User isolation (security) ----------

def test_user_a_cannot_retrieve_user_b_data(client):
    register(client, email="a@example.com")
    token_a = login(client, email="a@example.com").get_json()["access_token"]
    gen = client.post(
        "/generate-plan",
        json={"dietary_preference": "vegetarian", "goal": "balanced", "activity_level": "moderate"},
        headers=auth_header(token_a),
    )
    plan_id = gen.get_json()["plan"]["plan_id"]

    register(client, email="b@example.com")
    token_b = login(client, email="b@example.com").get_json()["access_token"]

    resp = client.get(f"/plans/{plan_id}", headers=auth_header(token_b))
    assert resp.status_code == 404  # User B cannot see User A's plan


# ---------- Logout ----------

def test_logout_revokes_token(client):
    register(client)
    token = login(client).get_json()["access_token"]
    resp = client.post("/logout", headers=auth_header(token))
    assert resp.status_code == 200

    resp2 = client.get("/profile", headers=auth_header(token))
    assert resp2.status_code == 401  # token revoked, must be rejected
