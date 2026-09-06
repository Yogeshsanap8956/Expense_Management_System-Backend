# Shree Ganesh Mitra Mandal – Backend

FastAPI API for the mandal operations app (vargani, expenses, aarti, mahaprasad, inventory, reports).

## Run locally

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
copy .env.example .env
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

API docs: http://127.0.0.1:8000/docs

Demo login:

- Admin: `9999999999` / `admin123`
- Members: `9000000001` … `9000000008` / `member123`
