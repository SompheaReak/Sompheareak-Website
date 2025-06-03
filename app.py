import os 
import requests
# Admin login credentials
ADMIN_USERNAME = 'AdminSompheaReakVitou'
ADMIN_PASSWORD = 'Thesong_Admin@2022?!$'
from flask import Flask, render_template, request, redirect, url_for, jsonify, session, abort
app = Flask(__name__)
def notify_telegram(ip, user_agent):
    import requests

    bot_token = "7528700801:AAGTvXjk5qPBnq_qx69ZOW4RMLuGy40w5k8"  # Confirmed bot token
    chat_id = "-1002654437316" # Confirmed group chat ID

    message = (
        f"📦 *New Visitor or Order Attempt*\n\n"
        f"*IP:* `{ip}`\n"
        f"*Device:* `{user_agent}`"
    )

    url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
    payload = {
        "chat_id": chat_id,
        "text": message,
        "parse_mode": "Markdown"
    }

    try:
        response = requests.post(url, data=payload)
        if response.status_code != 200:
            print(f"[❌] Telegram API Error: {response.status_code} - {response.text}")
        else:
            print(f"[✅] Telegram message sent successfully.")
        print("Telegram Response:", response.text)
    except Exception as e:
        print("[❌] Telegram notify error:", e)

    print("==> Visitor Bot Message Sent")
    print("BOT TOKEN:", bot_token)
    print("CHAT ID:", chat_id)
    print("MESSAGE:", message)
def check_bot_in_group(bot_token, chat_id):
    url = f"https://api.telegram.org/bot{bot_token}/getChatMember"
    user_id = int(bot_token.split(":")[0])
    response = requests.get(url, params={"chat_id": chat_id, "user_id": user_id})
    print("==> Bot Status Check:")
    print(response.text)
# List of IPs you want to ban
banned_ips = ['123.45.67.89','45.119.135.70'] # Replace with real IPs
@app.before_request
def block_banned_ips():
    ip = request.headers.get('X-Forwarded-For', request.remote_addr).split(',')[0].strip()
    user_agent = request.headers.get('User-Agent')

    # Block banned IPs
    if ip in banned_ips:
        abort(403)

    # Only notify once per session
    if not session.get('notified'):
        notify_telegram(ip, user_agent)
        session['notified'] = True
app.secret_key = 'your_secret_key'
app.debug = True

