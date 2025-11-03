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
    {"id": 1, "name_kh": "#OP01 One Piece - Sakazuki","price": 7500, "image": "/static/images/op01.jpg", "categories": ["LEGO Anime", "Toy"], "subcategory": ["One Piece"],"stock": 1,"discount":0 },
    {"id": 2, "name_kh": "#OP02 One Piece - Portgas D Ace","price": 6500, "image": "/static/images/op02.jpg", "categories": ["LEGO Anime", "Toy"], "subcategory": ["One Piece"],"stock": 1,"discount":0 },
    {"id": 3, "name_kh": "#OP03 One Piece - Marco","price": 7500, "image": "/static/images/op03.jpg", "categories": ["LEGO Anime", "Toy"], "subcategory": ["One Piece"],"stock": 1},
    {"id": 4, "name_kh": "#OP04 One Piece - Edward Newgate","price": 7500, "image": "/static/images/op04.jpg", "categories": ["LEGO Anime", "Toy"], "subcategory": ["One Piece"],"stock": 1,"discount":0 },
    {"id": 5, "name_kh": "#OP05 One Piece - Marshall D Teach","price": 7500, "image": "/static/images/op05.jpg", "categories": ["LEGO Anime", "Toy"], "subcategory": ["One Piece"],"stock": 1},
    {"id": 6, "name_kh": "#OP06 One Piece - Shanks","price": 7000, "image": "/static/images/op06.jpg", "categories": ["LEGO Anime", "Toy"], "subcategory": ["One Piece"],"stock": 1},
    {"id": 7, "name_kh": "#OP07 One Piece - Monkey D Luffy","price": 6000, "image": "/static/images/op07.jpg", "categories": ["LEGO Anime", "Toy"], "subcategory": ["One Piece"],"stock": 1},
    {"id": 8, "name_kh": "#OP08 One Piece - Monkey D Garp","price": 7500, "image": "/static/images/op08.jpg", "categories": ["LEGO Anime", "Toy"], "subcategory": ["One Piece"],"stock": 1,"discount":0 },
    {"id": 11, "name_kh": "#OP09 One Piece - Monkey D Luffy","price": 7000, "image": "/static/images/op11.jpg", "categories": ["LEGO Anime", "Toy"], "subcategory": ["One Piece"],"stock": 1},
    {"id": 12, "name_kh": "#OP10 One Piece - Sabo","price": 7500, "image": "/static/images/op12.jpg", "categories": ["LEGO Anime", "Toy"], "subcategory": ["One Piece"],"stock": 1},
    {"id": 13, "name_kh": "#OP11 One Piece - Portgas D Ace","price": 6500, "image": "/static/images/op13.jpg", "categories": ["LEGO Anime", "Toy"], "subcategory": ["One Piece"],"stock": 1},
    {"id": 14, "name_kh": "#OP12 One Piece - Edward Newgate","price": 7500, "image": "/static/images/op14.jpg", "categories": ["LEGO Anime", "Toy"], "subcategory": ["One Piece"],"stock": 1},
    {"id": 15, "name_kh": "#OP13 One Piece - Trafalgar D Water Law","price": 7500, "image": "/static/images/op15.jpg", "categories": ["LEGO Anime", "Toy"], "subcategory": ["One Piece"],"stock": 1},
    {"id": 16, "name_kh": "#OP14 One Piece - Portgas D Ace","price": 6000, "image": "/static/images/op16.jpg", "categories": ["LEGO Anime", "Toy"], "subcategory": ["One Piece"],"stock": 1},
    {"id": 17, "name_kh": "#OP15 One Piece - Roronoa Zoro","price": 7000, "image": "/static/images/op17.jpg", "categories": ["LEGO Anime", "Toy"], "subcategory": ["One Piece"],"stock": 1},
    {"id": 18, "name_kh": "#OP16 One Piece - Sengoku","price": 7500, "image": "/static/images/op18.jpg", "categories": ["LEGO Anime", "Toy"], "subcategory": ["One Piece"],"stock": 1},
    {"id": 21, "name_kh": "#OP21 One Piece - Monkey D Luffy","price": 8000, "image": "/static/images/op21.jpg", "categories": ["LEGO Anime", "Toy"], "subcategory": ["One Piece"],"stock": 1},
    {"id": 22, "name_kh": "#OP22 One Piece - Monkey D Luffy","price": 8000, "image": "/static/images/op22.jpg", "categories": ["LEGO Anime", "Toy"], "subcategory": ["One Piece"],"stock": 1},
    {"id": 23, "name_kh": "#OP23 One Piece - Monkey D Luffy","price": 8000, "image": "/static/images/op23.jpg", "categories": ["LEGO Anime", "Toy"], "subcategory": ["One Piece"],"stock": 1},
    {"id": 24, "name_kh": "#OP24 One Piece - Monkey D Luffy","price": 8000, "image": "/static/images/op24.jpg", "categories": ["LEGO Anime", "Toy"], "subcategory": ["One Piece"],"stock": 1},
    {"id": 25, "name_kh": "#OP25 One Piece - Roronoa Zoro","price": 8000, "image": "/static/images/op25.jpg", "categories": ["LEGO Anime", "Toy"], "subcategory": ["One Piece"],"stock": 1},
    {"id": 26, "name_kh": "#OP26 One Piece - Roronoa Zoro","price": 8000, "image": "/static/images/op26.jpg", "categories": ["LEGO Anime", "Toy"], "subcategory": ["One Piece"],"stock": 1},
    {"id": 27, "name_kh": "#OP27 One Piece - Roronoa Zoro","price": 8000, "image": "/static/images/op27.jpg", "categories": ["LEGO Anime", "Toy"], "subcategory": ["One Piece"],"stock": 1},
    {"id": 28, "name_kh": "#OP28 One Piece - Roronoa Zoro","price": 8000, "image": "/static/images/op28.jpg", "categories": ["LEGO Anime", "Toy"], "subcategory": ["One Piece"],"stock": 1},

    {"id": 101, "name_kh": "NINJAGO Season 1 - DX Suit","price": 30000, "image": "/static/images/njoss1dx.jpg", "categories": ["LEGO Ninjago", "Toy"], "subcategory": ["Lego Ninjago","Season 1"],"stock": 1},
    {"id": 102, "name_kh": "NINJAGO Season 1 - KAI (DX)","price": 5000, "image": "/static/images/njoss1dxkai.jpg", "categories": ["LEGO Ninjago", "Toy"], "subcategory": ["Lego Ninjago","Season 1"],"stock": 1},
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

    {"id": 201, "name_kh": "NINJAGO Season 2 - Kimono Suit","price": 36000, "image": "/static/images/njoss2kimono.jpg", "categories": ["LEGO Ninjago", "Toy"], "subcategory": ["Lego Ninjago","Season 2"],"stock": 1},
    {"id": 202, "name_kh": "NINJAGO Season 2 - KAI (Kimono)","price": 6000, "image": "/static/images/njoss2kimonokai.jpg", "categories": ["LEGO Ninjago", "Toy"], "subcategory": ["Lego Ninjago","Season 2"],"stock": 1},
    {"id": 203, "name_kh": "NINJAGO Season 2 - ZANE (Kimono)","price": 6000, "image": "/static/images/njoss2kimonozane.jpg", "categories": ["LEGO Ninjago", "Toy"], "subcategory": ["Lego Ninjago","Season 2"],"stock": 1},
    {"id": 204, "name_kh": "NINJAGO Season 2 - JAY (Kimono)","price": 6000, "image": "/static/images/njoss2kimonojay.jpg", "categories": ["LEGO Ninjago", "Toy"], "subcategory": ["Lego Ninjago","Season 2"],"stock": 1},
    {"id": 205, "name_kh": "NINJAGO Season 2 - COLE (Kimono)","price": 6000, "image": "/static/images/njoss2kimonocole.jpg", "categories": ["LEGO Ninjago", "Toy"], "subcategory": ["Lego Ninjago","Season 2"],"stock": 1},
    {"id": 206, "name_kh": "NINJAGO Season 2 - LLOYD  (Kimono)","price": 6000, "image": "/static/images/njoss2kimonolloyd.jpg", "categories": ["LEGO Ninjago", "Toy"], "subcategory": ["Lego Ninjago","Season 2"],"stock": 1},
    {"id": 207, "name_kh": "NINJAGO Season 2 - GOLDEN LLOYD (Kimono)","price": 6000, "image": "/static/images/njoss2kimonogoldlloyd.jpg", "categories": ["LEGO Ninjago", "Toy"], "subcategory": ["Lego Ninjago","Season 2"],"stock": 1},

    {"id": 211, "name_kh": "NINJAGO Season 2 - Pajamas ","price": 28000, "image": "/static/images/njoss2pajamas.jpg", "categories": ["LEGO Ninjago", "Toy"], "subcategory": ["Lego Ninjago","Season 2"],"stock": 1},
    {"id": 212, "name_kh": "NINJAGO Season 2 - KAI (Pajamas)","price": 7000, "image": "/static/images/njoss2pajamaskai.jpg", "categories": ["LEGO Ninjago", "Toy"], "subcategory": ["Lego Ninjago","Season 2"],"stock": 1},
    {"id": 213, "name_kh": "NINJAGO Season 2 - ZANE (Pajamas)","price": 7000, "image": "/static/images/njoss2pajamaszane.jpg", "categories": ["LEGO Ninjago", "Toy"], "subcategory": ["Lego Ninjago","Season 2"],"stock": 1},
    {"id": 214, "name_kh": "NINJAGO Season 2 - JAY (Pajamas)","price": 7000, "image": "/static/images/njoss2pajamasjay.jpg", "categories": ["LEGO Ninjago", "Toy"], "subcategory": ["Lego Ninjago","Season 2"],"stock": 1},
    {"id": 215, "name_kh": "NINJAGO Season 2 - Cole (Pajamas)","price": 7000, "image": "/static/images/njoss2pajamascole.jpg", "categories": ["LEGO Ninjago", "Toy"], "subcategory": ["Lego Ninjago","Season 2"],"stock": 1},

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
    {"id": 524, "name_kh": "NINJAGO Season 5 - JAY (Future)","price": 6500, "image": "/static/images/njoss5futurejay.jpg", "categories": ["LEGO Ninjago", "Toy"], "subcategory": ["Lego Ninjago","Season 5"],"stock": 1},
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

    {"id": 611, "name_kh": "NINJAGO Season 6 - Honor Robes","price": 24000, "image": "/static/images/njoss6honor.jpg", "categories": ["LEGO Ninjago", "Toy"], "subcategory": ["Lego Ninjago","Season 6"],"stock": 1},
    {"id": 612, "name_kh": "NINJAGO Season 6 - KAI (Honor)","price": 4000, "image": "/static/images/njoss6honorkai.jpg", "categories": ["LEGO Ninjago", "Toy"], "subcategory": ["Lego Ninjago","Season 6"],"stock": 1},
    {"id": 613, "name_kh": "NINJAGO Season 6 - ZANE (Honor)","price": 4000, "image": "/static/images/njoss6honorzane.jpg", "categories": ["LEGO Ninjago", "Toy"], "subcategory": ["Lego Ninjago","Season 6"],"stock": 1},
    {"id": 614, "name_kh": "NINJAGO Season 6 - JAY (Honor)","price": 4000, "image": "/static/images/njoss6honorjay.jpg", "categories": ["LEGO Ninjago", "Toy"], "subcategory": ["Lego Ninjago","Season 6"],"stock": 1},
    {"id": 615, "name_kh": "NINJAGO Season 6 - COLE (Honor)","price": 4000, "image": "/static/images/njoss6honorcole.jpg", "categories": ["LEGO Ninjago", "Toy"], "subcategory": ["Lego Ninjago","Season 6"],"stock": 1},
    {"id": 616, "name_kh": "NINJAGO Season 6 - NYA (Honor) ","price": 4000, "image": "/static/images/njoss6honornya.jpg", "categories": ["LEGO Ninjago", "Toy"], "subcategory": ["Lego Ninjago","Season 6"],"stock": 1},
    {"id": 617, "name_kh": "NINJAGO Season 6 - LLOYD (Honor)","price": 4000, "image": "/static/images/njoss6honorlloyd.jpg", "categories": ["LEGO Ninjago", "Toy"], "subcategory": ["Lego Ninjago","Season 6"],"stock": 1},

    {"id": 701, "name_kh": "NINJAGO Season 7 - Fusion Armour","price": 24500, "image": "/static/images/njoss7fusion.jpg", "categories": ["LEGO Ninjago", "Toy"], "subcategory": ["Lego Ninjago","Season 7"],"stock": 1},
    {"id": 702, "name_kh": "NINJAGO Season 7 - KAI (Fusion)","price": 3500, "image": "/static/images/njoss7fusionkai.jpg", "categories": ["LEGO Ninjago", "Toy"], "subcategory": ["Lego Ninjago","Season 7"],"stock": 1},
    {"id": 703, "name_kh": "NINJAGO Season 7 - ZANE (Fusion)","price": 3500, "image": "/static/images/njoss7fusionzane.jpg", "categories": ["LEGO Ninjago", "Toy"], "subcategory": ["Lego Ninjago","Season 7"],"stock": 1},
    {"id": 704, "name_kh": "NINJAGO Season 7 - JAY (Fusion)","price": 3500, "image": "/static/images/njoss7fusionjay.jpg", "categories": ["LEGO Ninjago", "Toy"], "subcategory": ["Lego Ninjago","Season 7"],"stock": 1},
    {"id": 705, "name_kh": "NINJAGO Season 7 - COLE (Fusion)","price": 3500, "image": "/static/images/njoss7fusioncole.jpg", "categories": ["LEGO Ninjago", "Toy"], "subcategory": ["Lego Ninjago","Season 7"],"stock": 1},
    {"id": 706, "name_kh": "NINJAGO Season 7 - NYA (Fusion) ","price": 3500, "image": "/static/images/njoss7fusionnya.jpg", "categories": ["LEGO Ninjago", "Toy"], "subcategory": ["Lego Ninjago","Season 7"],"stock": 1},
    {"id": 707, "name_kh": "NINJAGO Season 7 - LLOYD (Fusion)","price": 3500, "image": "/static/images/njoss7fusionlloyd.jpg", "categories": ["LEGO Ninjago", "Toy"], "subcategory": ["Lego Ninjago","Season 7"],"stock": 1},
    {"id": 708, "name_kh": "NINJAGO Season 7 - Sensei Wu (Fusion)","price": 3500, "image": "/static/images/njoss7fusionsenseiwu.jpg", "categories": ["LEGO Ninjago", "Toy"], "subcategory": ["Lego Ninjago","Season 7"],"stock": 1},

    {"id": 801, "name_kh": "NINJAGO Season 8 - KAI (Resistance)","price": 3500, "image": "/static/images/njoss8resistancekai.jpg", "categories": ["LEGO Ninjago", "Toy"], "subcategory": ["Lego Ninjago","Season 8"],"stock": 1},
    {"id": 802, "name_kh": "NINJAGO Season 8 - ZANE (Resistance)","price": 3500, "image": "/static/images/njoss8resistancezane.jpg", "categories": ["LEGO Ninjago", "Toy"], "subcategory": ["Lego Ninjago","Season 8"],"stock": 1},
    {"id": 803, "name_kh": "NINJAGO Season 8 - JAY (Resistance)","price": 3500, "image": "/static/images/njoss8resistancejay.jpg", "categories": ["LEGO Ninjago", "Toy"], "subcategory": ["Lego Ninjago","Season 8"],"stock": 1},
    {"id": 804, "name_kh": "NINJAGO Season 8 - COLE (Resistance)","price": 3500, "image": "/static/images/njoss8resistancecole.jpg", "categories": ["LEGO Ninjago", "Toy"], "subcategory": ["Lego Ninjago","Season 8"],"stock": 1},
    {"id": 805, "name_kh": "NINJAGO Season 8 - NYA (Resistance)","price": 3500, "image": "/static/images/njoss8resistancenya.jpg", "categories": ["LEGO Ninjago", "Toy"], "subcategory": ["Lego Ninjago","Season 8"],"stock": 1},
    {"id": 806, "name_kh": "NINJAGO Season 8 - LLOYD (Resistance) ","price": 3500, "image": "/static/images/njoss8resistancelloyd.jpg", "categories": ["LEGO Ninjago", "Toy"], "subcategory": ["Lego Ninjago","Season 8"],"stock": 1},
    
    {"id": 901, "name_kh": "NINJAGO Season 9 - Hunted Robes","price": 24000, "image": "/static/images/njoss9hunted.jpg", "categories": ["LEGO Ninjago", "Toy"], "subcategory": ["Lego Ninjago","Season 9"],"stock": 1},
    {"id": 902, "name_kh": "NINJAGO Season 9 - KAI (Hunted)","price": 4000, "image": "/static/images/njoss9huntedkai.jpg", "categories": ["LEGO Ninjago", "Toy"], "subcategory": ["Lego Ninjago","Season 9"],"stock": 1},
    {"id": 903, "name_kh": "NINJAGO Season 9 - ZANE (Hunted)","price": 4000, "image": "/static/images/njoss9huntedzane.jpg", "categories": ["LEGO Ninjago", "Toy"], "subcategory": ["Lego Ninjago","Season 9"],"stock": 1},
    {"id": 904, "name_kh": "NINJAGO Season 9 - JAY (Hunted)","price": 4000, "image": "/static/images/njoss9huntedjay.jpg", "categories": ["LEGO Ninjago", "Toy"], "subcategory": ["Lego Ninjago","Season 9"],"stock": 1},
    {"id": 905, "name_kh": "NINJAGO Season 9 - COLE (Hunted)","price": 4000, "image": "/static/images/njoss9huntedcole.jpg", "categories": ["LEGO Ninjago", "Toy"], "subcategory": ["Lego Ninjago","Season 9"],"stock": 1},
    {"id": 906, "name_kh": "NINJAGO Season 9 - NYA (Hunted) ","price": 4000, "image": "/static/images/njoss9huntednya.jpg", "categories": ["LEGO Ninjago", "Toy"], "subcategory": ["Lego Ninjago","Season 9"],"stock": 1},
    {"id": 907, "name_kh": "NINJAGO Season 9 - LLOYD (Hunted)","price": 4000, "image": "/static/images/njoss9huntedlloyd.jpg", "categories": ["LEGO Ninjago", "Toy"], "subcategory": ["Lego Ninjago","Season 9"],"stock": 1},

    {"id": 1001, "name_kh": "NINJAGO Season 10 - Legacy Robes","price": 24000, "image": "/static/images/njoss10legacy.jpg", "categories": ["LEGO Ninjago", "Toy"], "subcategory": ["Lego Ninjago","Season 10"],"stock": 1},
    {"id": 1002, "name_kh": "NINJAGO Season 10 - KAI (Legacy)","price": 4000, "image": "/static/images/njoss10legacykai.jpg", "categories": ["LEGO Ninjago", "Toy"], "subcategory": ["Lego Ninjago","Season 10"],"stock": 1},
    {"id": 1003, "name_kh": "NINJAGO Season 10 - ZANE (Legacy)","price": 4000, "image": "/static/images/njoss10legacyzane.jpg", "categories": ["LEGO Ninjago", "Toy"], "subcategory": ["Lego Ninjago","Season 10"],"stock": 1},
    {"id": 1004, "name_kh": "NINJAGO Season 10 - JAY (Legacy)","price": 4000, "image": "/static/images/njoss10legacyjay.jpg", "categories": ["LEGO Ninjago", "Toy"], "subcategory": ["Lego Ninjago","Season 10"],"stock": 1},
    {"id": 1005, "name_kh": "NINJAGO Season 10 - COLE (Legacy)","price": 4000, "image": "/static/images/njoss10legacycole.jpg", "categories": ["LEGO Ninjago", "Toy"], "subcategory": ["Lego Ninjago","Season 10"],"stock": 1},
    {"id": 1006, "name_kh": "NINJAGO Season 10 - NYA (Legacy) ","price": 4000, "image": "/static/images/njoss10legacynya.jpg", "categories": ["LEGO Ninjago", "Toy"], "subcategory": ["Lego Ninjago","Season 10"],"stock": 1},
    {"id": 1007, "name_kh": "NINJAGO Season 10 - LLOYD (Legacy)","price": 4000, "image": "/static/images/njoss10legacylloyd.jpg", "categories": ["LEGO Ninjago", "Toy"], "subcategory": ["Lego Ninjago","Season 10"],"stock": 1},

    {"id": 1101, "name_kh": "NINJAGO Season 11 - Armor Robes","price": 24000, "image": "/static/images/njoss11armor.jpg", "categories": ["LEGO Ninjago", "Toy"], "subcategory": ["Lego Ninjago","Season 11"],"stock": 1},
    {"id": 1102, "name_kh": "NINJAGO Season 11 - KAI (Armor)","price": 4000, "image": "/static/images/njoss11armorkai.jpg", "categories": ["LEGO Ninjago", "Toy"], "subcategory": ["Lego Ninjago","Season 11"],"stock": 1},
    {"id": 1103, "name_kh": "NINJAGO Season 11 - ZANE (Armor)","price": 4000, "image": "/static/images/njoss11armorzane.jpg", "categories": ["LEGO Ninjago", "Toy"], "subcategory": ["Lego Ninjago","Season 11"],"stock": 1},
    {"id": 1104, "name_kh": "NINJAGO Season 11 - JAY (Armor)","price": 4000, "image": "/static/images/njoss11armorjay.jpg", "categories": ["LEGO Ninjago", "Toy"], "subcategory": ["Lego Ninjago","Season 11"],"stock": 1},
    {"id": 1105, "name_kh": "NINJAGO Season 11 - COLE (Armor)","price": 4000, "image": "/static/images/njoss11armorcole.jpg", "categories": ["LEGO Ninjago", "Toy"], "subcategory": ["Lego Ninjago","Season 11"],"stock": 1},
    {"id": 1106, "name_kh": "NINJAGO Season 11 - NYA (Armor) ","price": 4000, "image": "/static/images/njoss11armornya.jpg", "categories": ["LEGO Ninjago", "Toy"], "subcategory": ["Lego Ninjago","Season 11"],"stock": 1},
    {"id": 1107, "name_kh": "NINJAGO Season 11 - LLOYD (Armor)","price": 4000, "image": "/static/images/njoss11armorlloyd.jpg", "categories": ["LEGO Ninjago", "Toy"], "subcategory": ["Lego Ninjago","Season 11"],"stock": 1},

    {"id": 1111, "name_kh": "NINJAGO Season 11 - Forbidden Spinjitzu","price": 21000, "image": "/static/images/njoss11forbidden.jpg", "categories": ["LEGO Ninjago", "Toy"], "subcategory": ["Lego Ninjago","Season 11"],"stock": 1},
    {"id": 1112, "name_kh": "NINJAGO Season 11 - KAI (Forbidden)","price": 3500, "image": "/static/images/njoss11forbiddenkai.jpg", "categories": ["LEGO Ninjago", "Toy"], "subcategory": ["Lego Ninjago","Season 11"],"stock": 1},
    {"id": 1113, "name_kh": "NINJAGO Season 11 - ZANE (Forbidden)","price": 3500, "image": "/static/images/njoss11forbiddenzane.jpg", "categories": ["LEGO Ninjago", "Toy"], "subcategory": ["Lego Ninjago","Season 11"],"stock": 1},
    {"id": 1114, "name_kh": "NINJAGO Season 11 - JAY (Forbidden)","price": 3500, "image": "/static/images/njoss11forbiddenjay.jpg", "categories": ["LEGO Ninjago", "Toy"], "subcategory": ["Lego Ninjago","Season 11"],"stock": 1},
    {"id": 1115, "name_kh": "NINJAGO Season 11 - COLE (Forbidden)","price": 3500, "image": "/static/images/njoss11forbiddencole.jpg", "categories": ["LEGO Ninjago", "Toy"], "subcategory": ["Lego Ninjago","Season 11"],"stock": 1},
    {"id": 1116, "name_kh": "NINJAGO Season 11 - NYA (Forbidden) ","price": 3500, "image": "/static/images/njoss11forbiddennya.jpg", "categories": ["LEGO Ninjago", "Toy"], "subcategory": ["Lego Ninjago","Season 11"],"stock": 1},
    {"id": 1117, "name_kh": "NINJAGO Season 11 - LLOYD (Forbidden)","price": 3500, "image": "/static/images/njoss11forbiddenlloyd.jpg", "categories": ["LEGO Ninjago", "Toy"], "subcategory": ["Lego Ninjago","Season 11"],"stock": 1},

    {"id": 1201, "name_kh": "NINJAGO Season 12 - Digi Robes","price": 17500, "image": "/static/images/njoss12digi.jpg", "categories": ["LEGO Ninjago", "Toy"], "subcategory": ["Lego Ninjago","Season 12"],"stock": 1},
    {"id": 1202, "name_kh": "NINJAGO Season 12 - KAI (Digi)","price": 3500, "image": "/static/images/njoss12digikai.jpg", "categories": ["LEGO Ninjago", "Toy"], "subcategory": ["Lego Ninjago","Season 12"],"stock": 1},
    {"id": 1203, "name_kh": "NINJAGO Season 12 - ZANE (Digi)","price": 3500, "image": "/static/images/njoss12digizane.jpg", "categories": ["LEGO Ninjago", "Toy"], "subcategory": ["Lego Ninjago","Season 12"],"stock": 1},
    {"id": 1204, "name_kh": "NINJAGO Season 12 - JAY (Digi)","price": 3500, "image": "/static/images/njoss12digijay.jpg", "categories": ["LEGO Ninjago", "Toy"], "subcategory": ["Lego Ninjago","Season 12"],"stock": 1},
    {"id": 1205, "name_kh": "NINJAGO Season 12 - COLE (Digi)","price": 3500, "image": "/static/images/njoss12digicole.jpg", "categories": ["LEGO Ninjago", "Toy"], "subcategory": ["Lego Ninjago","Season 12"],"stock": 1},
    {"id": 1206, "name_kh": "NINJAGO Season 12 - NYA (Digi) ","price": 3500, "image": "/static/images/njoss12diginya.jpg", "categories": ["LEGO Ninjago", "Toy"], "subcategory": ["Lego Ninjago","Season 12"],"stock": 1},
    {"id": 1207, "name_kh": "NINJAGO Season 12 - LLOYD (Digi)","price": 3500, "image": "/static/images/njoss12digilloyd.jpg", "categories": ["LEGO Ninjago", "Toy"], "subcategory": ["Lego Ninjago","Season 12"],"stock": 1},

    {"id": 1211, "name_kh": "NINJAGO Season 12 - Avatar Outfits","price": 30000, "image": "/static/images/njoss12avatar.jpg", "categories": ["LEGO Ninjago", "Toy"], "subcategory": ["Lego Ninjago","Season 12"],"stock": 1},
    {"id": 1212, "name_kh": "NINJAGO Season 12 - KAI (Avatar)","price": 5000, "image": "/static/images/njoss12avatarkai.jpg", "categories": ["LEGO Ninjago", "Toy"], "subcategory": ["Lego Ninjago","Season 12"],"stock": 1},
    {"id": 1213, "name_kh": "NINJAGO Season 12 - ZANE (Avatar)","price": 5000, "image": "/static/images/njoss12avatarzane.jpg", "categories": ["LEGO Ninjago", "Toy"], "subcategory": ["Lego Ninjago","Season 12"],"stock": 1},
    {"id": 1214, "name_kh": "NINJAGO Season 12 - JAY (Avatar)","price": 5000, "image": "/static/images/njoss12avatarjay.jpg", "categories": ["LEGO Ninjago", "Toy"], "subcategory": ["Lego Ninjago","Season 12"],"stock": 1},
    {"id": 1215, "name_kh": "NINJAGO Season 12 - COLE (Avatar)","price": 5000, "image": "/static/images/njoss12avatarcole.jpg", "categories": ["LEGO Ninjago", "Toy"], "subcategory": ["Lego Ninjago","Season 12"],"stock": 1},
    {"id": 1216, "name_kh": "NINJAGO Season 12 - NYA (Avatar) ","price": 5000, "image": "/static/images/njoss12avatarnya.jpg", "categories": ["LEGO Ninjago", "Toy"], "subcategory": ["Lego Ninjago","Season 12"],"stock": 1},
    {"id": 1217, "name_kh": "NINJAGO Season 12 - LLOYD (Avatar)","price": 5000, "image": "/static/images/njoss12avatarlloyd.jpg", "categories": ["LEGO Ninjago", "Toy"], "subcategory": ["Lego Ninjago","Season 12"],"stock": 1},

    {"id": 1301, "name_kh": "NINJAGO Season 13 - Hero Armor","price": 27000, "image": "/static/images/njoss13hero.jpg", "categories": ["LEGO Ninjago", "Toy"], "subcategory": ["Lego Ninjago","Season 13"],"stock": 1},
    {"id": 1302, "name_kh": "NINJAGO Season 13 - KAI (Hero)","price": 4500, "image": "/static/images/njoss13herokai.jpg", "categories": ["LEGO Ninjago", "Toy"], "subcategory": ["Lego Ninjago","Season 13"],"stock": 1},
    {"id": 1303, "name_kh": "NINJAGO Season 13 - ZANE (Hero)","price": 4500, "image": "/static/images/njoss13herozane.jpg", "categories": ["LEGO Ninjago", "Toy"], "subcategory": ["Lego Ninjago","Season 13"],"stock": 1},
    {"id": 1304, "name_kh": "NINJAGO Season 13 - JAY (Hero)","price": 4500, "image": "/static/images/njoss13herojay.jpg", "categories": ["LEGO Ninjago", "Toy"], "subcategory": ["Lego Ninjago","Season 13"],"stock": 1},
    {"id": 1305, "name_kh": "NINJAGO Season 13 - COLE (Hero)","price": 4500, "image": "/static/images/njoss13herocole.jpg", "categories": ["LEGO Ninjago", "Toy"], "subcategory": ["Lego Ninjago","Season 13"],"stock": 1},
    {"id": 1306, "name_kh": "NINJAGO Season 13 - NYA (Hero) ","price": 4500, "image": "/static/images/njoss13heronya.jpg", "categories": ["LEGO Ninjago", "Toy"], "subcategory": ["Lego Ninjago","Season 13"],"stock": 1},
    {"id": 1307, "name_kh": "NINJAGO Season 13 - LLOYD (Hero)","price": 4500, "image": "/static/images/njoss13herolloyd.jpg", "categories": ["LEGO Ninjago", "Toy"], "subcategory": ["Lego Ninjago","Season 13"],"stock": 1},

    {"id": 1901, "name_kh": " Dragon Rising S1 - KAI (Merge Suits)","price": 5000, "image": "/static/images/njodrgss1mergekai.jpg", "categories": ["LEGO Ninjago", "Toy"], "subcategory": ["Lego Ninjago","Dragon Rising"],"stock": 1},
    {"id": 1902, "name_kh": " Dragon Rising S1 - ZANE (Merge Suits)","price": 5000, "image": "/static/images/njodrgss1mergezane.jpg", "categories": ["LEGO Ninjago", "Toy"], "subcategory": ["Lego Ninjago","Dragon Rising"],"stock": 1},
    {"id": 1903, "name_kh": " Dragon Rising S1 - JAY (Merge Suits)","price": 5000, "image": "/static/images/njodrgss1mergejay.jpg", "categories": ["LEGO Ninjago", "Toy"], "subcategory": ["Lego Ninjago","Dragon Rising"],"stock": 1},
    {"id": 1904, "name_kh": " Dragon Rising S1 - COLE (Merge Suits)","price": 5000, "image": "/static/images/njodrgss1mergecole.jpg", "categories": ["LEGO Ninjago", "Toy"], "subcategory": ["Lego Ninjago","Dragon Rising"],"stock": 1},
    {"id": 1905, "name_kh": " Dragon Rising S1 - NYA (Merge Suits)","price": 5000, "image": "/static/images/njodrgss1mergenya.jpg", "categories": ["LEGO Ninjago", "Toy"], "subcategory": ["Lego Ninjago","Dragon Rising"],"stock": 1},
    {"id": 1906, "name_kh": " Dragon Rising S1 - LLOYD (Merge Suits)","price": 5000, "image": "/static/images/njodrgss1mergelloyd.jpg", "categories": ["LEGO Ninjago", "Toy"], "subcategory": ["Lego Ninjago","Dragon Rising"],"stock": 1},
    {"id": 1907, "name_kh": " Dragon Rising S1 - ARIN (Merge Suits)","price": 5000, "image": "/static/images/njodrgss1mergearin.jpg", "categories": ["LEGO Ninjago", "Toy"], "subcategory": ["Lego Ninjago","Dragon Rising"],"stock": 1},
    {"id": 1908, "name_kh": " Dragon Rising S1 - SORA (Merge Suits)","price": 5000, "image": "/static/images/njodrgss1mergesora.jpg", "categories": ["LEGO Ninjago", "Toy"], "subcategory": ["Lego Ninjago","Dragon Rising"],"stock": 1},

    {"id": 1909, "name_kh": " Dragon Rising S2 - KAI (Source Tournament Suits)","price": 6000, "image": "/static/images/njodrgss2sourcekai.jpg", "categories": ["LEGO Ninjago", "Toy"], "subcategory": ["Lego Ninjago","Dragon Rising"],"stock": 1},
    {"id": 1910, "name_kh": " Dragon Rising S2 - ZANE (Source Tournament Suits)","price": 6000, "image": "/static/images/njodrgss2sourcezane.jpg", "categories": ["LEGO Ninjago", "Toy"], "subcategory": ["Lego Ninjago","Dragon Rising"],"stock": 1},
    {"id": 1911, "name_kh": " Dragon Rising S2 - COLE (Source Tournament Suits)","price": 6000, "image": "/static/images/njodrgss2sourcecole.jpg", "categories": ["LEGO Ninjago", "Toy"], "subcategory": ["Lego Ninjago","Dragon Rising"],"stock": 1},
    {"id": 1912, "name_kh": " Dragon Rising S2 - NYA (Source Tournament Suits)","price": 6000, "image": "/static/images/njodrgss2sourcenya.jpg", "categories": ["LEGO Ninjago", "Toy"], "subcategory": ["Lego Ninjago","Dragon Rising"],"stock": 1},
    {"id": 1913, "name_kh": " Dragon Rising S2 - LLOYD (Source Tournament Suits)","price": 6000, "image": "/static/images/njodrgss2sourcelloyd.jpg", "categories": ["LEGO Ninjago", "Toy"], "subcategory": ["Lego Ninjago","Dragon Rising"],"stock": 1},

    {"id": 1914, "name_kh": " Dragon Rising S2 - KAI (Mech Pilot Suits)","price": 4000, "image": "/static/images/njodrgss2mechkai.jpg", "categories": ["LEGO Ninjago", "Toy"], "subcategory": ["Lego Ninjago","Dragon Rising"],"stock": 1},
    {"id": 1915, "name_kh": " Dragon Rising S2 - ZANE (Mech Pilot Suits)","price": 4000, "image": "/static/images/njodrgss2mechzane.jpg", "categories": ["LEGO Ninjago", "Toy"], "subcategory": ["Lego Ninjago","Dragon Rising"],"stock": 1},
    {"id": 1916, "name_kh": " Dragon Rising S2 - JAY (Mech Pilot Suits)","price": 4000, "image": "/static/images/njodrgss2mechjay.jpg", "categories": ["LEGO Ninjago", "Toy"], "subcategory": ["Lego Ninjago","Dragon Rising"],"stock": 1},
    {"id": 1917, "name_kh": " Dragon Rising S2 - COLE (Mech Pilot Suits)","price": 4000, "image": "/static/images/njodrgss2mechcole.jpg", "categories": ["LEGO Ninjago", "Toy"], "subcategory": ["Lego Ninjago","Dragon Rising"],"stock": 1},
    {"id": 1918, "name_kh": " Dragon Rising S2 - NYA (Mech Pilot Suits)","price": 4000, "image": "/static/images/njodrgss2mechnya.jpg", "categories": ["LEGO Ninjago", "Toy"], "subcategory": ["Lego Ninjago","Dragon Rising"],"stock": 1},
    {"id": 1919, "name_kh": " Dragon Rising S2 - LLOYD (Mech Pilot Suits)","price": 4000, "image": "/static/images/njodrgss2mechlloyd.jpg", "categories": ["LEGO Ninjago", "Toy"], "subcategory": ["Lego Ninjago","Dragon Rising"],"stock": 1},
    {"id": 1920, "name_kh": " Dragon Rising S2 - ARIN (Mech Pilot Suits)","price": 4000, "image": "/static/images/njodrgss2mecharin.jpg", "categories": ["LEGO Ninjago", "Toy"], "subcategory": ["Lego Ninjago","Dragon Rising"],"stock": 1},
    {"id": 1921, "name_kh": " Dragon Rising S2 - SENSEI WU (Mech Pilot Suits)","price": 4000, "image": "/static/images/njodrgss2mechsenseiwu.jpg", "categories": ["LEGO Ninjago", "Toy"], "subcategory": ["Lego Ninjago","Dragon Rising"],"stock": 1},
    {"id": 1921, "name_kh": " Dragon Rising S2 - EVIL JAY","price": 7000, "image": "/static/images/njodrgss2eviljay.jpg", "categories": ["LEGO Ninjago", "Toy"], "subcategory": ["Lego Ninjago","Dragon Rising"],"stock": 1},
    {"id": 1922, "name_kh": " Dragon Rising S3 - JAY ROGUE","price": 8000, "image": "/static/images/njodrgss3jayrogue.jpg", "categories": ["LEGO Ninjago", "Toy"], "subcategory": ["Lego Ninjago","Dragon Rising"],"stock": 1},
    {"id": 1923, "name_kh": " Dragon Rising S3 - MORRO","price": 9500, "image": "/static/images/njodrgss3morro.jpg", "categories": ["LEGO Ninjago", "Toy"], "subcategory": ["Lego Ninjago","Dragon Rising"],"stock": 1},

    {"id": 1924, "name_kh": " Dragon Rising S3 - NOKT","price": 9000, "image": "/static/images/ss3nokt.jpg", "categories": ["LEGO Ninjago", "Toy"], "subcategory": ["Lego Ninjago","Dragon Rising"],"stock": 1,"discount":30 },
    {"id": 1925, "name_kh": " Dragon Rising S3 - ROX","price": 9000, "image": "/static/images/ss3rox.jpg", "categories": ["LEGO Ninjago", "Toy"], "subcategory": ["Lego Ninjago","Dragon Rising"],"stock": 1,"discount":30 },
    {"id": 1926, "name_kh": " Dragon Rising S3 - DRIX","price": 9000, "image": "/static/images/ss3drix.jpg", "categories": ["LEGO Ninjago", "Toy"], "subcategory": ["Lego Ninjago","Dragon Rising"],"stock": 1,"discount":30 },
    {"id": 1927, "name_kh": " Dragon Rising S3 - ZARKT","price": 9000, "image": "/static/images/ss3zarkt.jpg", "categories": ["LEGO Ninjago", "Toy"], "subcategory": ["Lego Ninjago","Dragon Rising"],"stock": 1,"discount":30 },
    {"id": 1928, "name_kh": " Dragon Rising S3 - KUR","price": 9000, "image": "/static/images/ss3kur.jpg", "categories": ["LEGO Ninjago", "Toy"], "subcategory": ["Lego Ninjago","Dragon Rising"],"stock": 1,"discount":30 },

    {"id": 91101, "name_kh": "Zane's Set", "price": 68000, "image": "/static/images/nj01.jpg", "categories": ["LEGO Ninjago","Toy"], "subcategory": ["Lego Ninjago","Building Set"]},
    {"id": 91102, "name_kh": "Kai Merch", "price": 64000, "image": "/static/images/nj02.jpg", "categories": ["LEGO Ninjago", "Toy"], "subcategory": ["Lego Ninjago","Building Set"]},
    {"id": 91003, "name_kh": "cole Merch", "price": 140000, "image": "/static/images/nj03.jpg", "categories": ["LEGO Ninjago", "Toy"], "subcategory": ["Lego Ninjago","Building Set"]},
    {"id": 91004, "name_kh": "idk name ", "price": 88000, "image": "/static/images/nj04.jpg", "categories": ["LEGO Ninjago", "Toy"], "subcategory": ["Lego Ninjago","Building Set"]},
    {"id": 91005, "name_kh": "Zane's Set", "price": 132000, "image": "/static/images/nj05.jpg", "categories": ["LEGO Ninjago","Toy"], "subcategory": ["Lego Ninjago","Building Set"]},
    {"id": 91006, "name_kh": "Kai Merch", "price": 132000, "image": "/static/images/nj06.jpg", "categories": ["LEGO Ninjago", "Toy"], "subcategory": ["Lego Ninjago","Building Set"]},
    {"id": 91007, "name_kh": "cole Merch", "price": 43000, "image": "/static/images/nj07.jpg", "categories": ["LEGO Ninjago", "Toy"], "subcategory": ["Lego Ninjago","Building Set"]},
    {"id": 91008, "name_kh": "idk name ", "price": 43000, "image": "/static/images/nj08.jpg", "categories": ["LEGO Ninjago", "Toy"], "subcategory": ["Lego Ninjago","Building Set"]},
    {"id": 91009, "name_kh": "Zane's Set", "price": 44000, "image": "/static/images/nj09.jpg", "categories": ["LEGO Ninjago","Toy"], "subcategory": ["Lego Ninjago","Building Set"]},
    {"id": 91010, "name_kh": "Kai Merch", "price": 46000, "image": "/static/images/nj10.jpg", "categories": ["LEGO Ninjago", "Toy"], "subcategory": ["Lego Ninjago","Building Set"]},
    {"id": 91011, "name_kh": "cole Merch", "price": 28000, "image": "/static/images/nj11.jpg", "categories": ["LEGO Ninjago", "Toy"], "subcategory": ["Lego Ninjago","Building Set"]},
    {"id": 91012, "name_kh": "idk name ", "price": 46000, "image": "/static/images/nj12.jpg", "categories": ["LEGO Ninjago", "Toy"], "subcategory": ["Lego Ninjago","Building Set"]},
    {"id": 91013, "name_kh": "Kai Merch", "price": 49000, "image": "/static/images/nj13.jpg", "categories": ["LEGO Ninjago", "Toy"], "subcategory": ["Lego Ninjago","Building Set"]},
    {"id": 91014, "name_kh": "cole Merch", "price": 45000, "image": "/static/images/nj14.jpg", "categories": ["LEGO Ninjago", "Toy"], "subcategory": ["Lego Ninjago","Building Set"]},
    {"id": 91015, "name_kh": "idk name ", "price": 66000, "image": "/static/images/nj15.jpg", "categories": ["LEGO Ninjago", "Toy"], "subcategory": ["Lego Ninjago","Building Set"]},
    {"id": 91016, "name_kh": "Kai Merch", "price": 46000, "image": "/static/images/nj16.jpg", "categories": ["LEGO Ninjago", "Toy"], "subcategory": ["Lego Ninjago","Building Set"]},
    {"id": 91017, "name_kh": "cole Merch", "price": 38000, "image": "/static/images/nj17.jpg", "categories": ["LEGO Ninjago", "Toy"], "subcategory": ["Lego Ninjago","Building Set"]},
    {"id": 91018, "name_kh": "idk name ", "price": 59000, "image": "/static/images/nj18.jpg", "categories": ["LEGO Ninjago", "Toy"], "subcategory": ["Lego Ninjago","Building Set"]},
    {"id": 91019, "name_kh": "Kai Merch", "price": 52000, "image": "/static/images/nj19.jpg", "categories": ["LEGO Ninjago", "Toy"], "subcategory": ["Lego Ninjago","Building Set"]},
    {"id": 91020, "name_kh": "cole Merch", "price": 5000, "image": "/static/images/nj20.jpg", "categories": ["LEGO Ninjago", "Toy"], "subcategory": ["Lego Ninjago","Building Set"]},
    {"id": 91021, "name_kh": "idk name ", "price": 5000, "image": "/static/images/nj21.jpg", "categories": ["LEGO Ninjago", "Toy"], "subcategory": ["Lego Ninjago","Building Set"]},

    {"id": 2001, "name_kh": "WWII - កាំភ្លើងធំ","price": 3500, "image": "/static/images/wwii-biggun.jpg", "categories": ["toy"], "subcategory": "Lego WWII","discount":0},
    {"id": 2002, "name_kh": "WWII - កាំភ្លើងធំ6គ្រឿង 02","price": 6000, "image": "/static/images/wwii-gun6x.jpg", "categories": ["toy"], "subcategory": "Lego WWII","discount":0},
    {"id": 2003, "name_kh": "WWII -  RPG","price": 500, "image": "/static/images/wwii-rpg.jpg", "categories": ["toy"], "subcategory": "Lego WWII","discount":20 },
    {"id": 2004, "name_kh": "WWII -  04","price": 1250, "image": "/static/images/wwii-04.jpg", "categories": ["toy"], "subcategory": "Lego WWII","discount":20 },
    {"id": 2005, "name_kh": "WWII ","price": 1250, "image": "/static/images/wwii-05.jpg", "categories": ["toy"], "subcategory": "Lego WWII","discount":20 },
    {"id": 2006, "name_kh": "WWII សព្វាវុធ 01", "price": 3000, "image": "/static/images/wwii-a.jpg", "categories": ["toy"], "subcategory": "Lego WWII","discount":50 },
    {"id": 2007, "name_kh": "WWII សព្វាវុធ 02", "price": 3000, "image": "/static/images/wwii-b.jpg", "categories": ["toy"], "subcategory": "Lego WWII","discount":50 },
    {"id": 2008, "name_kh": "WWII សព្វាវុធ 03", "price": 3000, "image": "/static/images/wwii-c.jpg", "categories": ["toy"], "subcategory": "Lego WWII","discount":50 },
    {"id": 2009, "name_kh": "WWII សព្វាវុធ 04", "price": 3000, "image": "/static/images/wwii-d.jpg", "categories": ["toy"], "subcategory": "Lego WWII","discount":50 },
    {"id": 2010, "name_kh": "WWII សព្វាវុធ 05", "price": 3000, "image": "/static/images/wwii-e.jpg", "categories": ["toy"], "subcategory": "Lego WWII","discount":50 },
    {"id": 2011, "name_kh": "WWII Germany 01","price": 1250, "image": "/static/images/wwii-01.jpg", "categories": ["toy"], "subcategory": "Lego WWII","discount":20 },
    {"id": 2012, "name_kh": "WWII Germany 02","price": 1250, "image": "/static/images/wwii-02.jpg", "categories": ["toy"], "subcategory": "Lego WWII","discount":20 },
    {"id": 2013, "name_kh": "WWII Germany 03","price": 1250, "image": "/static/images/wwii-03.jpg", "categories": ["toy"], "subcategory": "Lego WWII","discount":20 },
    {"id": 2014, "name_kh": "WWII Germany 04","price": 1250, "image": "/static/images/wwii-04.jpg", "categories": ["toy"], "subcategory": "Lego WWII","discount":20 },
    {"id": 2015, "name_kh": "WWII Germany 05","price": 1250, "image": "/static/images/wwii-05.jpg", "categories": ["toy"], "subcategory": "Lego WWII","discount":20 },
    {"id": 2016, "name_kh": "WWII Germany 06", "name_en": "WWII Germany 06", "price": 1250, "image": "/static/images/wwii-06.jpg", "categories": ["toy"], "subcategory": "Lego WWII","discount":20 },
    {"id": 2017, "name_kh": "WWII USA 01", "name_en": "WWII USA 01", "price": 1250, "image": "/static/images/wwii-07.jpg", "categories": ["toy"], "subcategory": "Lego WWII","discount":20 },
    {"id": 2018, "name_kh": "WWII USA 02", "name_en": "WWII USA 02", "price": 1250, "image": "/static/images/wwii-08.jpg", "categories": ["toy"], "subcategory": "Lego WWII","discount":20 },
    {"id": 2019, "name_kh": "WWII USA 03", "name_en": "WWII USA 03", "price": 1250, "image": "/static/images/wwii-09.jpg", "categories": ["toy"], "subcategory": "Lego WWII","discount":20 },
    {"id": 2020, "name_kh": "WWII USA 04", "name_en": "WWII USA 04", "price": 1250, "image": "/static/images/wwii-10.jpg", "categories": ["toy"], "subcategory": "Lego WWII","discount":20 },
    {"id": 2021, "name_kh": "WWII USA 05", "name_en": "WWII USA 05", "price": 1250, "image": "/static/images/wwii-11.jpg", "categories": ["toy"], "subcategory": "Lego WWII","discount":20 },
    {"id": 2022, "name_kh": "WWII SOVIET 01", "name_en": "WWII SOVIET 01", "price": 1250, "image": "/static/images/wwii-12.jpg", "categories": ["toy"], "subcategory": "Lego WWII","discount":20 },
    {"id": 2023, "name_kh": "WWII SOVIET 02", "name_en": "WWII SOVIET 02", "price": 1250, "image": "/static/images/wwii-13.jpg", "categories": ["toy"], "subcategory": "Lego WWII","discount":20 },
    {"id": 2024, "name_kh": "WWII SOVIET 03", "name_en": "WWII SOVIET 03", "price": 1250, "image": "/static/images/wwii-14.jpg", "categories": ["toy"], "subcategory": "Lego WWII","discount":20 },
    {"id": 2025, "name_kh": "WWII SOVIET 04", "name_en": "WWII SOVIET 04", "price": 1250, "image": "/static/images/wwii-15.jpg", "categories": ["toy"], "subcategory": "Lego WWII","discount":20 },
    {"id": 2026, "name_kh": "WWII SOVIET 05", "name_en": "WWII SOVIET 05", "price": 1250, "image": "/static/images/wwii-16.jpg", "categories": ["toy"], "subcategory": "Lego WWII","discount":20 },
    {"id": 2027, "name_kh": "WWII SOVIET 06", "name_en": "WWII SOVIET 06", "price": 1250, "image": "/static/images/wwii-17.jpg", "categories": ["toy"], "subcategory": "Lego WWII","discount":20 },
    {"id": 2028, "name_kh": "WWII SOVIET 07", "name_en": "WWII SOVIET 07", "price": 1250, "image": "/static/images/wwii-18.jpg", "categories": ["toy"], "subcategory": "Lego WWII","discount":20 },
    {"id": 2029, "name_kh": "WWII SOVIET 08", "name_en": "WWII SOVIET 08", "price": 1250, "image": "/static/images/wwii-19.jpg", "categories": ["toy"], "subcategory": "Lego WWII","discount":20 },
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
     {"id": 3401, "name_kh": "Charm","price": 5000, "image": "/static/images/k001.jpg", "categories": ["Italy Bracelet"], "subcategory": ["All","Football"],"discount":20 },
     {"id": 3402, "name_kh": "Charm","price": 5000, "image": "/static/images/k002.jpg", "categories": ["Italy Bracelet"], "subcategory": ["All","Football"],"discount":20 },
     {"id": 3403, "name_kh": "Charm","price": 5000, "image": "/static/images/k003.jpg", "categories": ["Italy Bracelet"], "subcategory": ["All","Football"],"discount":20 },
     {"id": 3404, "name_kh": "Charm","price": 5000, "image": "/static/images/k004.jpg", "categories": ["Italy Bracelet"], "subcategory": ["All","Football"],"discount":20 },
     {"id": 3405, "name_kh": "Charm","price": 5000, "image": "/static/images/k005.jpg", "categories": ["Italy Bracelet"], "subcategory": ["All","Football"],"discount":20 },
     {"id": 3406, "name_kh": "Charm","price": 5000, "image": "/static/images/k006.jpg", "categories": ["Italy Bracelet"], "subcategory": ["All","Football"],"discount":20 },
     {"id": 3407, "name_kh": "Charm","price": 5000, "image": "/static/images/k007.jpg", "categories": ["Italy Bracelet"], "subcategory": ["All","Football"],"discount":20 },
     {"id": 3408, "name_kh": "Charm","price": 5000, "image": "/static/images/k008.jpg", "categories": ["Italy Bracelet"], "subcategory": ["All","Football"],"discount":20 },
     {"id": 3409, "name_kh": "Charm","price": 5000, "image": "/static/images/k009.jpg", "categories": ["Italy Bracelet"], "subcategory": ["All","Football"],"discount":20 },
     {"id": 3410, "name_kh": "Charm","price": 5000, "image": "/static/images/k010.jpg", "categories": ["Italy Bracelet"], "subcategory": ["All","Football"],"discount":20 },
     {"id": 3411, "name_kh": "Charm","price": 5000, "image": "/static/images/k011.jpg", "categories": ["Italy Bracelet"], "subcategory": ["All","Football"],"discount":20 },
     
     {"id": 3501, "name_kh": "Charm","price": 5000, "image": "/static/images/k101.jpg", "categories": ["Italy Bracelet"], "subcategory": ["All","Football"],"discount":20 },
     {"id": 3502, "name_kh": "Charm","price": 5000, "image": "/static/images/k102.jpg", "categories": ["Italy Bracelet"], "subcategory": ["All","Football"],"discount":20 },
     {"id": 3503, "name_kh": "Charm","price": 5000, "image": "/static/images/k103.jpg", "categories": ["Italy Bracelet"], "subcategory": ["All","Football"],"discount":20 },
     {"id": 3504, "name_kh": "Charm","price": 5000, "image": "/static/images/k104.jpg", "categories": ["Italy Bracelet"], "subcategory": ["All","Football"],"discount":20 },
     {"id": 3505, "name_kh": "Charm","price": 5000, "image": "/static/images/k105.jpg", "categories": ["Italy Bracelet"], "subcategory": ["All","Football"],"discount":20 },
     {"id": 3506, "name_kh": "Charm","price": 5000, "image": "/static/images/k106.jpg", "categories": ["Italy Bracelet"], "subcategory": ["All","Football"],"discount":20 },
     {"id": 3507, "name_kh": "Charm","price": 5000, "image": "/static/images/k107.jpg", "categories": ["Italy Bracelet"], "subcategory": ["All","Football"],"discount":20 },
     {"id": 3508, "name_kh": "Charm","price": 5000, "image": "/static/images/k108.jpg", "categories": ["Italy Bracelet"], "subcategory": ["All","Football"],"discount":20 },
     {"id": 3509, "name_kh": "Charm","price": 5000, "image": "/static/images/k109.jpg", "categories": ["Italy Bracelet"], "subcategory": ["All","Football"],"discount":20 },
     {"id": 3510, "name_kh": "Charm","price": 5000, "image": "/static/images/k110.jpg", "categories": ["Italy Bracelet"], "subcategory": ["All","Football"],"discount":20 },
     {"id": 3511, "name_kh": "Charm","price": 5000, "image": "/static/images/k111.jpg", "categories": ["Italy Bracelet"], "subcategory": ["All","Football"],"discount":20 },
     {"id": 3512, "name_kh": "Charm","price": 5000, "image": "/static/images/k112.jpg", "categories": ["Italy Bracelet"], "subcategory": ["All","Football"],"discount":20 },
     {"id": 3513, "name_kh": "Charm","price": 5000, "image": "/static/images/k113.jpg", "categories": ["Italy Bracelet"], "subcategory": ["All","Football"],"discount":20 },
     {"id": 3514, "name_kh": "Charm","price": 5000, "image": "/static/images/k114.jpg", "categories": ["Italy Bracelet"], "subcategory": ["All","Football"],"discount":20 },
     {"id": 3515, "name_kh": "Charm","price": 5000, "image": "/static/images/k115.jpg", "categories": ["Italy Bracelet"], "subcategory": ["All","Football"],"discount":20 },
     {"id": 3516, "name_kh": "Charm","price": 5000, "image": "/static/images/k116.jpg", "categories": ["Italy Bracelet"], "subcategory": ["All","Football"],"discount":20 },
     {"id": 3517, "name_kh": "Charm","price": 5000, "image": "/static/images/k117.jpg", "categories": ["Italy Bracelet"], "subcategory": ["All","Football"],"discount":20 },
     {"id": 3518, "name_kh": "Charm","price": 5000, "image": "/static/images/k118.jpg", "categories": ["Italy Bracelet"], "subcategory": ["All","Football"],"discount":20 },
     {"id": 3519, "name_kh": "Charm","price": 5000, "image": "/static/images/k119.jpg", "categories": ["Italy Bracelet"], "subcategory": ["All","Football"],"discount":20 },
     {"id": 3520, "name_kh": "Charm","price": 5000, "image": "/static/images/k120.jpg", "categories": ["Italy Bracelet"], "subcategory": ["All","Football"],"discount":20 },
     {"id": 3521, "name_kh": "Charm","price": 5000, "image": "/static/images/k121.jpg", "categories": ["Italy Bracelet"], "subcategory": ["All","Football"],"discount":20 },
     {"id": 3522, "name_kh": "Charm","price": 5000, "image": "/static/images/k122.jpg", "categories": ["Italy Bracelet"], "subcategory": ["All","Football"],"discount":20 },
     {"id": 3523, "name_kh": "Charm","price": 5000, "image": "/static/images/k123.jpg", "categories": ["Italy Bracelet"], "subcategory": ["All","Football"],"discount":20 },
     {"id": 3524, "name_kh": "Charm","price": 5000, "image": "/static/images/k124.jpg", "categories": ["Italy Bracelet"], "subcategory": ["All","Football"],"discount":20 },
     {"id": 3601, "name_kh": "Charm","price": 5000, "image": "/static/images/k201.jpg", "categories": ["Italy Bracelet"], "subcategory": ["All","Football"],"discount":20 },
     {"id": 3602, "name_kh": "Charm","price": 5000, "image": "/static/images/k202.jpg", "categories": ["Italy Bracelet"], "subcategory": ["All","Flag"],"discount":20 },
     {"id": 3603, "name_kh": "Charm","price": 5000, "image": "/static/images/k203.jpg", "categories": ["Italy Bracelet"], "subcategory": ["All","Flag"],"discount":20 },
     {"id": 3604, "name_kh": "Charm","price": 5000, "image": "/static/images/k204.jpg", "categories": ["Italy Bracelet"], "subcategory": ["All","Flag"],"discount":20 },
     {"id": 3605, "name_kh": "Charm","price": 5000, "image": "/static/images/k205.jpg", "categories": ["Italy Bracelet"], "subcategory": ["All","Flag"],"discount":20 },
     {"id": 3606, "name_kh": "Charm","price": 5000, "image": "/static/images/k206.jpg", "categories": ["Italy Bracelet"], "subcategory": ["All","Flag"],"discount":20 },
     {"id": 3607, "name_kh": "Charm","price": 5000, "image": "/static/images/k207.jpg", "categories": ["Italy Bracelet"], "subcategory": ["All","Flag"],"discount":20 },
     {"id": 3608, "name_kh": "Charm","price": 5000, "image": "/static/images/k208.jpg", "categories": ["Italy Bracelet"], "subcategory": ["All","Flag"],"discount":20 },
     {"id": 3609, "name_kh": "Charm","price": 5000, "image": "/static/images/k209.jpg", "categories": ["Italy Bracelet"], "subcategory": ["All","Flag"],"discount":20 },
     {"id": 3610, "name_kh": "Charm","price": 5000, "image": "/static/images/k210.jpg", "categories": ["Italy Bracelet"], "subcategory": ["All","Flag"],"discount":20 },

    {"id": 4001, "name_kh": "M416 - ប្រាក់មាស", "name_en": "M416 - Gold Plate", "price": 6000, "image": "/static/images/m416-gold.jpg", "categories": ["Keychain"], "subcategory": "Gun Keychains"},
    {"id": 4002, "name_kh": "M416 - ពណ៌ដើម", "name_en": "M416 - Default", "price": 6000, "image": "/static/images/m416-default.jpg", "categories": ["Keychain"], "subcategory": "Gun Keychains"},
    {"id": 4003, "name_kh": "AKM - ប្រាក់មាស", "name_en": "AKM - Gold Plate", "price": 6000, "image": "/static/images/akm-gold.jpg", "categories": ["Keychain"], "subcategory": "Gun Keychains"},
    {"id": 4004, "name_kh": "AKM - ពណ៌ដើម", "name_en": "AKM - Default", "price": 6000, "image": "/static/images/akm-default.jpg", "categories": ["Keychain"], "subcategory": "Gun Keychains"},
    {"id": 4005, "name_kh": "Scar L - ពណ៌ដើម", "name_en": "Scar L - Default", "price": 6000, "image": "/static/images/scarl-default.jpg", "categories": ["Keychain"], "subcategory": "Gun Keychains"},
    {"id": 4006, "name_kh": "Scar L - ពណ៌មាស", "name_en": "Scar L - Gold", "price": 6000, "image": "/static/images/scarl-gold.jpg", "categories": ["Keychain"], "subcategory": "Gun Keychains"},
    {"id": 20001, "name_kh": "71049 - 1 RED BULL","price": 24000, "image": "/static/images/lego71049-01.jpg", "categories": ["LEGO", "Toy"], "subcategory": ["Formula 1"],"stock": 1,"discount":0 },
    {"id": 20002, "name_kh": "71049 - 2 MERCEDES","price": 24000, "image": "/static/images/lego71049-02.jpg", "categories": ["LEGO", "Toy"], "subcategory": ["Formula 1"],"stock": 1,"discount":0 },
    {"id": 20003, "name_kh": "71049 - 3 FERRARI","price": 24000, "image": "/static/images/lego71049-03.jpg", "categories": ["LEGO", "Toy"], "subcategory": ["Formula 1"],"stock": 1},
    {"id": 20004, "name_kh": "71049 - 4 MCLAREN","price": 24000, "image": "/static/images/lego71049-04.jpg", "categories": ["LEGO", "Toy"], "subcategory": ["Formula 1"],"stock": 1,"discount":0 },
    {"id": 20005, "name_kh": "71049 - 5 ASTON MARTIN","price": 24000, "image": "/static/images/lego71049-05.jpg", "categories": ["LEGO", "Toy"], "subcategory": ["Formula 1"],"stock": 1},
    {"id": 20006, "name_kh": "71049 - 6 ALPINE","price": 24000, "image": "/static/images/lego71049-06.jpg", "categories": ["LEGO", "Toy"], "subcategory": ["Formula 1"],"stock": 1},
    {"id": 20007, "name_kh": "71049 - 7 WILLIAMS","price": 24000, "image": "/static/images/lego71049-07.jpg", "categories": ["LEGO", "Toy"], "subcategory": ["Formula 1"],"stock": 1},
    {"id": 20008, "name_kh": "71049 - 8 VISA CASH APP","price": 24000, "image": "/static/images/lego71049-08.jpg", "categories": ["LEGO", "Toy"], "subcategory": ["Formula 1"],"stock": 1,"discount":0 },
    {"id": 20009, "name_kh": "71049 - 9 SAUBER","price": 24000, "image": "/static/images/lego71049-09.jpg", "categories": ["LEGO", "Toy"], "subcategory": ["Formula 1"],"stock": 1},
    {"id": 20010, "name_kh": "71049 - 10 HAAS","price": 24000, "image": "/static/images/lego71049-10.jpg", "categories": ["LEGO", "Toy"], "subcategory": ["Formula 1"],"stock": 1},
    {"id": 20011, "name_kh": "71049 - 11 F1 ACADEMY ","price": 24000, "image": "/static/images/lego71049-11.jpg", "categories": ["LEGO", "Toy"], "subcategory": ["Formula 1"],"stock": 1},
    {"id": 20012, "name_kh": "71049 - 12 GENERIC","price": 24000, "image": "/static/images/lego71049-12.jpg", "categories": ["LEGO", "Toy"], "subcategory": ["Formula 1"],"stock": 1,"discount":0 },


]
# --- Subcategories Map ---
subcategories_map = {
    "Accessories": ["Gym Bracelet", "Gem Stone Bracelet","Dragon Bracelet","Bracelet"],
    "LEGO Ninjago": ["Dragon Rising","Building Set","Season 1", "Season 2", "Season 3", "Season 4", "Season 5", "Season 6", "Season 7", "Season 8","Season 9","Season 10","Season 11","Season 12","Season 13",
                     "Season 14","Season 15"],
    "LEGO Anime": ["One Piece","Demon Slayer"],
    "Keychain": ["Gun Keychains"],
    "Hot Sale": [],
    "LEGO": ["Formula 1"],
    "Toy": ["Lego Ninjago", "One Piece","Lego WWII", "Lego ទាហាន"],
    "Italy Bracelet": ["All","Football","Gem","Flag","Chain"],
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
@app.route('/custom-bracelet')
def custom_bracelet():
    # Example charms to display
    charms = [
     {"id": 3401, "name_kh": "Charm","price": 5000, "image": "/static/images/k001.jpg", "categories": ["Italy Bracelet"], "subcategory": ["All","Football"],"discount":20 },
     {"id": 3402, "name_kh": "Charm","price": 5000, "image": "/static/images/k002.jpg", "categories": ["Italy Bracelet"], "subcategory": ["All","Football"],"discount":20 },
     {"id": 3403, "name_kh": "Charm","price": 5000, "image": "/static/images/k003.jpg", "categories": ["Italy Bracelet"], "subcategory": ["All","Football"],"discount":20 },
     {"id": 3404, "name_kh": "Charm","price": 5000, "image": "/static/images/k004.jpg", "categories": ["Italy Bracelet"], "subcategory": ["All","Football"],"discount":20 },
     {"id": 3405, "name_kh": "Charm","price": 5000, "image": "/static/images/k005.jpg", "categories": ["Italy Bracelet"], "subcategory": ["All","Football"],"discount":20 },
     {"id": 3406, "name_kh": "Charm","price": 5000, "image": "/static/images/k006.jpg", "categories": ["Italy Bracelet"], "subcategory": ["All","Football"],"discount":20 },
     {"id": 3407, "name_kh": "Charm","price": 5000, "image": "/static/images/k007.jpg", "categories": ["Italy Bracelet"], "subcategory": ["All","Football"],"discount":20 },
     {"id": 3408, "name_kh": "Charm","price": 5000, "image": "/static/images/k008.jpg", "categories": ["Italy Bracelet"], "subcategory": ["All","Football"],"discount":20 },
     {"id": 3409, "name_kh": "Charm","price": 5000, "image": "/static/images/k009.jpg", "categories": ["Italy Bracelet"], "subcategory": ["All","Football"],"discount":20 },
     {"id": 3410, "name_kh": "Charm","price": 5000, "image": "/static/images/k010.jpg", "categories": ["Italy Bracelet"], "subcategory": ["All","Football"],"discount":20 },
     {"id": 3411, "name_kh": "Charm","price": 5000, "image": "/static/images/k011.jpg", "categories": ["Italy Bracelet"], "subcategory": ["All","Football"],"discount":20 },
     
     {"id": 3501, "name_kh": "Charm","price": 5000, "image": "/static/images/k101.jpg", "categories": ["Italy Bracelet"], "subcategory": ["All","Football"],"discount":20 },
     {"id": 3502, "name_kh": "Charm","price": 5000, "image": "/static/images/k102.jpg", "categories": ["Italy Bracelet"], "subcategory": ["All","Football"],"discount":20 },
     {"id": 3503, "name_kh": "Charm","price": 5000, "image": "/static/images/k103.jpg", "categories": ["Italy Bracelet"], "subcategory": ["All","Football"],"discount":20 },
     {"id": 3504, "name_kh": "Charm","price": 5000, "image": "/static/images/k104.jpg", "categories": ["Italy Bracelet"], "subcategory": ["All","Football"],"discount":20 },
     {"id": 3505, "name_kh": "Charm","price": 5000, "image": "/static/images/k105.jpg", "categories": ["Italy Bracelet"], "subcategory": ["All","Football"],"discount":20 },
     {"id": 3506, "name_kh": "Charm","price": 5000, "image": "/static/images/k106.jpg", "categories": ["Italy Bracelet"], "subcategory": ["All","Football"],"discount":20 },
     {"id": 3507, "name_kh": "Charm","price": 5000, "image": "/static/images/k107.jpg", "categories": ["Italy Bracelet"], "subcategory": ["All","Football"],"discount":20 },
     {"id": 3508, "name_kh": "Charm","price": 5000, "image": "/static/images/k108.jpg", "categories": ["Italy Bracelet"], "subcategory": ["All","Football"],"discount":20 },
     {"id": 3509, "name_kh": "Charm","price": 5000, "image": "/static/images/k109.jpg", "categories": ["Italy Bracelet"], "subcategory": ["All","Football"],"discount":20 },
     {"id": 3510, "name_kh": "Charm","price": 5000, "image": "/static/images/k110.jpg", "categories": ["Italy Bracelet"], "subcategory": ["All","Football"],"discount":20 },
     {"id": 3511, "name_kh": "Charm","price": 5000, "image": "/static/images/k111.jpg", "categories": ["Italy Bracelet"], "subcategory": ["All","Football"],"discount":20 },
     {"id": 3512, "name_kh": "Charm","price": 5000, "image": "/static/images/k112.jpg", "categories": ["Italy Bracelet"], "subcategory": ["All","Football"],"discount":20 },
     {"id": 3513, "name_kh": "Charm","price": 5000, "image": "/static/images/k113.jpg", "categories": ["Italy Bracelet"], "subcategory": ["All","Football"],"discount":20 },
     {"id": 3514, "name_kh": "Charm","price": 5000, "image": "/static/images/k114.jpg", "categories": ["Italy Bracelet"], "subcategory": ["All","Football"],"discount":20 },
     {"id": 3515, "name_kh": "Charm","price": 5000, "image": "/static/images/k115.jpg", "categories": ["Italy Bracelet"], "subcategory": ["All","Football"],"discount":20 },
     {"id": 3516, "name_kh": "Charm","price": 5000, "image": "/static/images/k116.jpg", "categories": ["Italy Bracelet"], "subcategory": ["All","Football"],"discount":20 },
     {"id": 3517, "name_kh": "Charm","price": 5000, "image": "/static/images/k117.jpg", "categories": ["Italy Bracelet"], "subcategory": ["All","Football"],"discount":20 },
     {"id": 3518, "name_kh": "Charm","price": 5000, "image": "/static/images/k118.jpg", "categories": ["Italy Bracelet"], "subcategory": ["All","Football"],"discount":20 },
     {"id": 3519, "name_kh": "Charm","price": 5000, "image": "/static/images/k119.jpg", "categories": ["Italy Bracelet"], "subcategory": ["All","Football"],"discount":20 },
     {"id": 3520, "name_kh": "Charm","price": 5000, "image": "/static/images/k120.jpg", "categories": ["Italy Bracelet"], "subcategory": ["All","Football"],"discount":20 },
     {"id": 3521, "name_kh": "Charm","price": 5000, "image": "/static/images/k121.jpg", "categories": ["Italy Bracelet"], "subcategory": ["All","Football"],"discount":20 },
     {"id": 3522, "name_kh": "Charm","price": 5000, "image": "/static/images/k122.jpg", "categories": ["Italy Bracelet"], "subcategory": ["All","Football"],"discount":20 },
     {"id": 3523, "name_kh": "Charm","price": 5000, "image": "/static/images/k123.jpg", "categories": ["Italy Bracelet"], "subcategory": ["All","Football"],"discount":20 },
     {"id": 3524, "name_kh": "Charm","price": 5000, "image": "/static/images/k124.jpg", "categories": ["Italy Bracelet"], "subcategory": ["All","Football"],"discount":20 },
     {"id": 3601, "name_kh": "Charm","price": 5000, "image": "/static/images/k201.jpg", "categories": ["Italy Bracelet"], "subcategory": ["All","Football"],"discount":20 },
     {"id": 3602, "name_kh": "Charm","price": 5000, "image": "/static/images/k202.jpg", "categories": ["Italy Bracelet"], "subcategory": ["All","Flag"],"discount":20 },
     {"id": 3603, "name_kh": "Charm","price": 5000, "image": "/static/images/k203.jpg", "categories": ["Italy Bracelet"], "subcategory": ["All","Flag"],"discount":20 },
     {"id": 3604, "name_kh": "Charm","price": 5000, "image": "/static/images/k204.jpg", "categories": ["Italy Bracelet"], "subcategory": ["All","Flag"],"discount":20 },
     {"id": 3605, "name_kh": "Charm","price": 5000, "image": "/static/images/k205.jpg", "categories": ["Italy Bracelet"], "subcategory": ["All","Flag"],"discount":20 },
     {"id": 3606, "name_kh": "Charm","price": 5000, "image": "/static/images/k206.jpg", "categories": ["Italy Bracelet"], "subcategory": ["All","Flag"],"discount":20 },
     {"id": 3607, "name_kh": "Charm","price": 5000, "image": "/static/images/k207.jpg", "categories": ["Italy Bracelet"], "subcategory": ["All","Flag"],"discount":20 },
     {"id": 3608, "name_kh": "Charm","price": 5000, "image": "/static/images/k208.jpg", "categories": ["Italy Bracelet"], "subcategory": ["All","Flag"],"discount":20 },
     {"id": 3609, "name_kh": "Charm","price": 5000, "image": "/static/images/k209.jpg", "categories": ["Italy Bracelet"], "subcategory": ["All","Flag"],"discount":20 },
     {"id": 3610, "name_kh": "Charm","price": 5000, "image": "/static/images/k210.jpg", "categories": ["Italy Bracelet"], "subcategory": ["All","Flag"],"discount":20 },

    ]
    return render_template('custom_bracelet.html', charms=charms)
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