# P3 — Job Tracker API

A RESTful Job Application Tracker API built with Flask, PostgreSQL, JWT authentication, and Docker.

## Stack

![Python](https://img.shields.io/badge/Python-3.11-blue)
![Flask](https://img.shields.io/badge/Flask-3.0.0-lightgrey)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-15-blue)
![Docker](https://img.shields.io/badge/Docker-compose-blue)
![pytest](https://img.shields.io/badge/pytest-8%20passing-green)

## Features

- JWT authentication — register, login, protected routes
- Full CRUD for job applications (create, read, update, delete)
- User isolation — every user only sees their own jobs
- bcrypt password hashing
- Flask app factory pattern with Blueprints
- Fully containerised with Docker + docker-compose
- 8 passing pytest tests using SQLite in-memory DB

## Project Structure

```
job-tracker-api/
├── app/
│   ├── __init__.py        # create_app() — app factory pattern
│   ├── config.py          # environment config
│   ├── models.py          # User + JobApplication SQLAlchemy models
│   ├── auth/
│   │   ├── __init__.py    # auth blueprint
│   │   └── routes.py      # /register, /login
│   └── jobs/
│       ├── __init__.py    # jobs blueprint
│       └── routes.py      # CRUD endpoints
├── tests/
│   ├── test_auth.py       # 4 auth tests
│   └── test_jobs.py       # 4 jobs tests
├── .env
├── requirements.txt
├── Dockerfile
└── docker-compose.yml
```

## API Endpoints

| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| POST | `/auth/register` | No | Register a new user |
| POST | `/auth/login` | No | Login and get JWT token |
| GET | `/jobs/` | JWT | List all jobs for current user |
| POST | `/jobs/` | JWT | Create a new job application |
| PUT | `/jobs/:id` | JWT | Update a job application |
| DELETE | `/jobs/:id` | JWT | Delete a job application |

## How JWT Works

```
POST /auth/login
→ bcrypt verifies password
→ server signs a JWT token (header.payload.signature)
→ token returned to client

GET /jobs/  (with Authorization: Bearer <token>)
→ @jwt_required() verifies signature
→ user_id extracted from payload
→ only that user's jobs returned
```

## Running Locally

```bash
# Clone the repo
git clone https://github.com/hirthikk-bwd/backend-projects
cd backend-projects/job-tracker-api

# Start containers
docker-compose up --build

# Run tests
docker-compose exec web python -m pytest tests/ -v
```

## Test Results

```
tests/test_auth.py::test_register_success         PASSED
tests/test_auth.py::test_register_duplicate_email PASSED
tests/test_auth.py::test_login_success            PASSED
tests/test_auth.py::test_login_wrong_password     PASSED
tests/test_jobs.py::test_create_job               PASSED
tests/test_jobs.py::test_get_jobs                 PASSED
tests/test_jobs.py::test_get_jobs_no_token        PASSED
tests/test_jobs.py::test_jobs_isolated_per_user   PASSED

8 passed in 3.27s
```

## Concepts Learned

- Flask app factory pattern (`create_app()`)
- Flask Blueprints for route separation
- SQLAlchemy ORM — models, relationships, sessions
- JWT auth flow — signing, verifying, extracting identity
- bcrypt — password hashing with salt rounds
- Docker + docker-compose for multi-container apps
- Flask-Migrate for database migrations
- HTTP 401 vs 403 vs 409 status codes
- pytest fixtures with SQLite in-memory DB

---

Part of my [Backend Engineering Portfolio](https://github.com/hirthikk-bwd/backend-projects) — building production-grade backend systems from scratch.