# Products data
products = [
    {"id": 101, "name_kh": "NINJAGO Season 1 - DX Suit","price": 30000, "image": "/static/images/njoss1dx.jpg", "categories": ["LEGO Ninjago", "Toy"], "subcategory": ["Lego Ninjago","Season 1"],"stock": 0},
    {"id": 102, "name_kh": "NINJAGO Season 1 - KAI (DX)","price": 5000, "image": "/static/images/njoss1dxkai.jpg", "categories": ["LEGO Ninjago", "Toy"], "subcategory": ["Lego Ninjago","Season 1"],"stock": 0},
    {"id": 103, "name_kh": "NINJAGO Season 1 - ZANE (DX)","price": 5000, "image": "/static/images/njoss1dxzane.jpg", "categories": ["LEGO Ninjago", "Toy"], "subcategory": ["Lego Ninjago","Season 1"],"stock": 1},
    {"id": 104, "name_kh": "NINJAGO Season 1 - JAY (DX)","price": 5000, "image": "/static/images/njoss1dxjay.jpg", "categories": ["LEGO Ninjago", "Toy"], "subcategory": ["Lego Ninjago","Season 1"],"stock": 1},
    {"id": 105, "name_kh": "NINJAGO Season 1 - COLE (DX)","price": 5000, "image": "/static/images/njoss1dxcole.jpg", "categories": ["LEGO Ninjago", "Toy"], "subcategory": ["Lego Ninjago","Season 1"],"stock": 1},
    {"id": 106, "name_kh": "NINJAGO Season 1 - NYA (DX)","price": 5000, "image": "/static/images/njoss1dxnya.jpg", "categories": ["LEGO Ninjago", "Toy"], "subcategory": ["Lego Ninjago","Season 1"],"stock": 1},
    {"id": 107, "name_kh": "NINJAGO Season 1 - LLOYD (DX)","price": 5000, "image": "/static/images/njoss1dxlloyd.jpg", "categories": ["LEGO Ninjago", "Toy"], "subcategory": ["Lego Ninjago","Season 1"],"stock": 1},
    {"id": 111, "name_kh": "NINJAGO Season 1 - Pilot Suit","price": 25000, "image": "/static/images/njoss1pilot.jpg", "categories": ["LEGO Ninjago", "Toy"], "subcategory": ["Lego Ninjago","Season 1"],"stock": 1},
    {"id": 112, "name_kh": "NINJAGO Season 1 - KAI (Pilot)","price": 5000, "image": "/static/images/njoss1pilotkai.jpg", "categories": ["LEGO Ninjago", "Toy"], "subcategory": ["Lego Ninjago","Season 1"],"stock": 1},
    {"id": 113, "name_kh": "NINJAGO Season 1 - ZANE (Pilot)","price": 25000, "image": "/static/images/njoss1pilotzane.jpg", "categories": ["LEGO Ninjago", "Toy"], "subcategory": ["Lego Ninjago","Season 1"],"stock": 1},
    {"id": 114, "name_kh": "NINJAGO Season 1 - JAY (Pilot)","price": 5000, "image": "/static/images/njoss1pilotjay.jpg", "categories": ["LEGO Ninjago", "Toy"], "subcategory": ["Lego Ninjago","Season 1"],"stock": 1},
    {"id": 115, "name_kh": "NINJAGO Season 1 - COLE (Pilot)","price": 5000, "image": "/static/images/njoss1pilotcole.jpg", "categories": ["LEGO Ninjago", "Toy"], "subcategory": ["Lego Ninjago","Season 1"],"stock": 1},
    {"id": 116,"name_kh": "NINJAGO Season 1 - LLOYD (Pilot)","price": 5000, "image": "/static/images/njoss1pilotlloyd.jpg", "categories": ["LEGO Ninjago", "Toy"], "subcategory": ["Lego Ninjago","Season 1"],"stock": 1},
    {"id": 121, "name_kh": "NINJAGO Season 1 - NRG","price": 35000, "image": "/static/images/njoss1nrg.jpg", "categories": ["LEGO Ninjago", "Toy"], "subcategory": ["Lego Ninjago","Season 1"],"stock": 1},
    {"id": 122, "name_kh": "NINJAGO Season 1 - NRG KAI","price": 7000, "image": "/static/images/njoss1nrgkai.jpg", "categories": ["LEGO Ninjago", "Toy"], "subcategory": ["Lego Ninjago","Season 1"],"stock": 1},
    {"id": 123, "name_kh": "NINJAGO Season 1 - NRG ZANE","price": 7000, "image": "/static/images/njoss1nrgzane.jpg", "categories": ["LEGO Ninjago", "Toy"], "subcategory": ["Lego Ninjago","Season 1"],"stock": 1},
    {"id": 124, "name_kh": "NINJAGO Season 1 - NRG JAY","price": 7000, "image": "/static/images/njoss1nrgjay.jpg", "categories": ["LEGO Ninjago", "Toy"], "subcategory": ["Lego Ninjago","Season 1"],"stock": 1},
    {"id": 125, "name_kh": "NINJAGO Season 1 - NRG COLE","price": 7000, "image": "/static/images/njoss1nrgcole.jpg", "categories": ["LEGO Ninjago", "Toy"], "subcategory": ["Lego Ninjago","Season 1"],"stock": 1},
    {"id": 126, "name_kh": "NINJAGO Season 1 - NRG LLOYD","price": 7000, "image": "/static/images/njoss1nrglloyd.jpg", "categories": ["LEGO Ninjago", "Toy"], "subcategory": ["Lego Ninjago","Season 1"],"stock": 1},
    {"id": 131, "name_kh": "NINJAGO Season 1 - ZX Suits","price": 25000, "image": "/static/images/njoss1zx.jpg", "categories": ["LEGO Ninjago", "Toy"], "subcategory": ["Lego Ninjago","Season 1"],"stock": 1},
    {"id": 132, "name_kh": "NINJAGO Season 1 - KAI (ZX)","price": 5000, "image": "/static/images/njoss1zxkai.jpg", "categories": ["LEGO Ninjago", "Toy"], "subcategory": ["Lego Ninjago","Season 1"],"stock": 1},
    {"id": 133, "name_kh": "NINJAGO Season 1 - ZANE (ZX)","price": 5000, "image": "/static/images/njoss1zxzane.jpg", "categories": ["LEGO Ninjago", "Toy"], "subcategory": ["Lego Ninjago","Season 1"],"stock": 1},
    {"id": 134, "name_kh": "NINJAGO Season 1 - JAY (ZX)","price": 5000, "image": "/static/images/njoss1zxjay.jpg", "categories": ["LEGO Ninjago", "Toy"], "subcategory": ["Lego Ninjago","Season 1"],"stock": 1},
    {"id": 135, "name_kh": "NINJAGO Season 1 - COLE (ZX)","price": 5000, "image": "/static/images/njoss1zxcole.jpg", "categories": ["LEGO Ninjago", "Toy"], "subcategory": ["Lego Ninjago","Season 1"],"stock": 1},
    {"id": 136, "name_kh": "NINJAGO Season 1 - LLOYD (ZX)","price": 5000, "image": "/static/images/njoss1zxlloyd.jpg", "categories": ["LEGO Ninjago", "Toy"], "subcategory": ["Lego Ninjago","Season 1"],"stock": 1},

    {"id": 301, "name_kh": "NINJAGO Season 3 - Techno Robes","price": 36000, "image": "/static/images/njoss3techno.jpg", "categories": ["LEGO Ninjago", "Toy"], "subcategory": ["Lego Ninjago","Season 3"],"stock": 1},
    {"id": 302, "name_kh": "NINJAGO Season 3 - KAI (Techno)","price": 6000, "image": "/static/images/njoss3technokai.jpg", "categories": ["LEGO Ninjago", "Toy"], "subcategory": ["Lego Ninjago","Season 3"],"stock": 1},
    {"id": 303, "name_kh": "NINJAGO Season 3 - ZANE (Techno)","price": 6000, "image": "/static/images/njoss3technozane.jpg", "categories": ["LEGO Ninjago", "Toy"], "subcategory": ["Lego Ninjago","Season 3"],"stock": 1},
    {"id": 304, "name_kh": "NINJAGO Season 3 - ZANE (Techno)","price": 6000, "image": "/static/images/njoss3technozane2.jpg", "categories": ["LEGO Ninjago", "Toy"], "subcategory": ["Lego Ninjago","Season 3"],"stock": 1},
    {"id": 305, "name_kh": "NINJAGO Season 3 - JAY (Techno)","price": 6000, "image": "/static/images/njoss3technojay.jpg", "categories": ["LEGO Ninjago", "Toy"], "subcategory": ["Lego Ninjago","Season 3"],"stock": 1},
    {"id": 306, "name_kh": "NINJAGO Season 3 - COLE (Techno)","price": 6000, "image": "/static/images/njoss3technocole.jpg", "categories": ["LEGO Ninjago", "Toy"], "subcategory": ["Lego Ninjago","Season 3"],"stock": 1},
    {"id": 307, "name_kh": "NINJAGO Season 3 - LLOYD (Techno)","price": 6000, "image": "/static/images/njoss3technolloyd.jpg", "categories": ["LEGO Ninjago", "Toy"], "subcategory": ["Lego Ninjago","Season 3"],"stock": 1},
    {"id": 311, "name_kh": "NINJAGO Season 3 - Stone Armor","price": 36000, "image": "/static/images/njoss3stone.jpg", "categories": ["LEGO Ninjago", "Toy"], "subcategory": ["Lego Ninjago","Season 3"],"stock": 1},
    {"id": 312, "name_kh": "NINJAGO Season 3 - KAI (Stone)","price": 6000, "image": "/static/images/njoss3stonekai.jpg", "categories": ["LEGO Ninjago", "Toy"], "subcategory": ["Lego Ninjago","Season 3"],"stock": 1},
    {"id": 313, "name_kh": "NINJAGO Season 3 - ZANE (Stone)","price": 6000, "image": "/static/images/njoss3stonezane.jpg", "categories": ["LEGO Ninjago", "Toy"], "subcategory": ["Lego Ninjago","Season 3"],"stock": 1},
    {"id": 314, "name_kh": "NINJAGO Season 3 - JAY (Stone)","price": 6000, "image": "/static/images/njoss3stonejay.jpg", "categories": ["LEGO Ninjago", "Toy"], "subcategory": ["Lego Ninjago","Season 3"],"stock": 1},
    {"id": 315, "name_kh": "NINJAGO Season 3 - COLE (Stone)","price": 6000, "image": "/static/images/njoss3stonecole.jpg", "categories": ["LEGO Ninjago", "Toy"], "subcategory": ["Lego Ninjago","Season 3"],"stock": 1},
    {"id": 316, "name_kh": "NINJAGO Season 3 - NYA(Stone)","price": 6000, "image": "/static/images/njoss3stonenya.jpg", "categories": ["LEGO Ninjago", "Toy"], "subcategory": ["Lego Ninjago","Season 3"],"stock": 1},
    {"id": 317, "name_kh": "NINJAGO Season 3 - LLOYD (Stone)","price": 6000, "image": "/static/images/njoss3stonelloyd.jpg", "categories": ["LEGO Ninjago", "Toy"], "subcategory": ["Lego Ninjago","Season 3"],"stock": 1},

    {"id": 401, "name_kh": "NINJAGO Season 4 - Tournament Robes","price": 26000, "image": "/static/images/njoss4tournament.jpg", "categories": ["LEGO Ninjago", "Toy"], "subcategory": ["Lego Ninjago","Season 4"],"stock": 1},
    {"id": 402, "name_kh": "NINJAGO Season 4 - KAI (Tournament)","price": 6500, "image": "/static/images/njoss4tournamentkai.jpg", "categories": ["LEGO Ninjago", "Toy"], "subcategory": ["Lego Ninjago","Season 4"],"stock": 1},
    {"id": 403, "name_kh": "NINJAGO Season 4 - JAY (Tournament)","price": 6500, "image": "/static/images/njoss4tournamentjay.jpg", "categories": ["LEGO Ninjago", "Toy"], "subcategory": ["Lego Ninjago","Season 4"],"stock": 1},
    {"id": 404, "name_kh": "NINJAGO Season 4 - COLE (Tournament)","price": 6500, "image": "/static/images/njoss4tournamentcole.jpg", "categories": ["LEGO Ninjago", "Toy"], "subcategory": ["Lego Ninjago","Season 4"],"stock": 1},
    {"id": 405, "name_kh": "NINJAGO Season 4 - LLOYD (Tournament)","price": 6500, "image": "/static/images/njoss4tournamentlloyd.jpg", "categories": ["LEGO Ninjago", "Toy"], "subcategory": ["Lego Ninjago","Season 4"],"stock": 1},
    {"id": 411, "name_kh": "NINJAGO Season 4 - Jungle Robes","price": 30000, "image": "/static/images/njoss4jungle.jpg", "categories": ["LEGO Ninjago", "Toy"], "subcategory": ["Lego Ninjago","Season 4"],"stock": 1},
    {"id": 412, "name_kh": "NINJAGO Season 4 - KAI (Jungle)","price": 5000, "image": "/static/images/njoss4junglekai.jpg", "categories": ["LEGO Ninjago", "Toy"], "subcategory": ["Lego Ninjago","Season 4"],"stock": 1},
    {"id": 413, "name_kh": "NINJAGO Season 4 - ZANE (Jungle)","price": 5000, "image": "/static/images/njoss4junglezane.jpg", "categories": ["LEGO Ninjago", "Toy"], "subcategory": ["Lego Ninjago","Season 4"],"stock": 1},
    {"id": 414, "name_kh": "NINJAGO Season 4 - JAY (Jungle)","price": 5000, "image": "/static/images/njoss4junglejay.jpg", "categories": ["LEGO Ninjago", "Toy"], "subcategory": ["Lego Ninjago","Season 4"],"stock": 1},
    {"id": 415, "name_kh": "NINJAGO Season 4 - COLE (Jungle)","price": 5000, "image": "/static/images/njoss4junglecole.jpg", "categories": ["LEGO Ninjago", "Toy"], "subcategory": ["Lego Ninjago","Season 4"],"stock": 1},
    {"id": 416, "name_kh": "NINJAGO Season 4 - SKYLAR (Jungle)","price": 5000, "image": "/static/images/njoss4jungleskylar.jpg", "categories": ["LEGO Ninjago", "Toy"], "subcategory": ["Lego Ninjago","Season 4"],"stock": 1},
    {"id": 417, "name_kh": "NINJAGO Season 4 - LLOYD (Jungle)","price": 5000, "image": "/static/images/njoss4junglelloyd.jpg", "categories": ["LEGO Ninjago", "Toy"], "subcategory": ["Lego Ninjago","Season 4"],"stock": 1},

    {"id": 501, "name_kh": "NINJAGO Season 5 - Deepstone Armour","price": 27000, "image": "/static/images/njoss5deep.jpg", "categories": ["LEGO Ninjago", "Toy"], "subcategory": ["Lego Ninjago","Season 5"],"stock": 1},
    {"id": 502, "name_kh": "NINJAGO Season 5 - KAI (Deepstone)","price": 4500, "image": "/static/images/njoss5deepkai.jpg", "categories": ["LEGO Ninjago", "Toy"], "subcategory": ["Lego Ninjago","Season 5"],"stock": 1},
    {"id": 503, "name_kh": "NINJAGO Season 5 - ZANE (Deepstone)","price": 4500, "image": "/static/images/njoss5deepzane.jpg", "categories": ["LEGO Ninjago", "Toy"], "subcategory": ["Lego Ninjago","Season 5"],"stock": 1},
    {"id": 504, "name_kh": "NINJAGO Season 5 - JAY (Deepstone)","price": 4500, "image": "/static/images/njoss5deepjay.jpg", "categories": ["LEGO Ninjago", "Toy"], "subcategory": ["Lego Ninjago","Season 5"],"stock": 1},
    {"id": 505, "name_kh": "NINJAGO Season 5 - COLE (Deepstone)","price": 4500, "image": "/static/images/njoss5deepcole.jpg", "categories": ["LEGO Ninjago", "Toy"], "subcategory": ["Lego Ninjago","Season 5"],"stock": 1},
    {"id": 506, "name_kh": "NINJAGO Season 5 - NYA (Deepstone) ","price": 4500, "image": "/static/images/njoss5deepnya.jpg", "categories": ["LEGO Ninjago", "Toy"], "subcategory": ["Lego Ninjago","Season 5"],"stock": 1},
    {"id": 507, "name_kh": "NINJAGO Season 5 - LLOYD (Deepstone)","price": 4500, "image": "/static/images/njoss5deeplloyd.jpg", "categories": ["LEGO Ninjago", "Toy"], "subcategory": ["Lego Ninjago","Season 5"],"stock": 1},
    {"id": 511, "name_kh": "NINJAGO Season 5 - Air Jitzu","price": 36000, "image": "/static/images/njoss5air.jpg", "categories": ["LEGO Ninjago", "Toy"], "subcategory": ["Lego Ninjago","Season 5"],"stock": 1},
    {"id": 512, "name_kh": "NINJAGO Season 5 - KAI (Air)","price": 6000, "image": "/static/images/njoss5airkai.jpg", "categories": ["LEGO Ninjago", "Toy"], "subcategory": ["Lego Ninjago","Season 5"],"stock": 1},
    {"id": 513, "name_kh": "NINJAGO Season 5 - ZANE (Air)","price": 6000, "image": "/static/images/njoss5airzane.jpg", "categories": ["LEGO Ninjago", "Toy"], "subcategory": ["Lego Ninjago","Season 5"],"stock": 1},
    {"id": 514, "name_kh": "NINJAGO Season 5 - JAY (Air)","price": 6000, "image": "/static/images/njoss5airjay.jpg", "categories": ["LEGO Ninjago", "Toy"], "subcategory": ["Lego Ninjago","Season 5"],"stock": 1},
    {"id": 515, "name_kh": "NINJAGO Season 5 - COLE (Air)","price": 6000, "image": "/static/images/njoss5aircole.jpg", "categories": ["LEGO Ninjago", "Toy"], "subcategory": ["Lego Ninjago","Season 5"],"stock": 1},
    {"id": 516, "name_kh": "NINJAGO Season 5 - NYA (Air) ","price": 6000, "image": "/static/images/njoss5airnya.jpg", "categories": ["LEGO Ninjago", "Toy"], "subcategory": ["Lego Ninjago","Season 5"],"stock": 1},
    {"id": 517, "name_kh": "NINJAGO Season 5 - LLOYD (Air)","price": 6000, "image": "/static/images/njoss5airlloyd.jpg", "categories": ["LEGO Ninjago", "Toy"], "subcategory": ["Lego Ninjago","Season 5"],"stock": 1},
    {"id": 521, "name_kh": "NINJAGO Season 5 - Future Robes","price": 39000, "image": "/static/images/njoss5future.jpg", "categories": ["LEGO Ninjago", "Toy"], "subcategory": ["Lego Ninjago","Season 5"],"stock": 1},
    {"id": 522, "name_kh": "NINJAGO Season 5 - KAI (Future)","price": 6500, "image": "/static/images/njoss5futurekai.jpg", "categories": ["LEGO Ninjago", "Toy"], "subcategory": ["Lego Ninjago","Season 5"],"stock": 1},
    {"id": 523, "name_kh": "NINJAGO Season 5 - ZANE (Future)","price": 6500, "image": "/static/images/njoss5futurezane.jpg", "categories": ["LEGO Ninjago", "Toy"], "subcategory": ["Lego Ninjago","Season 5"],"stock": 1},
    {"id": 524, "name_kh": "NINJAGO Season 5 - JAY (Future)","price": 6500, "image": "/static/images/njoss5futurrjay.jpg", "categories": ["LEGO Ninjago", "Toy"], "subcategory": ["Lego Ninjago","Season 5"],"stock": 1},
    {"id": 525, "name_kh": "NINJAGO Season 5 - COLE (Future)","price": 6500, "image": "/static/images/njoss5futurecole.jpg", "categories": ["LEGO Ninjago", "Toy"], "subcategory": ["Lego Ninjago","Season 5"],"stock": 1},
    {"id": 526, "name_kh": "NINJAGO Season 5 - NYA (Future) ","price": 6500, "image": "/static/images/njoss5futurenya.jpg", "categories": ["LEGO Ninjago", "Toy"], "subcategory": ["Lego Ninjago","Season 5"],"stock": 1},
    {"id": 527, "name_kh": "NINJAGO Season 5 - LLOYD (Future)","price": 6500, "image": "/static/images/njoss5futurelloyd.jpg", "categories": ["LEGO Ninjago", "Toy"], "subcategory": ["Lego Ninjago","Season 5"],"stock": 1},

    {"id": 601, "name_kh": "NINJAGO Season 6 - Destiny Robes","price": 27000, "image": "/static/images/njoss6destiny.jpg", "categories": ["LEGO Ninjago", "Toy"], "subcategory": ["Lego Ninjago","Season 6"],"stock": 1},
    {"id": 602, "name_kh": "NINJAGO Season 6 - KAI (Destiny)","price": 4500, "image": "/static/images/njoss6destinykai.jpg", "categories": ["LEGO Ninjago", "Toy"], "subcategory": ["Lego Ninjago","Season 6"],"stock": 1},
    {"id": 603, "name_kh": "NINJAGO Season 6 - ZANE (Destiny)","price": 4500, "image": "/static/images/njoss6destinyzane.jpg", "categories": ["LEGO Ninjago", "Toy"], "subcategory": ["Lego Ninjago","Season 6"],"stock": 1},
    {"id": 604, "name_kh": "NINJAGO Season 6 - JAY (Destiny)","price": 4500, "image": "/static/images/njoss6destinyjay.jpg", "categories": ["LEGO Ninjago", "Toy"], "subcategory": ["Lego Ninjago","Season 6"],"stock": 1},
    {"id": 605, "name_kh": "NINJAGO Season 6 - COLE (Destiny)","price": 4500, "image": "/static/images/njoss6destinycole.jpg", "categories": ["LEGO Ninjago", "Toy"], "subcategory": ["Lego Ninjago","Season 6"],"stock": 1},
    {"id": 606, "name_kh": "NINJAGO Season 6 - NYA (Destiny) ","price": 4500, "image": "/static/images/njoss6destinynya.jpg", "categories": ["LEGO Ninjago", "Toy"], "subcategory": ["Lego Ninjago","Season 6"],"stock": 1},
    {"id": 607, "name_kh": "NINJAGO Season 6 - LLOYD (Destiny)","price": 4500, "image": "/static/images/njoss6destinylloyd.jpg", "categories": ["LEGO Ninjago", "Toy"], "subcategory": ["Lego Ninjago","Season 6"],"stock": 1},

    {"id": 1916, "name_kh": " Dragon Rising S3 - NOKT","price": 9000, "image": "/static/images/ss3nokt.jpg", "categories": ["LEGO Ninjago", "Toy"], "subcategory": ["Lego Ninjago","New"],"stock": 1},
    {"id": 1917, "name_kh": " Dragon Rising S3 - ROX","price": 9000, "image": "/static/images/ss3rox.jpg", "categories": ["LEGO Ninjago", "Toy"], "subcategory": ["Lego Ninjago","New"],"stock": 1},
    {"id": 1918, "name_kh": " Dragon Rising S3 - DRIX","price": 9000, "image": "/static/images/ss3drix.jpg", "categories": ["LEGO Ninjago", "Toy"], "subcategory": ["Lego Ninjago","New"],"stock": 1},
    {"id": 1919, "name_kh": " Dragon Rising S3 - ZARKT","price": 9000, "image": "/static/images/ss3zarkt.jpg", "categories": ["LEGO Ninjago", "Toy"], "subcategory": ["Lego Ninjago","New"],"stock": 1},
    {"id": 1920, "name_kh": " Dragon Rising S3 - KUR","price": 9000, "image": "/static/images/ss3kur.jpg", "categories": ["LEGO Ninjago", "Toy"], "subcategory": ["Lego Ninjago","New"],"stock": 1},

    {"id": 1101, "name_kh": "Zane's Set", "price": 68000, "image": "/static/images/nj01.jpg", "categories": ["LEGO Ninjago","Toy"], "subcategory": ["Lego Ninjago","Building Set"]},
    {"id": 1102, "name_kh": "Kai Merch", "price": 64000, "image": "/static/images/nj02.jpg", "categories": ["LEGO Ninjago", "Toy"], "subcategory": ["Lego Ninjago","Building Set"]},
    {"id": 1003, "name_kh": "cole Merch", "price": 140000, "image": "/static/images/nj03.jpg", "categories": ["LEGO Ninjago", "Toy"], "subcategory": ["Lego Ninjago","Building Set"]},
    {"id": 1004, "name_kh": "idk name ", "price": 88000, "image": "/static/images/nj04.jpg", "categories": ["LEGO Ninjago", "Toy"], "subcategory": ["Lego Ninjago","Building Set"]},
    {"id": 1005, "name_kh": "Zane's Set", "price": 132000, "image": "/static/images/nj05.jpg", "categories": ["LEGO Ninjago","Toy"], "subcategory": ["Lego Ninjago","Building Set"]},
    {"id": 1006, "name_kh": "Kai Merch", "price": 132000, "image": "/static/images/nj06.jpg", "categories": ["LEGO Ninjago", "Toy"], "subcategory": ["Lego Ninjago","Building Set"]},
    {"id": 1007, "name_kh": "cole Merch", "price": 43000, "image": "/static/images/nj07.jpg", "categories": ["LEGO Ninjago", "Toy"], "subcategory": ["Lego Ninjago","Building Set"]},
    {"id": 1008, "name_kh": "idk name ", "price": 43000, "image": "/static/images/nj08.jpg", "categories": ["LEGO Ninjago", "Toy"], "subcategory": ["Lego Ninjago","Building Set"]},
    {"id": 1009, "name_kh": "Zane's Set", "price": 44000, "image": "/static/images/nj09.jpg", "categories": ["LEGO Ninjago","Toy"], "subcategory": ["Lego Ninjago","Building Set"]},
    {"id": 1010, "name_kh": "Kai Merch", "price": 46000, "image": "/static/images/nj10.jpg", "categories": ["LEGO Ninjago", "Toy"], "subcategory": ["Lego Ninjago","Building Set"]},
    {"id": 1011, "name_kh": "cole Merch", "price": 28000, "image": "/static/images/nj11.jpg", "categories": ["LEGO Ninjago", "Toy"], "subcategory": ["Lego Ninjago","Building Set"]},
    {"id": 1012, "name_kh": "idk name ", "price": 46000, "image": "/static/images/nj12.jpg", "categories": ["LEGO Ninjago", "Toy"], "subcategory": ["Lego Ninjago","Building Set"]},
    {"id": 1013, "name_kh": "Kai Merch", "price": 49000, "image": "/static/images/nj13.jpg", "categories": ["LEGO Ninjago", "Toy"], "subcategory": ["Lego Ninjago","Building Set"]},
    {"id": 1014, "name_kh": "cole Merch", "price": 45000, "image": "/static/images/nj14.jpg", "categories": ["LEGO Ninjago", "Toy"], "subcategory": ["Lego Ninjago","Building Set"]},
    {"id": 1015, "name_kh": "idk name ", "price": 66000, "image": "/static/images/nj15.jpg", "categories": ["LEGO Ninjago", "Toy"], "subcategory": ["Lego Ninjago","Building Set"]},
    {"id": 1016, "name_kh": "Kai Merch", "price": 46000, "image": "/static/images/nj16.jpg", "categories": ["LEGO Ninjago", "Toy"], "subcategory": ["Lego Ninjago","Building Set"]},
    {"id": 1017, "name_kh": "cole Merch", "price": 38000, "image": "/static/images/nj17.jpg", "categories": ["LEGO Ninjago", "Toy"], "subcategory": ["Lego Ninjago","Building Set"]},
    {"id": 1018, "name_kh": "idk name ", "price": 59000, "image": "/static/images/nj18.jpg", "categories": ["LEGO Ninjago", "Toy"], "subcategory": ["Lego Ninjago","Building Set"]},
    {"id": 1019, "name_kh": "Kai Merch", "price": 52000, "image": "/static/images/nj19.jpg", "categories": ["LEGO Ninjago", "Toy"], "subcategory": ["Lego Ninjago","Building Set"]},
    {"id": 1020, "name_kh": "cole Merch", "price": 5000, "image": "/static/images/nj20.jpg", "categories": ["LEGO Ninjago", "Toy"], "subcategory": ["Lego Ninjago","Building Set"]},
    {"id": 1021, "name_kh": "idk name ", "price": 5000, "image": "/static/images/nj21.jpg", "categories": ["LEGO Ninjago", "Toy"], "subcategory": ["Lego Ninjago","Building Set"]},

    {"id": 2001, "name_kh": "WWII Germany 01","price": 1250, "image": "/static/images/wwii-01.jpg", "categories": ["toy"], "subcategory": "Lego WWII"},
    {"id": 2002, "name_kh": "WWII Germany 02","price": 1250, "image": "/static/images/wwii-02.jpg", "categories": ["toy"], "subcategory": "Lego WWII"},
    {"id": 2003, "name_kh": "WWII Germany 03","price": 1250, "image": "/static/images/wwii-03.jpg", "categories": ["toy"], "subcategory": "Lego WWII"},
    {"id": 2004, "name_kh": "WWII Germany 04","price": 1250, "image": "/static/images/wwii-04.jpg", "categories": ["toy"], "subcategory": "Lego WWII"},
    {"id": 2005, "name_kh": "WWII Germany 05","price": 1250, "image": "/static/images/wwii-05.jpg", "categories": ["toy"], "subcategory": "Lego WWII"},
    {"id": 2006, "name_kh": "WWII Germany 06", "name_en": "WWII Germany 06", "price": 1250, "image": "/static/images/wwii-06.jpg", "categories": ["toy"], "subcategory": "Lego WWII"},
    {"id": 2007, "name_kh": "WWII USA 01", "name_en": "WWII USA 01", "price": 1250, "image": "/static/images/wwii-07.jpg", "categories": ["toy"], "subcategory": "Lego WWII"},
    {"id": 2008, "name_kh": "WWII USA 02", "name_en": "WWII USA 02", "price": 1250, "image": "/static/images/wwii-08.jpg", "categories": ["toy"], "subcategory": "Lego WWII"},
    {"id": 2009, "name_kh": "WWII USA 03", "name_en": "WWII USA 03", "price": 1250, "image": "/static/images/wwii-09.jpg", "categories": ["toy"], "subcategory": "Lego WWII"},
    {"id": 2010, "name_kh": "WWII USA 04", "name_en": "WWII USA 04", "price": 1250, "image": "/static/images/wwii-10.jpg", "categories": ["toy"], "subcategory": "Lego WWII"},
    {"id": 2011, "name_kh": "WWII USA 05", "name_en": "WWII USA 05", "price": 1250, "image": "/static/images/wwii-11.jpg", "categories": ["toy"], "subcategory": "Lego WWII"},
    {"id": 2012, "name_kh": "WWII SOVIET 01", "name_en": "WWII SOVIET 01", "price": 1250, "image": "/static/images/wwii-12.jpg", "categories": ["toy"], "subcategory": "Lego WWII"},
    {"id": 2013, "name_kh": "WWII SOVIET 02", "name_en": "WWII SOVIET 02", "price": 1250, "image": "/static/images/wwii-13.jpg", "categories": ["toy"], "subcategory": "Lego WWII"},
    {"id": 2014, "name_kh": "WWII SOVIET 03", "name_en": "WWII SOVIET 03", "price": 1250, "image": "/static/images/wwii-14.jpg", "categories": ["toy"], "subcategory": "Lego WWII"},
    {"id": 2015, "name_kh": "WWII SOVIET 04", "name_en": "WWII SOVIET 04", "price": 1250, "image": "/static/images/wwii-15.jpg", "categories": ["toy"], "subcategory": "Lego WWII"},
    {"id": 2016, "name_kh": "WWII SOVIET 05", "name_en": "WWII SOVIET 05", "price": 1250, "image": "/static/images/wwii-16.jpg", "categories": ["toy"], "subcategory": "Lego WWII"},
    {"id": 2017, "name_kh": "WWII SOVIET 06", "name_en": "WWII SOVIET 06", "price": 1250, "image": "/static/images/wwii-17.jpg", "categories": ["toy"], "subcategory": "Lego WWII"},
    {"id": 2018, "name_kh": "WWII SOVIET 07", "name_en": "WWII SOVIET 07", "price": 1250, "image": "/static/images/wwii-18.jpg", "categories": ["toy"], "subcategory": "Lego WWII"},
    {"id": 2019, "name_kh": "WWII SOVIET 08", "name_en": "WWII SOVIET 08", "price": 1250, "image": "/static/images/wwii-19.jpg", "categories": ["toy"], "subcategory": "Lego WWII"},
    {"id": 3101, "name_kh": "ខ្សៃដៃ GYM BRACELET - គ្រាប់រលោង(ខ្មៅ)","price": 5000, "image": "/static/images/gymblack1.jpg", "categories": ["Accessories","Hot Sale"], "subcategory": "Gym Bracelet"},
    {"id": 3102, "name_kh": "ខ្សៃដៃ GYM BRACELET - គ្រាប់គ្រើម(ខ្មៅ)","price": 5000, "image": "/static/images/gymblack2.jpg", "categories": ["Accessories","Hot Sale"], "subcategory": "Gym Bracelet"},
    {"id": 3103, "name_kh": "ខ្សៃដៃ GYM BRACELET - គ្រាប់រលោង(ប្រាក់)","price": 5000, "image": "/static/images/gymsilver1.jpg", "categories": ["Accessories","Hot Sale"], "subcategory": "Gym Bracelet"},
    {"id": 3104, "name_kh": "ខ្សៃដៃ GYM BRACELET - គ្រាប់គ្រើម(ប្រាក់)","price": 5000, "image": "/static/images/gymsilver2.jpg", "categories": ["Accessories","Hot Sale"], "subcategory": "Gym Bracelet"},
    {"id": 3105, "name_kh": "ខ្សៃដៃ GYM BRACELET - គ្រាប់រលោង(មាស)","price": 5000, "image": "/static/images/gymgold1.jpg", "categories": ["Accessories","Hot Sale"], "subcategory": "Gym Bracelet"},
    {"id": 3106, "name_kh": "ខ្សៃដៃ GYM BRACELET - គ្រាប់គ្រើម(មាស) ","price": 5000, "image": "/static/images/gymgold2.jpg", "categories": ["Accessories","Hot Sale"], "subcategory": "Gym Bracelet"},

    {"id": 3011, "name_kh": "ខ្សែដៃថ្មធម្មជាតិ -","price": 6000, "image": "/static/images/bcl01.jpg", "categories": ["Accessories"], "subcategory": "Bracelet"},
    {"id": 3012, "name_kh": "ខ្សែដៃថ្មធម្មជាតិ - ","price": 6000, "image": "/static/images/bcl02.jpg", "categories": ["Accessories"], "subcategory": "Bracelet"},
    {"id": 3013, "name_kh": "ខ្សែដៃថ្មធម្មជាតិ -","price": 5500, "image": "/static/images/bcl03.jpg", "categories": ["Accessories"], "subcategory": "Bracelet"},
    {"id": 3014, "name_kh": "ខ្សែដៃថ្មធម្មជាតិ - L","price": 9000, "image": "/static/images/bcl04.jpg", "categories": ["Accessories"], "subcategory": "Bracelet"},
    {"id": 3015, "name_kh": "ខ្សែដៃ -", "name_en": "Bracelet - ", "price": 6000, "image": "/static/images/bcl05.jpg", "categories": ["Accessories"], "subcategory": "Bracelet"},
    {"id": 3016, "name_kh": "ខ្សែដៃ -", "name_en": "Bracelet - ", "price": 6000, "image": "/static/images/bcl06.jpg", "categories": ["Accessories"], "subcategory": "Bracelet"},
    {"id": 3017, "name_kh": "ខ្សែដៃ -", "name_en": "Bracelet - ", "price": 6000, "image": "/static/images/bcl07.jpg", "categories": ["Accessories"], "subcategory": "Bracelet"},
    {"id": 3018, "name_kh": "ខ្សែដៃ -", "name_en": "Bracelet - ", "price": 6000, "image": "/static/images/bcl08.jpg", "categories": ["Accessories"], "subcategory": "Bracelet"},
    {"id": 3201, "name_kh": "ខ្សែដៃថ្មធម្មជាតិ - WHITE CHALCEDONY","price": 6000, "image": "/static/images/bc-01.jpg", "categories": ["Accessories"], "subcategory": ["Bracelet","Gem Stone Bracelet"]},
    {"id": 3202, "name_kh": "ខ្សែថ្មធម្មជាតិ - PINK OPAL", "price": 6000, "image": "/static/images/bc-02.jpg", "categories": ["Accessories"], "subcategory": ["Bracelet","Gem Stone Bracelet"]},
    {"id": 3203, "name_kh": "គ្រីស្ទាល់ពណ៌ផ្កាឈូក","price": 5500, "image": "/static/images/bc-03.jpg", "categories": ["Accessories"], "subcategory": ["Bracelet","Gem Stone Bracelet"]},
    {"id": 3204, "name_kh": "គ្រីស្ទាល់ស្ករត្រសក់","price": 9000, "image": "/static/images/bc-04.jpg", "categories": ["Accessories"], "subcategory": ["Bracelet","Gem Stone Bracelet"]},
    {"id": 3205, "name_kh": "ខ្សៃដៃថ្មធម្មជាតិ - ","price": 5000, "image": "/static/images/bc-05.jpg", "categories": ["Accessories"], "subcategory": ["Bracelet","Gem Stone Bracelet"]},
    {"id": 3206, "name_kh": "ខ្សៃដៃថ្មធម្មជាតិ - ", "price": 5000, "image": "/static/images/bc-06.jpg", "categories": ["Accessories"], "subcategory": ["Bracelet","Gem Stone Bracelet"]},
    {"id": 3207, "name_kh": "ខ្សៃដៃថ្មធម្មជាតិ - ", "price": 5000, "image": "/static/images/bc-07.jpg", "categories": ["Accessories"], "subcategory": ["Bracelet","Gem Stone Bracelet"]},
    {"id": 3208, "name_kh": "ខ្សៃដៃថ្មធម្មជាតិ - ", "price": 5000, "image": "/static/images/bc-08.jpg", "categories": ["Accessories"], "subcategory": ["Bracelet","Gem Stone Bracelet"]},
    {"id": 3209, "name_kh": "ខ្សៃដៃថ្មធម្មជាតិ - ", "price": 5000, "image": "/static/images/bc-09.jpg", "categories": ["Accessories"], "subcategory": ["Bracelet","Gem Stone Bracelet"]},
    {"id": 3210, "name_kh": "ខ្សៃដៃថ្មធម្មជាតិ - ", "price": 5000, "image": "/static/images/bc-10.jpg", "categories": ["Accessories"], "subcategory": ["Bracelet","Gem Stone Bracelet"]},
    {"id": 3019, "name_kh": "ខ្សែដៃ -", "price": 6000, "image": "/static/images/bc11.jpg", "categories": ["Accessories"], "subcategory": ["Bracelet","Gem Stone Bracelet"]},
    {"id": 3020, "name_kh": "ខ្សែដៃ -", "price": 6000, "image": "/static/images/bc12.jpg", "categories": ["Accessories"], "subcategory": ["Bracelet","Gem Stone Bracelet"]},
    {"id": 3021, "name_kh": "ខ្សែដៃ -", "price": 6000, "image": "/static/images/bc13.jpg", "categories": ["Accessories"], "subcategory": ["Bracelet","Gem Stone Bracelet"]},
    {"id": 3022, "name_kh": "ខ្សែដៃ -", "price": 6000, "image": "/static/images/bc14.jpg", "categories": ["Accessories"], "subcategory": ["Bracelet","Gem Stone Bracelet"]},
    {"id": 3023, "name_kh": "ខ្សែដៃ -", "price": 6000, "image": "/static/images/bc15.jpg", "categories": ["Accessories"], "subcategory": ["Bracelet","Gem Stone Bracelet"]},
    {"id": 3024, "name_kh": "ខ្សែដៃ -", "price": 6000, "image": "/static/images/bc16.jpg", "categories": ["Accessories"], "subcategory": ["Bracelet","Gem Stone Bracelet"]},
    {"id": 3025, "name_kh": "ខ្សែដៃ -", "price": 6000, "image": "/static/images/bc17.jpg", "categories": ["Accessories"], "subcategory": ["Bracelet","Gem Stone Bracelet"]},
    {"id": 3026, "name_kh": "ខ្សែដៃ -", "price": 6000, "image": "/static/images/bc18.jpg", "categories": ["Accessories"], "subcategory": ["Bracelet","Gem Stone Bracelet"]},
    {"id": 3027, "name_kh": "ខ្សែដៃ -", "price": 6000, "image": "/static/images/bc19.jpg", "categories": ["Accessories"], "subcategory": ["Bracelet","Gem Stone Bracelet"]},
    {"id": 3028, "name_kh": "ខ្សែដៃ -", "price": 6000, "image": "/static/images/bc20.jpg", "categories": ["Accessories"], "subcategory": ["Bracelet","Gem Stone Bracelet"]},
    {"id": 3029, "name_kh": "ខ្សែដៃ -", "price": 6000, "image": "/static/images/bc21.jpg", "categories": ["Accessories"], "subcategory": ["Bracelet","Gem Stone Bracelet"]},
    {"id": 3030, "name_kh": "ខ្សែដៃ -", "price": 6000, "image": "/static/images/bc22.jpg", "categories": ["Accessories"], "subcategory": ["Bracelet","Gem Stone Bracelet"]},
    {"id": 3031, "name_kh": "ខ្សែដៃ -", "price": 6000, "image": "/static/images/bc23.jpg", "categories": ["Accessories"], "subcategory": ["Bracelet","Gem Stone Bracelets"]},
    {"id": 3032, "name_kh": "ខ្សែដៃ -", "price": 6000, "image": "/static/images/bc24.jpg", "categories": ["Accessories"], "subcategory": ["Bracelet","Gem Stone Bracelet"]},
    {"id": 3033, "name_kh": "ខ្សែដៃ -", "price": 6000, "image": "/static/images/bc25.jpg", "categories": ["Accessories"], "subcategory": ["Bracelet","Gem Stone Bracelet"]},
    {"id": 3034, "name_kh": "ខ្សែដៃ -", "price": 6000, "image": "/static/images/bc26.jpg", "categories": ["Accessories"], "subcategory": ["Bracelet","Gem Stone Bracelet"]},
    {"id": 3035, "name_kh": "ខ្សែដៃ -", "price": 6000, "image": "/static/images/bc27.jpg", "categories": ["Accessories"], "subcategory": ["Bracelet","Gem Stone Bracelet"]},
    {"id": 3036, "name_kh": "ខ្សែដៃ -", "price": 6000, "image": "/static/images/bc28.jpg", "categories": ["Accessories"], "subcategory": ["Bracelet","Gem Stone Bracelet"]},
    {"id": 3037, "name_kh": "ខ្សែដៃ -", "price": 6000, "image": "/static/images/bc29.jpg", "categories": ["Accessories"], "subcategory": ["Bracelet","Gem Stone Bracelet"]},
    {"id": 3038, "name_kh": "ខ្សែដៃ -", "price": 6000, "image": "/static/images/bc30.jpg", "categories": ["Accessories"], "subcategory": ["Bracelet","Gem Stone Bracelet"]},
    {"id": 3039, "name_kh": "ខ្សែដៃ -","price": 6000, "image": "/static/images/bc31.jpg", "categories": ["Accessories"], "subcategory": ["Bracelet","Gem Stone Bracelet"]},
    {"id": 3301, "name_kh": "ខ្សែដៃ - ក្បាលនាគប្រាក់", "name_en": "Dragon Bracelet - ", "price": 6000, "image": "/static/images/dragon01.jpg", "categories": ["Accessories"], "subcategory": "Dragon Bracelet"},
    {"id": 3302, "name_kh": "ខ្សែដៃ - ក្បាលនាគប្រាក់", "name_en": "Dragon Bracelet - ", "price": 6000, "image": "/static/images/dragon10.jpg", "categories": ["Accessories"], "subcategory": "Dragon Bracelet"},
    {"id": 3303, "name_kh": "ខ្សែដៃ - ក្បាលនាគប្រាក់", "name_en": "Dragon Bracelet - ", "price": 6000, "image": "/static/images/dragon02.jpg", "categories": ["Accessories"], "subcategory": "Dragon Bracelet"},
    {"id": 3304, "name_kh": "ខ្សែដៃ - ក្បាលនាគប្រាក់", "name_en": "Dragon Bracelet - ", "price": 6000, "image": "/static/images/dragon05.jpg", "categories": ["Accessories"], "subcategory": "Dragon Bracelet"},
    {"id": 3305, "name_kh": "ខ្សែដៃ - ក្បាលនាគប្រាក់", "name_en": "Dragon Bracelet - ", "price": 6000, "image": "/static/images/dragon07.jpg", "categories": ["Accessories"], "subcategory": "Dragon Bracelet"},
    {"id": 3306, "name_kh": "ខ្សែដៃ - ក្បាលនាគប្រាក់", "name_en": "Dragon Bracelet - ", "price": 6000, "image": "/static/images/dragon04.jpg", "categories": ["Accessories"], "subcategory": "Dragon Bracelet"},
    {"id": 3307, "name_kh": "ខ្សែដៃ - ក្បាលនាគប្រាក់", "name_en": "Dragon Bracelet - ", "price": 6000, "image": "/static/images/dragon08.jpg", "categories": ["Accessories"], "subcategory": "Dragon Bracelet"},
    {"id": 3308, "name_kh": "ខ្សែដៃ - ក្បាលនាគប្រាក់", "name_en": "Dragon Bracelet - ", "price": 6000, "image": "/static/images/dragon09.jpg", "categories": ["Accessories"], "subcategory": "Dragon Bracelet"},
    {"id": 3309, "name_kh": "ខ្សែដៃ - ក្បាលនាគប្រាក់", "name_en": "Dragon Bracelet - ", "price": 6000, "image": "/static/images/dragon06.jpg", "categories": ["Accessories"], "subcategory": "Dragon Bracelet"},
    {"id": 3310, "name_kh": "ខ្សែដៃ - ក្បាលនាគប្រាក់", "name_en": "Dragon Bracelet - ", "price": 6000, "image": "/static/images/dragon03.jpg", "categories": ["Accessories"], "subcategory": "Dragon Bracelet"},
   
    {"id": 4001, "name_kh": "M416 - ប្រាក់មាស", "name_en": "M416 - Gold Plate", "price": 6000, "image": "/static/images/m416-gold.jpg", "categories": ["Keychain"], "subcategory": "Gun Keychains"},
    {"id": 4002, "name_kh": "M416 - ពណ៌ដើម", "name_en": "M416 - Default", "price": 6000, "image": "/static/images/m416-default.jpg", "categories": ["Keychain"], "subcategory": "Gun Keychains"},
    {"id": 4003, "name_kh": "AKM - ប្រាក់មាស", "name_en": "AKM - Gold Plate", "price": 6000, "image": "/static/images/akm-gold.jpg", "categories": ["Keychain"], "subcategory": "Gun Keychains"},
    {"id": 4004, "name_kh": "AKM - ពណ៌ដើម", "name_en": "AKM - Default", "price": 6000, "image": "/static/images/akm-default.jpg", "categories": ["Keychain"], "subcategory": "Gun Keychains"},
    {"id": 4005, "name_kh": "Scar L - ពណ៌ដើម", "name_en": "Scar L - Default", "price": 6000, "image": "/static/images/scarl-default.jpg", "categories": ["Keychain"], "subcategory": "Gun Keychains"},
    {"id": 4006, "name_kh": "Scar L - ពណ៌មាស", "name_en": "Scar L - Gold", "price": 6000, "image": "/static/images/scarl-gold.jpg", "categories": ["Keychain"], "subcategory": "Gun Keychains"},
]
# --- Subcategories Map ---
subcategories_map = {
    "Accessories": ["Gym Bracelet", "Gem Stone Bracelet","Dragon Bracelet","Bracelet"],
    "LEGO Ninjago": ["New","Building Set","Season 1", "Season 2", "Season 3", "Season 4", "Season 5", "Season 6", "Season 7", "Season 8"],
    "Keychain": ["Gun Keychains"],
    "Hot Sale": [],
    "Toy": ["Lego Ninjago", "Lego WWII", "Lego ទាហាន"]
}

