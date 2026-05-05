# P4 — Rate Limiter API

A Flask + Redis API that demonstrates four rate limiting algorithms implemented from scratch.

## Tech Stack

- Python 3.11
- Flask
- Redis
- Docker + Docker Compose

## Rate Limiting Algorithms

- **Fixed Window Counter** — counts requests in fixed time buckets
- **Sliding Window Log** — tracks exact timestamps using a Redis sorted set
- **Token Bucket** — refills tokens over time, allows short bursts
- **Sliding Window Counter** — weighted blend of current and previous window counts

## Project Structure

    rate-limiter-api/
    ├── app/
    │   ├── __init__.py       App factory
    │   ├── config.py         Config from environment variables
    │   ├── limiter.py        All 4 rate limiting algorithm classes
    │   ├── middleware.py     before_request hook — intercepts every request
    │   └── routes.py        /ping, /limited, /unlimited endpoints
    ├── .env
    ├── Dockerfile
    ├── docker-compose.yml
    ├── requirements.txt
    └── run.py

## How to Run

    docker-compose up --build

## Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | /ping | Health check |
| GET | /limited | Rate limited route — 5 requests per 60 seconds |
| GET | /unlimited | Always accessible, never blocked |

## Key Concepts

- Middleware pattern using Flask before_request hook
- Redis as the state store for all rate limit counters
- Each algorithm trades off memory, accuracy, and burst tolerance differently
