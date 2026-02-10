from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
import requests
import os

app = FastAPI()

# === CONFIG ===
TOKEN = os.getenv("BOT_TOKEN")
API_URL = f"https://api.telegram.org/bot{TOKEN}"

# === STATIC FILES ===
app.mount("/static", StaticFiles(directory="app"), name="static")

# === MAIN MINI APP PAGE ===
@app.get("/", response_class=HTMLResponse)
async def index():
    with open("app/index.html", "r", encoding="utf-8") as f:
        return f.read()

# === TELEGRAM WEBHOOK ===
@app.post("/webhook")
async def telegram_webhook(request: Request):
    data = await request.json()

    if "message" not in data:
        return {"ok": True}

    message = data["message"]
    chat_id = message["chat"]["id"]
    text = message.get("text", "")

    if text.startswith("/start"):
        requests.post(
            f"{API_URL}/sendMessage",
            json={
                "chat_id": chat_id,
                "text": "🚀 Open premium mini app",
                "reply_markup": {
                    "inline_keyboard": [[
                        {
                            "text": "✨ Open Mini App",
                            "web_app": {
                                "url": "https://tg-miniapp-iggw.onrender.com"
                            }
                        }
                    ]]
                }
            }
        )

    return {"ok": True}
