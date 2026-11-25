import asyncio
import logging
import os
import time
from contextlib import asynccontextmanager
from datetime import datetime, timedelta, timezone
from typing import Any, List, Optional

import httpx
from fastapi import BackgroundTasks, FastAPI
from pydantic import BaseModel

logger = logging.getLogger(__name__)

_CRED_CACHE: dict = {"token": "", "chat_id": "", "expires": 0.0}
_CRED_TTL_SECONDS = 60.0
_http_client: Optional[httpx.AsyncClient] = None


def escape_tg_markdown(text: Any) -> str:
    if not text:
        return ""
    for ch in ("*", "_", "`", "[", "]"):
        text = str(text).replace(ch, "")
    return text.strip()


def get_cached_credentials() -> tuple[str, str]:
    now = time.monotonic()
    if now < _CRED_CACHE["expires"] and _CRED_CACHE["token"] and _CRED_CACHE["chat_id"]:
        return _CRED_CACHE["token"], _CRED_CACHE["chat_id"]

    bot_token = os.environ.get("TELEGRAM_BOT_TOKEN", "").strip()
    chat_id = os.environ.get("TELEGRAM_CHAT_ID", "").strip()
    try:
        from app import app as flask_app
        from models import SystemSetting

        with flask_app.app_context():
            tg_conf = SystemSetting.get_val("telegram_config")
            if isinstance(tg_conf, dict):
                if tg_conf.get("bot_token"):
                    bot_token = str(tg_conf["bot_token"]).strip()
                if tg_conf.get("chat_id"):
                    chat_id = str(tg_conf["chat_id"]).strip()
    except Exception as e:
        logger.warning(f"Failed to fetch telegram_config from DB: {e}")

    _CRED_CACHE.update({"token": bot_token, "chat_id": chat_id, "expires": now + _CRED_TTL_SECONDS})
    return bot_token, chat_id


def invalidate_credentials_cache() -> None:
    _CRED_CACHE["expires"] = 0.0


async def _send_single_chat(client: httpx.AsyncClient, bot_token: str, cid: str, text: str) -> tuple[bool, str]:
    url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
    payload: dict[str, Any] = {"chat_id": cid, "text": text, "parse_mode": "Markdown"}
    last_err = "Telegram request failed"

    for attempt in range(3):
        try:
            resp = await client.post(url, json=payload)
            if resp.status_code == 200:
                return True, "Sent"
            if resp.status_code == 400 and "parse_mode" in payload:
                logger.warning(f"Telegram Markdown 400 for {cid}, retrying plain text")
                payload = {"chat_id": cid, "text": text.replace("*", "").replace("`", "")}
                continue
            last_err = resp.text[:200]
            logger.error(f"Telegram send failed for {cid} ({resp.status_code}): {last_err}")
            if resp.status_code < 500:
                return False, last_err
        except httpx.HTTPError as exc:
            last_err = str(exc) or exc.__class__.__name__
            logger.warning(f"Telegram HTTP attempt {attempt + 1} for {cid} failed: {last_err}")
    return False, last_err


async def send_to_all_chats_async(bot_token: str, chat_id: str, text: str) -> tuple[bool, str]:
    chat_ids = [c.strip() for c in str(chat_id).split(",") if c.strip()]
    if not bot_token or not chat_ids:
        return False, "Bot token or Chat ID is missing"

    async def _dispatch(client: httpx.AsyncClient) -> tuple[bool, str]:
        results = await asyncio.gather(
            *(_send_single_chat(client, bot_token, cid, text) for cid in chat_ids)
        )
        ok = all(r[0] for r in results)
        last_err = next((r[1] for r in results if not r[0]), "Sent")
        return ok, last_err

    if _http_client is not None:
        return await _dispatch(_http_client)

    async with httpx.AsyncClient(timeout=httpx.Timeout(15.0, connect=8.0)) as client:
        return await _dispatch(client)


async def _send_background_alert(bot_token: str, chat_id: str, text: str, label: str) -> None:
    try:
        ok, err = await send_to_all_chats_async(bot_token, chat_id, text)
        if not ok:
            logger.error(f"Telegram {label} failed: {err}")
    except Exception as exc:
        logger.exception(f"Telegram {label} raised unexpected error: {exc}")


