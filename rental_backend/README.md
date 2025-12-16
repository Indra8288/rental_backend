# Rental House System – FastAPI Backend

A FastAPI backend scaffold that matches your screens & tables:
- JWT auth with 3 roles: **owner**, **admin**, **client**
- Customer registration (with optional ID upload)
- Room availability & room view status colors
- Monthly electric/water input (manual + Excel upload)
- Room payments (full/partly with promise date), stop room, notes
- End-of-month (EOM) roll-over helper
- Electric bill barcode image viewer
- Client issue tickets + history
- Dashboard aggregations
- Customer history: last 12 months for the logged-in client

## Quick start

### 1) Create venv + install
```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

### 2) Configure env
```bash
cp .env .env
```
Edit `.env` (SQLite default is fine).

### 3) Run
```bash
uvicorn app.main:app --reload
```

Open docs: http://127.0.0.1:8000/docs

### 4) Seed an owner user
Run once:
```bash
python -m app.scripts.seed_owner
```
Default creds are in `.env.example`.

## Notes
- This scaffold uses **SQLAlchemy (sync)** to stay simple and portable.
- Some fields needed by UI logic are **added** (non-breaking) compared to your table list:
  - `room_payment.status` (PENDING/ACCEPTED) to support “Blue = Pending accept”
  - `room_note` table for room notes/history
  - `issue_ticket` table for issue logs
  - `user_login.customer_id` + `user_login.room_no` to link **client** logins to a room/customer
- File uploads are stored locally under `./uploads/` and served from `/static/*`.

If you want Postgres:
- set `DATABASE_URL=postgresql+psycopg2://user:pass@host:5432/dbname`
- install `psycopg2-binary` and update requirements.
