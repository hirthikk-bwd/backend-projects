# P2 — URL Shortener API

A production-ready URL Shortener API built with Flask, PostgreSQL, Redis, and Docker.

## Stack

![Python](https://img.shields.io/badge/Python-3.11-blue)
![Flask](https://img.shields.io/badge/Flask-3.0.0-lightgrey)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-15-blue)
![Redis](https://img.shields.io/badge/Redis-7-red)
![Docker](https://img.shields.io/badge/Docker-compose-blue)

## Features

- Shorten any long URL to a 6-character Base62 code
- Redirect short URLs to original with HTTP 302
- Click analytics — track how many times each link was visited
- Redis caching — redirects served from memory, not database
- Fully containerised with Docker + docker-compose

## Project Structure

```
url-shortener/
├── app/
│   ├── __init__.py        # create_app() — app factory pattern
│   ├── config.py          # environment config
│   ├── models.py          # URL SQLAlchemy model
│   ├── shortener.py       # Base62 encoding logic
│   ├── cache.py           # Redis GET/SET with TTL
│   └── routes.py          # API endpoints
├── tests/
│   └── test_shortener.py
├── .env
├── requirements.txt
├── Dockerfile
└── docker-compose.yml
```

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/shorten` | Submit a long URL, get a short code back |
| GET | `/:code` | Redirect to the original URL |
| GET | `/stats/:code` | Get click count for a short URL |

## How It Works

```
POST /shorten  { "url": "https://example.com/very/long/path" }
→ generates Base62 short code (e.g. "aB3xYz")
→ stores in PostgreSQL
→ caches in Redis with TTL

GET /aB3xYz
→ check Redis first (fast path)
→ if miss, query PostgreSQL
→ HTTP 302 redirect to original URL
→ increment click counter
```

## Running Locally

```bash
git clone https://github.com/hirthikk-bwd/backend-projects
cd backend-projects/url-shortener
docker-compose up --build
```

## Concepts Learned

- Flask app factory pattern
- Base62 encoding for short code generation
- Redis SET/GET with TTL for caching
- HTTP 301 vs 302 redirects
- SQLAlchemy ORM
- Docker + docker-compose multi-container setup
- python-dotenv for environment config

---

Part of my [Backend Engineering Portfolio](https://github.com/hirthikk-bwd/backend-projects) — building production-grade backend systems from scratch.