def format_order_message(payload: "OrderAlertPayload") -> str:
    item_lines = []
    for idx, item in enumerate(payload.items, 1):
        title = escape_tg_markdown(item.get("title") or item.get("name") or "Item")
        qty = item.get("qty") or 1
        price = float(item.get("price") or 0.0)
        var_name = escape_tg_markdown(item.get("variantName"))
        var_text = f" ({var_name})" if var_name else ""
        item_lines.append(f"  {idx}. {title}{var_text} x{qty} — ${price:.2f}")

    items_formatted = "\n".join(item_lines) if item_lines else "  (No items specified)"
    total_usd = float(payload.total_usd or 0.0)
    khr_equiv = int(total_usd * 4100)
    tg_contact = escape_tg_markdown(payload.telegram_name)
    tg_line = f"✈️ *Telegram:* {tg_contact}\n" if tg_contact else ""

    return (
        f"🛍️ *NEW ORDER ALERT #{payload.order_id}*\n"
        f"━━━━━━━━━━━━━━━━━━━\n"
        f"👤 *Customer:* {escape_tg_markdown(payload.customer_name)}\n"
        f"📞 *Phone:* `{escape_tg_markdown(payload.customer_phone)}`\n"
        f"{tg_line}"
        f"📍 *Address:* {escape_tg_markdown(payload.customer_address)}\n"
        f"💵 *Total:* ${total_usd:.2f} ({khr_equiv:,} ៛)\n"
        f"🎟️ *Promo:* {escape_tg_markdown(payload.promo_code_used or 'None')}\n"
        f"📦 *Items:*\n{items_formatted}\n"
        f"━━━━━━━━━━━━━━━━━━━\n"
        f"⏰ {datetime.now(timezone(timedelta(hours=7))).strftime('%Y-%m-%d %H:%M:%S')} ICT (UTC+7)"
    )


class OrderAlertPayload(BaseModel):
    order_id: int
    customer_name: str = ""
    customer_phone: str = ""
    customer_address: str = ""
    total_usd: float = 0.0
    promo_code_used: Optional[str] = None
    telegram_name: Optional[str] = None
    items: List[dict[str, Any]] = []
    bot_token: Optional[str] = None
    chat_id: Optional[str] = None


class TestAlertPayload(BaseModel):
    bot_token: str
    chat_id: str


class RecoveryAlertPayload(BaseModel):
    full_name: Optional[str] = None
    phone: str
    credit_balance: int = 0
    note: Optional[str] = None


@asynccontextmanager
async def lifespan(_: FastAPI):
    global _http_client
    _http_client = httpx.AsyncClient(timeout=httpx.Timeout(15.0, connect=8.0))
    try:
        yield
    finally:
        await _http_client.aclose()
        _http_client = None


app = FastAPI(title="Somphea Reak Telegram Alert Service", lifespan=lifespan)


@app.get("/health")
async def health():
    return {"status": "ok"}


@app.post("/alert/order", status_code=202)
async def alert_order(payload: OrderAlertPayload, background_tasks: BackgroundTasks):
    bot_token = (payload.bot_token or "").strip()
    chat_id = (payload.chat_id or "").strip()
    if not bot_token or not chat_id:
        b_tok, c_id = get_cached_credentials()
        bot_token = bot_token or b_tok
        chat_id = chat_id or c_id
    if not bot_token or not chat_id:
        from fastapi import HTTPException
        raise HTTPException(status_code=503, detail="Telegram credentials not configured")

    msg = format_order_message(payload)
    background_tasks.add_task(_send_background_alert, bot_token, chat_id, msg, f"order #{payload.order_id}")
    return {"queued": True, "order_id": payload.order_id}


@app.post("/alert/test")
async def alert_test(payload: TestAlertPayload):
    text = (
        "✅ *Somphea Reak Telegram Alert Connected!*\n\n"
        "Your bot is now configured successfully. You will receive real-time notifications whenever a customer places an order."
    )
    ok, err = await send_to_all_chats_async(payload.bot_token, payload.chat_id, text)
    return {"ok": ok, "message": "Test alert sent successfully! Check your Telegram chat." if ok else f"Telegram API error: {err}"}


@app.post("/alert/recovery", status_code=202)
async def alert_recovery(payload: RecoveryAlertPayload, background_tasks: BackgroundTasks):
    bot_token, chat_id = get_cached_credentials()
    if not bot_token or not chat_id:
        from fastapi import HTTPException
        raise HTTPException(status_code=503, detail="Telegram credentials not configured")

    now_str = datetime.now(timezone(timedelta(hours=7))).strftime("%Y-%m-%d %H:%M:%S")
    safe_note = escape_tg_markdown(payload.note)
    note_line = f"📝 *Note:* {safe_note}\n" if safe_note else ""
    msg = (
        f"🆘 *CUSTOMER ACCOUNT RECOVERY REQUEST*\n"
        f"━━━━━━━━━━━━━━━━━━━\n"
        f"👤 *Customer:* {escape_tg_markdown(payload.full_name or 'N/A')}\n"
        f"📱 *Phone:* `{escape_tg_markdown(payload.phone)}`\n"
        f"🪙 *Credit Balance:* {payload.credit_balance} pts\n"
        f"{note_line}"
        f"━━━━━━━━━━━━━━━━━━━\n"
        f"⏰ {now_str} ICT (UTC+7)\n"
        f"👉 Go to Admin Panel -> Customers to reset and provide their password."
    )
    background_tasks.add_task(_send_background_alert, bot_token, chat_id, msg, "recovery alert")
    return {"queued": True}
