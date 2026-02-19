import os
import sqlite3
from datetime import datetime, timedelta, timezone
from typing import Optional, Dict, Any

import requests
from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles

BOT_TOKEN = os.getenv("BOT_TOKEN", "").strip()
ADMIN_KEY = os.getenv("ADMIN_KEY", "").strip()  # придумай и задай в Render
APP_URL = os.getenv("APP_URL", "").strip()      # https://<your-service>.onrender.com

API_URL = f"https://api.telegram.org/bot{BOT_TOKEN}" if BOT_TOKEN else ""

DB_PATH = os.getenv("DB_PATH", "users.db")

app = FastAPI()

# --- DB ---
conn = sqlite3.connect(DB_PATH, check_same_thread=False)
cur = conn.cursor()
cur.execute("""
CREATE TABLE IF NOT EXISTS users (
  user_id INTEGER PRIMARY KEY,
  plan TEXT DEFAULT 'FREE',
  expires_at TEXT DEFAULT NULL,
  updated_at TEXT DEFAULT NULL
)
""")
conn.commit()

def now_utc() -> datetime:
    return datetime.now(timezone.utc)

def iso(dt: datetime) -> str:
    return dt.astimezone(timezone.utc).isoformat()

def parse_iso(s: Optional[str]) -> Optional[datetime]:
    if not s:
        return None
    try:
        return datetime.fromisoformat(s)
    except Exception:
        return None

def get_user(user_id: int) -> Dict[str, Any]:
    cur.execute("SELECT user_id, plan, expires_at FROM users WHERE user_id=?", (user_id,))
    row = cur.fetchone()
    if not row:
        return {"user_id": user_id, "plan": "FREE", "expires_at": None, "is_active": False}
    expires = parse_iso(row[2])
    active = bool(expires and expires > now_utc())
    return {"user_id": row[0], "plan": row[1] or "FREE", "expires_at": row[2], "is_active": active}

def upsert_user(user_id: int, plan: str, expires_at: Optional[str]) -> None:
    cur.execute("""
    INSERT INTO users (user_id, plan, expires_at, updated_at)
    VALUES (?, ?, ?, ?)
    ON CONFLICT(user_id) DO UPDATE SET
      plan=excluded.plan,
      expires_at=excluded.expires_at,
      updated_at=excluded.updated_at
    """, (user_id, plan, expires_at, iso(now_utc())))
    conn.commit()

def require_admin(request: Request):
    key = request.headers.get("x-admin-key", "")
    if not ADMIN_KEY or key != ADMIN_KEY:
        raise HTTPException(status_code=401, detail="Unauthorized")

# --- Static ---
app.mount("/static", StaticFiles(directory="app"), name="static")

# --- Pages ---
@app.get("/", response_class=HTMLResponse)
async def index():
    with open("app/index.html", "r", encoding="utf-8") as f:
        return f.read()

# --- Health ---
@app.get("/api/health")
async def health():
    return {"ok": True, "time": iso(now_utc())}

# --- Public API for Mini App ---
@app.post("/api/status")
async def status(payload: Dict[str, Any]):
    user_id = payload.get("user_id")
    if not user_id:
        return JSONResponse({"ok": True, "user": None, "note": "no_user_id"}, status_code=200)
    try:
        user_id = int(user_id)
    except Exception:
        raise HTTPException(status_code=400, detail="bad user_id")
    u = get_user(user_id)
    # если истёк — принудительно FREE (чтобы UI был честный)
    if u["plan"] != "FREE" and not u["is_active"]:
        upsert_user(user_id, "FREE", None)
        u = get_user(user_id)
    return {"ok": True, "user": u}

@app.post("/api/activate")
async def activate(payload: Dict[str, Any]):
    """
    Demo-активация PRO на 30 дней.
    Реальные платежи подключаются позже (Stripe/CryptoPay/TonConnect).
    """
    user_id = payload.get("user_id")
    if not user_id:
        raise HTTPException(status_code=400, detail="no user_id")
    try:
        user_id = int(user_id)
    except Exception:
        raise HTTPException(status_code=400, detail="bad user_id")

    days = int(payload.get("days") or 30)
    expires = now_utc() + timedelta(days=days)
    upsert_user(user_id, "PRO", iso(expires))
    return {"ok": True, "user": get_user(user_id)}

# --- Admin API (for SaaS owner) ---
@app.get("/api/admin/users")
async def admin_users(request: Request, q: str = "", limit: int = 50):
    require_admin(request)
    limit = max(1, min(int(limit), 200))
    q = (q or "").strip()
    if q:
        # поиск по user_id (частичное совпадение строкой)
        cur.execute("SELECT user_id, plan, expires_at, updated_at FROM users WHERE CAST(user_id AS TEXT) LIKE ? ORDER BY updated_at DESC LIMIT ?",
                    (f"%{q}%", limit))
    else:
        cur.execute("SELECT user_id, plan, expires_at, updated_at FROM users ORDER BY updated_at DESC LIMIT ?", (limit,))
    rows = cur.fetchall()
    items = []
    for r in rows:
        expires = parse_iso(r[2])
        active = bool(expires and expires > now_utc())
        items.append({"user_id": r[0], "plan": r[1], "expires_at": r[2], "updated_at": r[3], "is_active": active})
    return {"ok": True, "items": items}

@app.post("/api/admin/set_plan")
async def admin_set_plan(request: Request, payload: Dict[str, Any]):
    require_admin(request)
    user_id = payload.get("user_id")
    plan = (payload.get("plan") or "FREE").upper()
    days = payload.get("days")  # optional
    if not user_id:
        raise HTTPException(status_code=400, detail="no user_id")
    user_id = int(user_id)

    if plan == "FREE":
        upsert_user(user_id, "FREE", None)
        return {"ok": True, "user": get_user(user_id)}

    if days is None:
        days = 30
    days = int(days)
    expires = now_utc() + timedelta(days=days)
    upsert_user(user_id, plan, iso(expires))
    return {"ok": True, "user": get_user(user_id)}

# --- Optional: Telegram webhook to send "Open Mini App" button on /start ---
@app.post("/webhook")
async def telegram_webhook(request: Request):
    if not BOT_TOKEN:
        return {"ok": True, "note": "BOT_TOKEN not set"}
    data = await request.json()
    msg = data.get("message") or {}
    text = (msg.get("text") or "").strip()
    chat = msg.get("chat") or {}
    chat_id = chat.get("id")

    if not chat_id:
        return {"ok": True}

    if text.startswith("/start"):
        if not APP_URL:
            # fallback: just text
            requests.post(f"{API_URL}/sendMessage", json={"chat_id": chat_id, "text": "APP_URL is not set on server."})
            return {"ok": True}

        requests.post(
            f"{API_URL}/sendMessage",
            json={
                "chat_id": chat_id,
                "text": "🚀 Open the Mini App:",
                "reply_markup": {
                    "inline_keyboard": [[
                        {"text": "✨ Open Subscribo", "web_app": {"url": APP_URL}}
                    ]]
                }
            },
            timeout=10
        )
    return {"ok": True}
