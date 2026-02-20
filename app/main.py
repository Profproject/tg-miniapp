import os
import sqlite3
from datetime import datetime, timedelta, timezone
from typing import Optional, Dict, Any

import requests
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles


APP_URL = os.getenv("APP_URL", "").rstrip("/")
ADMIN_KEY = os.getenv("ADMIN_KEY", "").strip()
DB_PATH = os.getenv("DB_PATH", "users.db").strip()

CRYPTOPAY_TOKEN = os.getenv("CRYPTOPAY_TOKEN", "").strip()
CRYPTOPAY_WEBHOOK_SECRET = os.getenv("CRYPTOPAY_WEBHOOK_SECRET", "").strip()
CRYPTOPAY_API = "https://pay.crypt.bot/api"


def now_utc() -> datetime:
    return datetime.now(timezone.utc)


def iso(dt: datetime) -> str:
    return dt.astimezone(timezone.utc).isoformat()


def parse_iso(s: Optional[str]) -> Optional[datetime]:
    if not s:
        return None
    try:
        dt = datetime.fromisoformat(s)
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        return dt
    except Exception:
        return None


app = FastAPI()
app.mount("/static", StaticFiles(directory="app"), name="static")

# ---- DB ----
conn = sqlite3.connect(DB_PATH, check_same_thread=False)
cur = conn.cursor()

cur.execute("""
CREATE TABLE IF NOT EXISTS users (
  user_id INTEGER PRIMARY KEY,
  plan TEXT NOT NULL DEFAULT 'FREE',
  expires_at TEXT DEFAULT NULL,
  updated_at TEXT NOT NULL
)
""")

cur.execute("""
CREATE TABLE IF NOT EXISTS invoices (
  invoice_id INTEGER PRIMARY KEY,
  user_id INTEGER NOT NULL,
  plan TEXT NOT NULL,
  amount TEXT NOT NULL,
  asset TEXT NOT NULL,
  status TEXT NOT NULL DEFAULT 'pending',
  pay_url TEXT DEFAULT NULL,
  created_at TEXT NOT NULL,
  paid_at TEXT DEFAULT NULL
)
""")

conn.commit()


def normalize_user(u: Dict[str, Any]) -> Dict[str, Any]:
    plan = (u.get("plan") or "FREE").upper()
    exp = parse_iso(u.get("expires_at"))
    active = bool(plan != "FREE" and exp and exp > now_utc())
    if plan != "FREE" and not active:
        # expired -> FREE
        try:
            db_set_plan(int(u["user_id"]), "FREE", None)
        except Exception:
            pass
        return {"user_id": u["user_id"], "plan": "FREE", "expires_at": None, "is_active": False}
    return {"user_id": u["user_id"], "plan": plan, "expires_at": u.get("expires_at"), "is_active": active}


def db_get_user(user_id: int) -> Dict[str, Any]:
    c = conn.cursor()
    c.execute("SELECT user_id, plan, expires_at FROM users WHERE user_id=?", (user_id,))
    row = c.fetchone()
    if not row:
        c.execute(
            "INSERT INTO users (user_id, plan, expires_at, updated_at) VALUES (?, 'FREE', NULL, ?)",
            (user_id, iso(now_utc()))
        )
        conn.commit()
        c.execute("SELECT user_id, plan, expires_at FROM users WHERE user_id=?", (user_id,))
        row = c.fetchone()

    user = {"user_id": row[0], "plan": row[1], "expires_at": row[2]}
    return normalize_user(user)


def db_set_plan(user_id: int, plan: str, days: Optional[int]) -> Dict[str, Any]:
    plan = plan.upper().strip()
    if plan not in ("FREE", "PRO", "VIP"):
        raise ValueError("invalid plan")

    expires_at = None
    if plan != "FREE":
        d = int(days) if days is not None else (30 if plan == "PRO" else 90)
        expires_at = iso(now_utc() + timedelta(days=d))

    c = conn.cursor()
    c.execute("""
      INSERT INTO users (user_id, plan, expires_at, updated_at)
      VALUES (?, ?, ?, ?)
      ON CONFLICT(user_id) DO UPDATE SET
        plan=excluded.plan,
        expires_at=excluded.expires_at,
        updated_at=excluded.updated_at
    """, (user_id, plan, expires_at, iso(now_utc())))
    conn.commit()

    return db_get_user(user_id)


