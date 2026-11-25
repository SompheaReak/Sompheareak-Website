import asyncio
import json
import logging
import os
from concurrent.futures import ThreadPoolExecutor

import requests

from telegram_service import (
    OrderAlertPayload,
    format_order_message,
    get_cached_credentials,
    send_to_all_chats_async,
)

logger = logging.getLogger(__name__)
_EXECUTOR = ThreadPoolExecutor(max_workers=2, thread_name_prefix="tg-alert")


def get_telegram_credentials():
    return get_cached_credentials()


def _parse_order_items(order):
    if not hasattr(order, "items_json") or not order.items_json:
        return []
    try:
        return json.loads(order.items_json) if isinstance(order.items_json, str) else order.items_json
    except Exception:
        return []


def _dispatch_order_worker(payload: OrderAlertPayload, bot_token: str, chat_id: str) -> bool:
    service_url = os.environ.get("TELEGRAM_SERVICE_URL", "").strip().rstrip("/")
    if service_url:
        try:
            resp = requests.post(
                f"{service_url}/alert/order",
                json=payload.model_dump(),
                timeout=3.0,
            )
            if resp.status_code in (200, 202):
                return True
            logger.warning(f"FastAPI telegram service returned {resp.status_code}, falling back to direct send")
        except Exception as exc:
            logger.warning(f"FastAPI telegram service unreachable ({exc}), falling back to direct send")

    msg = format_order_message(payload)
    ok, err = asyncio.run(send_to_all_chats_async(bot_token, chat_id, msg))
    if not ok:
        logger.error(f"Telegram order alert #{payload.order_id} failed: {err}")
    return ok


def send_telegram_order_alert(order, bot_token=None, chat_id=None, async_dispatch=True):
    """
    Dispatches order notification alert to Telegram without blocking the Flask request thread.
    Snapshots order fields before leaving request context.
    """
    if not bot_token or not chat_id:
        b_tok, c_id = get_telegram_credentials()
        bot_token = bot_token or b_tok
        chat_id = chat_id or c_id

    if not bot_token or not chat_id:
        logger.info("Telegram notification skipped: Bot Token or Chat ID not configured.")
        return False

    try:
        payload = OrderAlertPayload(
            order_id=int(order.id),
            customer_name=str(order.customer_name or ""),
            customer_phone=str(order.customer_phone or ""),
            customer_address=str(order.customer_address or ""),
            total_usd=float(order.total_usd or 0.0),
            promo_code_used=order.promo_code_used,
            telegram_name=getattr(order, "telegram_name", None),
            items=_parse_order_items(order),
            bot_token=bot_token,
            chat_id=chat_id,
        )
        if async_dispatch:
            _EXECUTOR.submit(_dispatch_order_worker, payload, bot_token, chat_id)
            return True
        return _dispatch_order_worker(payload, bot_token, chat_id)
    except Exception as e:
        logger.error(f"Error queuing Telegram alert: {e}")
        return False


def send_telegram_test_message(bot_token, chat_id):
    if not bot_token:
        return False, "Bot token is missing"
    if not chat_id:
        return False, "Chat ID is missing"

    text = (
        "✅ *Somphea Reak Telegram Alert Connected!*\n\n"
        "Your bot is now configured successfully. You will receive real-time notifications whenever a customer places an order."
    )
    ok, err = asyncio.run(send_to_all_chats_async(bot_token, chat_id, text))
    if ok:
        return True, "Test alert sent successfully! Check your Telegram chat."
    return False, f"Telegram API error: {err}"


def send_telegram_recovery_alert(user, note=None, async_dispatch=True):
    bot_token, chat_id = get_telegram_credentials()
    if not bot_token or not chat_id:
        logger.info("Telegram recovery alert skipped: Bot Token or Chat ID not configured.")
        return False

    try:
        from datetime import datetime
        from telegram_service import escape_tg_markdown

        now_str = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
        cust_name = escape_tg_markdown(user.full_name or "N/A")
        cust_phone = escape_tg_markdown(user.phone)
        safe_note = escape_tg_markdown(note)
        note_line = f"📝 *Note:* {safe_note}\n" if safe_note else ""
        msg = (
            f"🆘 *CUSTOMER ACCOUNT RECOVERY REQUEST*\n"
            f"━━━━━━━━━━━━━━━━━━━\n"
            f"👤 *Customer:* {cust_name}\n"
            f"📱 *Phone:* `{cust_phone}`\n"
            f"🪙 *Credit Balance:* {user.credit_balance} pts\n"
            f"{note_line}"
            f"━━━━━━━━━━━━━━━━━━━\n"
            f"⏰ {now_str} UTC\n"
            f"👉 Go to Admin Panel -> Customers to reset and provide their password."
        )
        if async_dispatch:
            _EXECUTOR.submit(lambda: asyncio.run(send_to_all_chats_async(bot_token, chat_id, msg)))
            return True
        ok, _ = asyncio.run(send_to_all_chats_async(bot_token, chat_id, msg))
        return ok
    except Exception as e:
        logger.error(f"Error sending recovery Telegram alert: {e}")
        return False
