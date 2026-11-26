# EventFlow

REST API to manage event guests: register organizers, create events' guest lists, generate a QR code per guest and mark their entry once.

## Features

- Current: `GET /health` returns `{"status": "ok"}`.
- Current: `POST /registro` creates an organizer profile (password hashed with bcrypt).
- Current: `POST /login` returns a JWT access token (valid for 60 minutes).
- Current: `POST /invitados` adds a guest to an event.
- Current: `GET /invitados?evento_id=` lists the guests of an event.
- Current: `GET /invitados/{id}/qr` returns a QR code (PNG) for a guest.
- Current: `PATCH /invitados/{id}/ingreso` marks a guest's entry once and returns 409 if the guest is already in.
- Current: Guest endpoints require a valid token (401 without it) and only the owner of the event can use them (403 for events of other profiles, 404 for nonexistent ones).
- Current: Automated tests with pytest run on every push with GitHub Actions against a temporary PostgreSQL database.
- Planned: Import guest lists using AI and send the invitation through WhatsApp.

## Installation

```
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

## Configuration

Copy `.env.example` to `.env` and fill in your real values (database connection and `JWT_SECRET`). The `.env` file is never committed.

```
Copy-Item .env.example .env
```

## Run

```
uvicorn main:app --reload
```

Then open http://127.0.0.1:8000/docs in your browser to try the endpoints.

## Tests

```
pytest
```

Locally, the tests need the PostgreSQL container from `docker-compose.yml` running. In GitHub Actions a temporary database is created automatically.