# ---- CryptoPay helpers ----
def cryptopay_headers() -> Dict[str, str]:
    if not CRYPTOPAY_TOKEN:
        return {}
    return {"Crypto-Pay-API-Token": CRYPTOPAY_TOKEN}


def cryptopay_call(method: str, payload: Dict[str, Any]) -> Dict[str, Any]:
    if not CRYPTOPAY_TOKEN:
        raise HTTPException(status_code=500, detail="CRYPTOPAY_TOKEN not set")

    r = requests.post(
        f"{CRYPTOPAY_API}/{method}",
        json=payload,
        headers=cryptopay_headers(),
        timeout=20
    )

    data = r.json() if r.content else {}
    if not r.ok or not data.get("ok"):
        raise HTTPException(status_code=502, detail=f"CryptoPay error: {data}")
    return data["result"]


def plan_price(plan: str) -> Dict[str, str]:
    # поменяй под свой оффер
    plan = plan.upper()
    if plan == "PRO":
        return {"asset": "USDT", "amount": "19"}
    if plan == "VIP":
        return {"asset": "USDT", "amount": "49"}
    return {"asset": "USDT", "amount": "0"}


# ---- Pages ----
@app.get("/", response_class=HTMLResponse)
async def index():
    with open("app/index.html", "r", encoding="utf-8") as f:
        return f.read()


# ---- Public API ----
@app.get("/api/health")
async def health():
    return {"ok": True, "time": iso(now_utc())}


@app.post("/api/status")
async def status(payload: Dict[str, Any]):
    user_id = payload.get("user_id")
    if not user_id:
        raise HTTPException(status_code=400, detail="user_id required")
    return db_get_user(int(user_id))


@app.get("/api/status")
async def status_get(user_id: int):
    return db_get_user(int(user_id))


@app.post("/api/activate_demo")
async def activate_demo(payload: Dict[str, Any]):
    """
    Демо-режим (для продажи): включает план без оплаты.
    Если не нужен — удалишь endpoint + кнопки в UI.
    """
    user_id = payload.get("user_id")
    plan = (payload.get("plan") or "PRO").upper()
    if not user_id:
        raise HTTPException(status_code=400, detail="user_id required")
    if plan not in ("PRO", "VIP", "FREE"):
        raise HTTPException(status_code=400, detail="bad plan")
    return db_set_plan(int(user_id), plan, None)


# ---- CryptoPay: create invoice ----
@app.post("/api/pay/create")
async def pay_create(payload: Dict[str, Any]):
    user_id = payload.get("user_id")
    plan = (payload.get("plan") or "").upper().strip()

    if not user_id:
        raise HTTPException(status_code=400, detail="user_id required")
    if plan not in ("PRO", "VIP"):
        raise HTTPException(status_code=400, detail="plan must be PRO or VIP")

    price = plan_price(plan)
    asset = price["asset"]
    amount = price["amount"]

    desc = f"Subscribo {plan} access"
    inv = cryptopay_call("createInvoice", {
        "asset": asset,
        "amount": amount,
        "description": desc,
        "hidden_message": "Thanks! Access will activate automatically.",
        "paid_btn_name": "openBot",
        "paid_btn_url": APP_URL or "https://telegram.org/",
        "payload": f"uid={int(user_id)}|plan={plan}"
    })

    invoice_id = int(inv["invoice_id"])
    pay_url = inv.get("pay_url")

    c = conn.cursor()
    c.execute("""
      INSERT OR REPLACE INTO invoices (invoice_id, user_id, plan, amount, asset, status, pay_url, created_at, paid_at)
      VALUES (?, ?, ?, ?, ?, 'pending', ?, ?, NULL)
    """, (invoice_id, int(user_id), plan, amount, asset, pay_url, iso(now_utc())))
    conn.commit()

    return {"ok": True, "invoice_id": invoice_id, "pay_url": pay_url, "amount": amount, "asset": asset}