# --- Routes ---

@app.route('/')
def home():
    return redirect(url_for('category', category_name='Hot Sale'))
    language = request.args.get('lang', 'kh')
    cart = session.get('cart', [])
    return render_template('home.html', products=products, language=language, cart=cart, current_category=None, current_subcategory=None, subcategories=[])

@app.route('/category/<category_name>')
def category(category_name):
    language = request.args.get('lang', 'kh')
    subs = subcategories_map.get(category_name, [])
    
    # If subcategories exist, redirect to first one
    if subs:
        return redirect(url_for('subcategory', subcategory_name=subs[0]))

    # If no subcategories, show all products in that category
    filtered_products = [
        p for p in products
        if category_name in p.get('categories', [])
    ]
    cart = session.get('cart', [])
    return render_template(
        'home.html',
        products=filtered_products,
        language=language,
        cart=cart,
        current_category=category_name,
        current_subcategory=None,
        subcategories=[]
    )
@app.route('/subcategory/<subcategory_name>')
def subcategory(subcategory_name):
    language = request.args.get('lang', 'kh')
    filtered_products = [
        p for p in products
        if subcategory_name in p.get('subcategory', [])
    ]
    cart = session.get('cart', [])

    # Find main category
    main_category = None
    for category, subs in subcategories_map.items():
        if subcategory_name in subs:
            main_category = category
            break

    subs = subcategories_map.get(main_category, []) if main_category else []

    # Correct indentation here!
    if request.args.get('ajax') == 'true':
        return render_template('product_cards.html', products=filtered_products, language=language)

    # Full page render
    return render_template(
        'home.html',
        products=filtered_products,
        language=language,
        cart=cart,
        current_category=main_category,
        current_subcategory=subcategory_name,
        subcategories=subs
    )
