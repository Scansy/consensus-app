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
