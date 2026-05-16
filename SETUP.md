# HireMate Backend — Setup Guide

## Step 1 — Install Python 3.12

Download and install Python 3.12 from https://python.org/downloads

> **Important during install:** Check ✅ "Add Python to PATH"

Verify it works — open a new terminal and run:
```
python --version
```
Expected: `Python 3.12.x`

---

## Step 2 — Set up Supabase Project

1. Go to [supabase.com](https://supabase.com) and sign up (free)
2. Click **"New Project"** → choose a name (e.g. `hiremate`) and set a strong database password
3. Wait ~2 minutes for the project to provision
4. Go to **Project Settings → Database → Connection String → URI**
5. Copy the URI — it looks like:
   ```
   postgresql://postgres:[YOUR-PASSWORD]@db.[PROJECT-REF].supabase.co:5432/postgres
   ```

---

## Step 3 — Configure Environment Variables

```bash
# Navigate to backend folder
cd backend

# Copy the example file
copy .env.example .env
```

Open `backend/.env` and fill in:
```env
DATABASE_URL=postgresql+asyncpg://postgres:[YOUR-PASSWORD]@db.[PROJECT-REF].supabase.co:5432/postgres
SECRET_KEY=run-this-to-generate: python -c "import secrets; print(secrets.token_hex(32))"
```

> Replace `[YOUR-PASSWORD]` and `[PROJECT-REF]` with your actual values.  
> For `SECRET_KEY`, open a terminal and run:
> ```
> python -c "import secrets; print(secrets.token_hex(32))"
> ```
> Copy the output into the .env file.

---

## Step 4 — Install Python Dependencies

```bash
# From the backend/ directory
cd backend
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
```

---

## Step 5 — Create Database Tables

```bash
# Still in backend/ with venv activated
python migrate.py
```

Expected output:
```
🔧 Creating database tables...
✅ Tables created successfully!
   → users
   → candidates
```

---

## Step 6 — Seed Sample Candidates

```bash
python seed.py
```

Expected output:
```
🌱 Seeding database with sample candidates...
✅ Seeded 8 candidates successfully!
```

---

## Step 7 — Start the Backend Server

```bash
uvicorn main:app --reload --port 8000
```

Expected output:
```
INFO:     Uvicorn running on http://127.0.0.1:8000
INFO:     Started reloader process
```

✅ API docs available at: **http://localhost:8000/docs**

---

## Step 8 — Start the Frontend

Open a **new terminal** (keep the backend running):

```bash
# From the project root
cd ..
npm run dev
```

Frontend at: **http://localhost:5173**

---

## Testing the Integration

1. Open http://localhost:5173
2. Click **Sign up** and create an account
3. You'll be redirected to the dashboard
4. Navigate to **Candidates** — all 8 sample candidates should load from Supabase
5. Try dragging a candidate card to a different Kanban column — status persists!

---

## API Endpoints Reference

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/auth/signup` | Register new user |
| POST | `/api/auth/login` | Login, get JWT token |
| GET | `/api/auth/me` | Get current user |
| GET | `/api/candidates/` | List all candidates |
| POST | `/api/candidates/` | Create candidate |
| GET | `/api/candidates/{id}` | Get single candidate |
| PUT | `/api/candidates/{id}` | Update candidate |
| PATCH | `/api/candidates/{id}/status` | Update pipeline status |
| DELETE | `/api/candidates/{id}` | Delete candidate |

Interactive docs: **http://localhost:8000/docs**
