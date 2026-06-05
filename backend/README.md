# FarmSense Backend

Minimal FastAPI app for FarmSense.

Quick start:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Endpoints:
- `GET /health` — health check
- `GET /api/items/{item_id}` — example item endpoint