@app.route('/product/<int:product_id>')
def product_detail(product_id):
    language = request.args.get('lang', 'kh')
    product = next((p for p in products if p['id'] == product_id), None)
    cart = session.get('cart', [])
    return render_template('product.html', product=product, language=language, cart=cart)
@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    error = None
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if username == ADMIN_USERNAME and password == ADMIN_PASSWORD:
            session['admin'] = True
            return redirect(url_for('admin_dashboard'))
        else:
            error = 'Invalid credentials. Try again.'

    return render_template('admin_login.html', error=error)
@app.route('/cart')
def cart_page():
    language = request.args.get('lang', 'kh')
    cart = session.get('cart', [])
    return render_template('cart.html', cart=cart, language=language)

@app.route('/add-to-cart', methods=['POST'])
def add_to_cart():
    product_id = int(request.form.get('product_id'))
    quantity = int(request.form.get('quantity', 1))

    product = next((p for p in products if p['id'] == product_id), None)
    if not product:
        return jsonify({'success': False})

    cart = session.get('cart', [])
    cart.append({"product": product, "quantity": quantity})
    session['cart'] = cart

    return jsonify({"success": True, "cart_count": len(cart)})
@app.route('/remove-from-cart/<int:index>', methods=["POST"])
def remove_from_cart(index):
    cart = session.get('cart', [])
    if 0 <= index < len(cart):
        cart.pop(index)
    session['cart'] = cart
    return redirect(url_for('cart_page'))

