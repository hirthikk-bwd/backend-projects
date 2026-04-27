import pytest
from app import create_app, db


@pytest.fixture
def client():
    app = create_app({
        "TESTING": True,
        "SQLALCHEMY_DATABASE_URI": "sqlite:///:memory:",
        "JWT_SECRET_KEY": "test-secret"
    })
    with app.app_context():
        db.create_all()
        yield app.test_client()
        db.drop_all()


def get_token(client):
    client.post("/auth/register", json={
        "email": "test@example.com",
        "password": "password123"
    })
    response = client.post("/auth/login", json={
        "email": "test@example.com",
        "password": "password123"
    })
    return response.get_json()["token"]


def test_create_job(client):
    token = get_token(client)
    response = client.post("/jobs/", json={
        "company": "Google",
        "role": "Backend Engineer",
        "status": "applied"
    }, headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 201
    assert response.get_json()["message"] == "Job added"


def test_get_jobs(client):
    token = get_token(client)
    client.post("/jobs/", json={
        "company": "Google",
        "role": "Backend Engineer",
        "status": "applied"
    }, headers={"Authorization": f"Bearer {token}"})
    response = client.get("/jobs/", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200
    assert len(response.get_json()) == 1


def test_get_jobs_no_token(client):
    response = client.get("/jobs/")
    assert response.status_code == 401


def test_jobs_isolated_per_user(client):
    # User 1
    client.post("/auth/register", json={"email": "user1@example.com", "password": "pass123"})
    r1 = client.post("/auth/login", json={"email": "user1@example.com", "password": "pass123"})
    token1 = r1.get_json()["token"]

    # User 2
    client.post("/auth/register", json={"email": "user2@example.com", "password": "pass123"})
    r2 = client.post("/auth/login", json={"email": "user2@example.com", "password": "pass123"})
    token2 = r2.get_json()["token"]

    # User 1 adds a job
    client.post("/jobs/", json={"company": "Zoho", "role": "SDE", "status": "applied"},
                headers={"Authorization": f"Bearer {token1}"})

    # User 2 should see 0 jobs
    response = client.get("/jobs/", headers={"Authorization": f"Bearer {token2}"})
    assert response.status_code == 200
    assert len(response.get_json()) == 0