# ---- CryptoPay: check invoice (polling) ----
@app.get("/api/pay/check")
async def pay_check(invoice_id: int):
    c = conn.cursor()
    c.execute("SELECT invoice_id, status, user_id, plan FROM invoices WHERE invoice_id=?", (invoice_id,))
    row = c.fetchone()
    if not row:
        raise HTTPException(status_code=404, detail="invoice not found")

    result = cryptopay_call("getInvoices", {"invoice_ids": str(invoice_id)})
    if not result or not result.get("items"):
        raise HTTPException(status_code=502, detail="CryptoPay: invoice not found")

    item = result["items"][0]
    status = item.get("status")  # active | paid | expired

    c.execute("UPDATE invoices SET status=? WHERE invoice_id=?", (status, invoice_id))
    conn.commit()

    if status == "paid":
        user_id = int(row[2])
        plan = str(row[3]).upper()
        db_set_plan(user_id, plan, None)
        c.execute(
            "UPDATE invoices SET paid_at=? WHERE invoice_id=? AND paid_at IS NULL",
            (iso(now_utc()), invoice_id)
        )
        conn.commit()

    u = db_get_user(int(row[2]))
    return {"ok": True, "invoice_id": invoice_id, "status": status, "user": u}


# ---- CryptoPay: webhook ----
@app.post("/api/pay/webhook")
async def pay_webhook(request: Request):
    """
    Надёжный вариант: берём invoice_id из тела и сверяем статус через getInvoices.
    Заголовок x-webhook-secret проверяем только если он реально пришёл.
    """
    secret = request.headers.get("x-webhook-secret", "")
    if CRYPTOPAY_WEBHOOK_SECRET:
        if secret and secret != CRYPTOPAY_WEBHOOK_SECRET:
            raise HTTPException(status_code=401, detail="bad webhook secret")

    body = await request.json()
    payload = body.get("payload") or body.get("invoice") or body.get("data") or {}
    invoice_id = payload.get("invoice_id") or body.get("invoice_id")

    if not invoice_id:
        return {"ok": True}

    try:
        invoice_id = int(invoice_id)
    except Exception:
        return {"ok": True}

    try:
        await pay_check(invoice_id)
    except Exception:
        pass

    return {"ok": True}


# ---- Admin / metrics ----
def require_admin(request: Request):
    key = (request.headers.get("x-admin-key") or "").strip()
    if not ADMIN_KEY or key != ADMIN_KEY:
        raise HTTPException(status_code=401, detail="Unauthorized")


@app.get("/api/metrics")
async def metrics():
    c = conn.cursor()
    c.execute("SELECT COUNT(*) FROM users")
    total = c.fetchone()[0]
    c.execute("SELECT COUNT(*) FROM users WHERE plan='PRO'")
    pro = c.fetchone()[0]
    c.execute("SELECT COUNT(*) FROM users WHERE plan='VIP'")
    vip = c.fetchone()[0]
    return {"total_users": total, "pro_users": pro, "vip_users": vip}


@app.get("/api/admin/users")
async def admin_users(request: Request, limit: int = 100):
    require_admin(request)
    limit = max(1, min(int(limit), 200))
    c = conn.cursor()
    c.execute("SELECT user_id, plan, expires_at, updated_at FROM users ORDER BY updated_at DESC LIMIT ?", (limit,))
    rows = c.fetchall()
    items = []
    for r in rows:
        u = normalize_user({"user_id": r[0], "plan": r[1], "expires_at": r[2]})
        u["updated_at"] = r[3]
        items.append(u)
    return {"ok": True, "items": items}


@app.post("/api/admin/set_plan")
async def admin_set_plan(request: Request, payload: Dict[str, Any]):
    require_admin(request)
    user_id = payload.get("user_id")
    plan = (payload.get("plan") or "FREE").upper()
    days = payload.get("days")

    if not user_id:
        raise HTTPException(status_code=400, detail="user_id required")

    return db_set_plan(int(user_id), plan, int(days) if days is not None else None)
