"""
Module 1 Tests — Auth & Dataset endpoints
Run: pytest tests/ -v
"""
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.main import app
from app.database.connection import Base, get_db

# ─── In-memory SQLite for testing ─────────────────────────────────────────────
TEST_DATABASE_URL = "sqlite:///./test.db"

engine = create_engine(TEST_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db


@pytest.fixture(scope="module", autouse=True)
def setup_db():
    """Create tables before tests, drop after"""
    from app.auth.models import User, RefreshToken
    from app.datasets.models import Dataset, DatasetVersion
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="module")
def client():
    return TestClient(app)


@pytest.fixture(scope="module")
def auth_tokens(client):
    """Register + login and return tokens"""
    # Register
    client.post("/api/v1/auth/register", json={
        "full_name": "Test User",
        "email": "testuser@automl.com",
        "password": "TestPass123!",
    })
    # Login
    resp = client.post("/api/v1/auth/login", json={
        "email": "testuser@automl.com",
        "password": "TestPass123!",
    })
    return resp.json()


# ─── Auth Tests ───────────────────────────────────────────────────────────────

class TestAuthRegister:
    def test_register_success(self, client):
        resp = client.post("/api/v1/auth/register", json={
            "full_name": "New User",
            "email": "newuser@automl.com",
            "password": "NewPass123!",
        })
        assert resp.status_code == 201
        data = resp.json()
        assert data["email"] == "newuser@automl.com"
        assert "hashed_password" not in data

    def test_register_duplicate_email(self, client):
        payload = {"full_name": "Dup", "email": "dup@automl.com", "password": "DupPass123!"}
        client.post("/api/v1/auth/register", json=payload)
        resp = client.post("/api/v1/auth/register", json=payload)
        assert resp.status_code == 409

    def test_register_weak_password(self, client):
        resp = client.post("/api/v1/auth/register", json={
            "full_name": "Weak",
            "email": "weak@automl.com",
            "password": "weakpass",
        })
        assert resp.status_code == 422

    def test_register_invalid_email(self, client):
        resp = client.post("/api/v1/auth/register", json={
            "full_name": "Bad Email",
            "email": "notanemail",
            "password": "StrongPass123!",
        })
        assert resp.status_code == 422


class TestAuthLogin:
    def test_login_success(self, client):
        client.post("/api/v1/auth/register", json={
            "full_name": "Login User",
            "email": "login@automl.com",
            "password": "LoginPass123!",
        })
        resp = client.post("/api/v1/auth/login", json={
            "email": "login@automl.com",
            "password": "LoginPass123!",
        })
        assert resp.status_code == 200
        data = resp.json()
        assert "access_token" in data
        assert "refresh_token" in data
        assert data["token_type"] == "bearer"

    def test_login_wrong_password(self, client):
        resp = client.post("/api/v1/auth/login", json={
            "email": "login@automl.com",
            "password": "WrongPass999!",
        })
        assert resp.status_code == 401

    def test_login_nonexistent_user(self, client):
        resp = client.post("/api/v1/auth/login", json={
            "email": "nobody@automl.com",
            "password": "SomePass123!",
        })
        assert resp.status_code == 401


class TestAuthMe:
    def test_get_me_success(self, client, auth_tokens):
        headers = {"Authorization": f"Bearer {auth_tokens['access_token']}"}
        resp = client.get("/api/v1/auth/me", headers=headers)
        assert resp.status_code == 200
        assert resp.json()["email"] == "testuser@automl.com"

    def test_get_me_no_token(self, client):
        resp = client.get("/api/v1/auth/me")
        assert resp.status_code == 403

    def test_get_me_invalid_token(self, client):
        headers = {"Authorization": "Bearer invalid.token.here"}
        resp = client.get("/api/v1/auth/me", headers=headers)
        assert resp.status_code == 401


class TestRefreshToken:
    def test_refresh_success(self, client, auth_tokens):
        resp = client.post("/api/v1/auth/refresh", json={
            "refresh_token": auth_tokens["refresh_token"]
        })
        assert resp.status_code == 200
        assert "access_token" in resp.json()

    def test_refresh_invalid_token(self, client):
        resp = client.post("/api/v1/auth/refresh", json={"refresh_token": "bad-token"})
        assert resp.status_code == 401


# ─── Dashboard Tests ──────────────────────────────────────────────────────────

class TestDashboard:
    def test_dashboard_stats(self, client, auth_tokens):
        headers = {"Authorization": f"Bearer {auth_tokens['access_token']}"}
        resp = client.get("/api/v1/dashboard/stats", headers=headers)
        assert resp.status_code == 200
        data = resp.json()
        assert "total_datasets" in data
        assert "total_storage_bytes" in data
        assert "recent_datasets" in data


# ─── Health Tests ─────────────────────────────────────────────────────────────

class TestHealth:
    def test_root(self, client):
        resp = client.get("/")
        assert resp.status_code == 200
        assert resp.json()["status"] == "running"

    def test_health(self, client):
        resp = client.get("/health")
        assert resp.status_code == 200
