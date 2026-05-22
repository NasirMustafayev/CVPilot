# CVPilot

AI-assisted CV analysis for HR teams and job seekers.

## Quick start

**Backend** (terminal 1):

```bash
cd backend
pip install -r requirements.txt
cp .env.example .env   # optional: JWT_SECRET, OPENAI_API_KEY
python -m uvicorn main:app --reload --port 8000
```

**Frontend** (terminal 2):

```bash
npm install
npm run dev
```

Open http://localhost:5173 — register as **HR** or **Candidate**, then use the dashboard.

## Auth

- `POST /auth/register` — email, password (8+ chars), role (`hr` | `candidate`), display name
- `POST /auth/login` — email, password
- `GET /auth/me` — current user (Bearer token)
- CV analysis endpoints require a valid JWT
- `GET /analyses?workspace=hr|candidate` — list saved analyses for the logged-in user
- `GET /analyses/{id}` — load a saved analysis

Users and analysis history are stored in `backend/cvpilot.db` (SQLite). Tokens are signed with `JWT_SECRET` from `.env`.

## Features

- Separate HR and candidate workspaces
- JWT authentication (register / login / session restore)
- CV upload and job fit scoring
- Optional OpenAI-enhanced insights (`OPENAI_API_KEY`)
