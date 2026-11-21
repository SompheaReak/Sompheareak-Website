import os
import logging
import requests
from datetime import datetime

logger = logging.getLogger(__name__)

def send_recovery_sms(phone, otp):
    """
    Sends password recovery OTP to the given phone number via SMS.
    Also mirrors to Telegram bot and logs so recovery code can be tested
    both in production (via SMS gateway) and development/staging (via Telegram/logs).
    """
    message_text = f"[Somphea Reak] Your password recovery code is: {otp}. Valid for 10 minutes. Do not share this code."
    sms_sent = False
    details = ""

    # 1. Dispatch via external SMS gateway if configured in env
    # Supports generic SMS webhook: SMS_GATEWAY_URL (POST {phone, message, otp})
    gateway_url = os.environ.get("SMS_GATEWAY_URL", "").strip()
    api_token = os.environ.get("SMS_GATEWAY_TOKEN", "").strip()
    if gateway_url:
        try:
            headers = {"Authorization": f"Bearer {api_token}"} if api_token else {}
            payload = {
                "to": phone,
                "phone": phone,
                "message": message_text,
                "otp": otp
            }
            resp = requests.post(gateway_url, json=payload, headers=headers, timeout=5.0)
            if resp.status_code in (200, 201):
                sms_sent = True
                details = "Sent via SMS Gateway"
            else:
                logger.warning(f"SMS gateway returned HTTP {resp.status_code}")
        except Exception as e:
            logger.error(f"Error calling SMS gateway: {e}")

    # 2. Mirror to Telegram Bot for real-time verification and admin visibility
    try:
        from telegram_notifier import get_telegram_credentials
        bot_token, chat_id = get_telegram_credentials()
        if bot_token and chat_id:
            tg_text = (
                f"🔐 *PASSWORD RECOVERY OTP*\n"
                f"━━━━━━━━━━━━━━━━━━━\n"
                f"📱 *Phone:* `{phone}`\n"
                f"🔢 *SMS Code:* *{otp}*\n"
                f"⏰ *Validity:* 10 minutes\n"
                f"━━━━━━━━━━━━━━━━━━━\n"
                f"💬 *SMS Preview:*\n\"{message_text}\""
            )
            tg_url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
            requests.post(tg_url, json={
                "chat_id": chat_id,
                "text": tg_text,
                "parse_mode": "Markdown"
            }, timeout=4.0)
    except Exception as e:
        logger.warning(f"Could not mirror OTP to Telegram: {e}")

    # 3. Always log in server console
    logger.info(f"🔑 [SMS RECOVERY] Phone: {phone} | Code: {otp}")
    print(f"🔑 [SMS RECOVERY] Phone: {phone} | Code: {otp}")

    return {
        "success": True,
        "otp": otp,
        "phone": phone,
        "sms_sent": sms_sent,
        "message": details or "Recovery code dispatched"
    }
