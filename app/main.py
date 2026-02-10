from fastapi import FastAPI

app = FastAPI(title="Telegram Mini App Backend")

@app.get("/")
def root():
    return {
        "status": "ok",
        "message": "Backend is running"
    }

@app.get("/health")
def health():
    return {"ok": True}