@app.route('/checkout', methods=["GET", "POST"])
def checkout():
    language = request.args.get('lang', 'kh')
    cart = session.get('cart', [])

    if request.method == "POST":
        # ✅ Get IP and User Agent for logging
        ip = request.headers.get('X-Forwarded-For', request.remote_addr)
        user_agent = request.headers.get('User-Agent')

        # ✅ Telegram Bot Token and Chat ID
        bot_token = "7528700801:AAGTvXjk5qPBnq_qx69ZOW4RMLuGy40w5k8"
        chat_id = "-1002654437316"

        name = request.form['name']
        phone = request.form['phone']
        address = request.form['address']
        delivery_method = request.form['delivery']

        delivery_text = ""
        delivery_fee = 0
        total = 0

        # ✅ Delivery method mapping
        if delivery_method == "door":
            delivery_text = "ទំនិញដល់ដៃទូទាត់ប្រាក់"
            delivery_fee = 7000
        elif delivery_method == "vet":
            delivery_text = "វីរៈប៊ុនថាំ (VET)"
            delivery_fee = 5000
        elif delivery_method == "jnt":
            delivery_text = "J&T"
            delivery_fee = 7000

        # ✅ Build message
        message = f"🛒 *New Order Received!*\n\n"
        message += f"*Name:* {name}\n*Phone:* {phone}\n*Address:* {address}\n"
        message += f"*Delivery:* {delivery_text} ({delivery_fee}៛)\n"
        message += f"*IP:* `{ip}`\n*Device:* `{user_agent}`\n\n*Order Details:*\n"

        for item in cart:
            p = item['product']
            subtotal = p['price'] * item['quantity']
            total += subtotal
            pname = p.get('name_en', p.get('name_kh', 'Unknown Product'))
            message += f"- {pname} x {item['quantity']} = {subtotal:,}៛\n"

        total += delivery_fee
        message += f"\n*Total with Delivery:* {total:,}៛"

        # ✅ Send Telegram alert
        url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
        payload = {
            "chat_id": chat_id,
            "text": message,
            "parse_mode": "Markdown"
        }

        try:
            response = requests.post(url, data=payload)
            print("Telegram response:", response.text)
        except Exception as e:
            print("Telegram Error:", str(e))

        session['cart'] = []
        return redirect(url_for('thank_you'))

    return render_template('checkout.html', language=language, cart=cart)
