from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
import sqlite3
import os
import requests

BOT_TOKEN = os.getenv("BOT_TOKEN")
API_URL = f"https://api.telegram.org/bot{BOT_TOKEN}"

app = FastAPI()

# --- DB ---
conn = sqlite3.connect("users.db", check_same_thread=False)
cur = conn.cursor()
cur.execute("""
CREATE TABLE IF NOT EXISTS users (
    user_id INTEGER PRIMARY KEY,
    premium INTEGER DEFAULT 0
)
""")
conn.commit()

# --- Static ---
app.mount("/static", StaticFiles(directory="app"), name="static")

# --- Pages ---
@app.get("/", response_class=HTMLResponse)
async def index():
    with open("app/index.html", "r", encoding="utf-8") as f:
        return f.read()

# --- API ---
@app.post("/api/status")
async def status(data: dict):
    user_id = data.get("user_id")
    cur.execute("SELECT premium FROM users WHERE user_id=?", (user_id,))
    row = cur.fetchone()
    return {"premium": bool(row and row[0] == 1)}

@app.post("/api/activate")
async def activate(data: dict):
    user_id = data.get("user_id")
    cur.execute(
        "INSERT INTO users (user_id, premium) VALUES (?,1) "
        "ON CONFLICT(user_id) DO UPDATE SET premium=1",
        (user_id,)
    )
    conn.commit()
    return {"success": True}

# --- Telegram Webhook ---
@app.post("/webhook")
async def telegram(request: Request):
    data = await request.json()
    if "message" not in data:
        return {"ok": True}

    msg = data["message"]
    chat_id = msg["chat"]["id"]
    text = msg.get("text", "")

    if text.startswith("/start"):
        requests.post(
            f"{API_URL}/sendMessage",
            json={
                "chat_id": chat_id,
                "text": "🚀 Open premium dashboard",
                "reply_markup": {
                    "inline_keyboard": [[{
                        "text": "✨ Open Mini App",
                        "web_app": {"url": os.getenv("APP_URL")}
                    }]]
                }
            }
        )

    return {"ok": True}
