# FitBuddy

FitBuddy is a FastAPI + SQLite application that generates personalized seven-day workout plans, nutrition guidance, and feedback-based revisions. It uses Google Gemini when `GOOGLE_API_KEY` is configured and deterministic demo responses otherwise.

## VS Code setup

1. Open this folder in VS Code.
2. Install the Python extension.
3. Create a virtual environment: `python -m venv .venv`.
4. Activate it in PowerShell: `.venv\\Scripts\\Activate.ps1`.
5. Install dependencies: `python -m pip install -r requirements.txt`.
6. Optional: copy `.env.example` to `.env` and add a Gemini API key.

## Run

```powershell
python -m uvicorn app.main:app --reload
```

Open `http://127.0.0.1:8000` for the web app and `http://127.0.0.1:8000/docs` for Swagger API docs. The SQLite database is created as `fitbuddy.db` on first startup.

## API examples

Generate a plan with `POST /api/generate-plan`:

```json
{"user_id": 1001, "name": "Alex", "age": 28, "weight": 70, "goal": "build strength", "intensity": "medium"}
```

Update it with `POST /api/update-plan/1001`:

```json
{"user_id": 1001, "feedback": "Add more cardio and keep one extra rest day."}
```

Other endpoints: `GET /api/users`, `GET /api/users/{user_id}`, and `GET /view-all-users`.

## Test

```powershell
python -m pytest
```

The tests use the demo AI mode and an isolated SQLite database, so no API key is required.
