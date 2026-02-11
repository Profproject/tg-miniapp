from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from datetime import datetime, timedelta
import sqlite3
import os
import requests

app = FastAPI()

BOT_TOKEN = os.getenv("BOT_TOKEN")
APP_URL = os.getenv("APP_URL")
API_URL = f"https://api.telegram.org/bot{BOT_TOKEN}"

# -------- DATABASE --------
conn = sqlite3.connect("users.db", check_same_thread=False)
cur = conn.cursor()

cur.execute("""
CREATE TABLE IF NOT EXISTS users (
    user_id INTEGER PRIMARY KEY,
    plan TEXT DEFAULT 'free',
    expires_at TEXT,
    created_at TEXT
)
""")
conn.commit()

# -------- STATIC --------
app.mount("/static", StaticFiles(directory="app"), name="static")

# -------- HELPERS --------
def is_active(expires_at):
    if not expires_at:
        return False
    return datetime.utcnow() < datetime.fromisoformat(expires_at)

def calculate_mrr():
    cur.execute("SELECT COUNT(*) FROM users WHERE plan != 'free'")
    count = cur.fetchone()[0]
    return count * 10  # demo $10 per subscription

# -------- ROUTES --------
@app.get("/", response_class=HTMLResponse)
async def index():
    with open("app/index.html", "r", encoding="utf-8") as f:
        return f.read()

@app.get("/admin", response_class=HTMLResponse)
async def admin():
    return """
    <h1>Admin Panel</h1>
    <div id='stats'></div>
    <script>
    fetch('/api/admin/stats')
    .then(r=>r.json())
    .then(d=>{
        document.getElementById('stats').innerHTML =
        `<p>Total Users: ${d.total}</p>
         <p>Active Subs: ${d.active}</p>
         <p>MRR: $${d.mrr}</p>`;
    })
    </script>
    """

@app.post("/api/status")
async def status(data: dict):
    user_id = data.get("user_id")
    cur.execute("SELECT plan, expires_at FROM users WHERE user_id=?", (user_id,))
    row = cur.fetchone()

    if not row:
        return {"active": False, "plan": "free"}

    plan, expires_at = row
    active = is_active(expires_at)

    if not active:
        cur.execute("UPDATE users SET plan='free' WHERE user_id=?", (user_id,))
        conn.commit()

    return {
        "active": active,
        "plan": plan,
        "expires_at": expires_at
    }

@app.post("/api/activate")
async def activate(data: dict):
    user_id = data.get("user_id")
    plan = data.get("plan", "pro")

    expires = datetime.utcnow() + timedelta(days=30)

    cur.execute("""
    INSERT INTO users (user_id, plan, expires_at, created_at)
    VALUES (?, ?, ?, ?)
    ON CONFLICT(user_id)
    DO UPDATE SET
        plan=?,
        expires_at=?
    """, (
        user_id,
        plan,
        expires.isoformat(),
        datetime.utcnow().isoformat(),
        plan,
        expires.isoformat()
    ))

    conn.commit()

    return {"success": True}

@app.get("/api/admin/stats")
async def admin_stats():
    cur.execute("SELECT COUNT(*) FROM users")
    total = cur.fetchone()[0]

    cur.execute("SELECT expires_at FROM users")
    rows = cur.fetchall()
    active = sum(1 for r in rows if is_active(r[0]))

    return {
        "total": total,
        "active": active,
        "mrr": calculate_mrr()
    }

# -------- TELEGRAM WEBHOOK --------
@app.post("/webhook")
async def webhook(request: Request):
    data = await request.json()
    if "message" not in data:
        return {"ok": True}

    msg = data["message"]
    chat_id = msg["chat"]["id"]

    requests.post(
        f"{API_URL}/sendMessage",
        json={
            "chat_id": chat_id,
            "text": "🚀 Open Subscription Dashboard",
            "reply_markup": {
                "inline_keyboard": [[{
                    "text": "✨ Open Subscribo",
                    "web_app": {"url": APP_URL}
                }]]
            }
        }
    )

    return {"ok": True}