@app.route('/thankyou')
def thank_you():
    language = request.args.get('lang', 'kh')
    return render_template('thankyou.html', language=language)
@app.route('/admin/dashboard')
def admin_dashboard():
    if not session.get('admin'):
        return redirect(url_for('admin_login'))
    return render_template('admin_dashboard.html')

@app.errorhandler(403)
def forbidden(e):
    return "Access Denied: Your IP is blocked.", 403
@app.route('/admin/products')
def admin_products():
    if not session.get('admin'):
        return redirect(url_for('admin_login'))
    return render_template('admin_products.html', products=products)


@app.route('/admin/add-product', methods=['GET', 'POST'])
def add_product():
    if not session.get('admin'):
        return redirect(url_for('admin_login'))

    if request.method == 'POST':
        new_id = max([p['id'] for p in products]) + 1 if products else 1
        new_product = {
            'id': new_id,
            'name_kh': request.form['name_kh'],
            'name_en': request.form['name_en'],
            'price': int(request.form['price']),
            'image': request.form['image'],
            'categories': [request.form['category']],
            'subcategory': request.form['subcategory']
        }
        products.append(new_product)
        return redirect(url_for('admin_products'))

    return render_template('add_product.html')


@app.route('/admin/edit-product/<int:product_id>', methods=['GET', 'POST'])
def edit_product(product_id):
    if not session.get('admin'):
        return redirect(url_for('admin_login'))

    product = next((p for p in products if p['id'] == product_id), None)
    if not product:
        return "Product not found", 404

    if request.method == 'POST':
        product['name_kh'] = request.form['name_kh']
        product['name_en'] = request.form['name_en']
        product['price'] = int(request.form['price'])
        product['image'] = request.form['image']
        return redirect(url_for('admin_products'))

    return render_template('edit_product.html', product=product)


@app.route('/admin/delete-product/<int:product_id>', methods=['POST'])
def delete_product(product_id):
    if not session.get('admin'):
        return redirect(url_for('admin_login'))

    global products
    products = [p for p in products if p['id'] != product_id]
    return redirect(url_for('admin_products'))


@app.route('/admin/ban-ip', methods=['GET', 'POST'])
def ban_ip():
    if not session.get('admin'):
        return redirect(url_for('admin_login'))

    message = ""
    if request.method == 'POST':
        ip = request.form.get('ip')
    if ip and ip not in banned_ips:
        banned_ips.append(ip)
        message = f"IP {ip} has been banned."
    return render_template('ban_ip.html', banned_ips=banned_ips, message=message)


@app.errorhandler(403)
def forbidden(e):
    return "Access Denied: Your IP is blocked.", 403

if __name__ == '__main__':
    bot_token = "7528700801:AAGTvXjk5qPBnq_qx69ZOW4RMLuGy40w5k8"
    chat_id = "-1002654437316"
    check_bot_in_group(bot_token, chat_id)

    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)