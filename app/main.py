from fastapi import FastAPI, Request
from fastapi.responses import FileResponse
import requests
import os

TOKEN = os.getenv("BOT_TOKEN")
API_URL = f"https://api.telegram.org/bot{TOKEN}"

app = FastAPI()

# 👉 Главная страница Mini App
@app.get("/")
def serve_app():
    return FileResponse("app/index.html")

# 👉 Webhook от Telegram
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
                "text": "Открой мини-приложение 👇",
                "reply_markup": {
                    "inline_keyboard": [[
                        {
                            "text": "🚀 Open Mini App",
                            "web_app": {
                                "url": "https://tg-miniapp-iggw.onrender.com"
                            }
                        }
                    ]]
                }
            }
        )

    return {"ok": True}
