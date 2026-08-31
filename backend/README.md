# Backend

FastAPI server.

## Get started

```bash
python3 -m venv .venv
source .venv/bin/activate       # Windows: .venv\Scripts\activate
pip install -r requirements.txt
uvicorn main:app --reload
```

Then visit `http://localhost:8000/health` — should return `{"status": "ok"}`.

For an interactive page where you can try each endpoint in the browser,
visit `http://localhost:8000/docs`.

## What's here

Rooms, events, and voting — the MVP flow: create a room, join it with a
code, propose an event, vote yes/no on it, close voting.

Data is stored in plain in-memory Python dicts for now (see the comment at
the top of `main.py`) — everything resets when the server restarts. This
will move to a real database (SQLite) once the endpoint logic is settled.

Calendar file generation (.ics for Google Calendar / Outlook) isn't built
yet — cut from the MVP for now, will come back later.
