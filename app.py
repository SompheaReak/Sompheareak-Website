import os 
import requests
# Admin login credentials
ADMIN_USERNAME = 'AdminSompheaReakVitou'
ADMIN_PASSWORD = 'Thesong_Admin@2022?!$'
from flask import Flask, render_template, request, redirect, url_for, jsonify, session, abort
app = Flask(__name__)
import datetime
def notify_telegram(ip, user_agent):
    bot_token = "7663680888:AAHhInaDKP8QNxw8l87dQaNPsRTZFQXy1J4"
    chat_id = "-1002660809745"
    message = f"🌐 *New Visitor Alert!*\n\n*IP:* `{ip}`\n*Device:* `{user_agent}`"

    url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
    payload = {
        'chat_id': chat_id,
        'text': message,
        'parse_mode': 'Markdown'
    }

    response = requests.post(url, data=payload)
    print("==> Visitor Bot Message Sent")
    print("BOT TOKEN:", bot_token)
    print("CHAT ID:", chat_id)
    print("MESSAGE:", message)
    print("RESPONSE:", response.text)
# List of IPs you want to ban
banned_ips = ['123.45.67.89']  # Replace with real IPs
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
    {"id": 1916, "name_kh": " Dragon Rising S3 - NOKT","price": 9000, "image": "/static/images/ss3nokt.jpg", "categories": ["LEGO Ninjago", "Toy"], "subcategory": ["Lego Ninjago","New"],"stock": 1},
    {"id": 1917, "name_kh": " Dragon Rising S3 - ROX","price": 9000, "image": "/static/images/ss3rox.jpg", "categories": ["LEGO Ninjago", "Toy"], "subcategory": ["Lego Ninjago","New"],"stock": 1},
    {"id": 1918, "name_kh": " Dragon Rising S3 - DRIX","price": 9000, "image": "/static/images/ss3drix.jpg", "categories": ["LEGO Ninjago", "Toy"], "subcategory": ["Lego Ninjago","New"],"stock": 1},
    {"id": 1919, "name_kh": " Dragon Rising S3 - ZARKT","price": 9000, "image": "/static/images/ss3zarkt.jpg", "categories": ["LEGO Ninjago", "Toy"], "subcategory": ["Lego Ninjago","New"],"stock": 1},
    {"id": 1920, "name_kh": " Dragon Rising S3 - KUR","price": 9000, "image": "/static/images/ss3kur.jpg", "categories": ["LEGO Ninjago", "Toy"], "subcategory": ["Lego Ninjago","New"],"stock": 1},

    {"id": 1101, "name_kh": "Zane's Set", "price": 44000, "image": "/static/images/set01.jpg", "categories": ["LEGO Ninjago","Toy"], "subcategory": ["Lego Ninjago","Building Set"]},
    {"id": 1102, "name_kh": "Kai Merch", "price": 5000, "image": "/static/images/set02.jpg", "categories": ["LEGO Ninjago", "Toy"], "subcategory": ["Lego Ninjago","Building Set"]},
    {"id": 1003, "name_kh": "cole Merch", "price": 5000, "image": "/static/images/set03.jpg", "categories": ["LEGO Ninjago", "Toy"], "subcategory": ["Lego Ninjago","Building Set"]},
    {"id": 1004, "name_kh": "idk name ", "price": 5000, "image": "/static/images/set04.jpg", "categories": ["LEGO Ninjago", "Toy"], "subcategory": ["Lego Ninjago","Building Set"]},

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
        ip = request.headers.get('X-Forwarded-For', request.remote_addr)
        bot_token = "7663680888:AAHhInaDKP8QNxw8l87dQaNPsRTZFQXy1J4"
        chat_id = "-1002660809745"

        name = request.form['name']
        phone = request.form['phone']
        address = request.form['address']
        delivery_method = request.form['delivery']

        delivery_text = ""
        delivery_fee = 0
        total = 0

        if delivery_method == "door":
            delivery_text = "ទំនិញដល់ដៃទូទាត់ប្រាក់"
            delivery_fee = 7000
        elif delivery_method == "vet":
            delivery_text = "វីរៈប៊ុនថាំ (VET)"
            delivery_fee = 5000
        elif delivery_method == "jnt":
            delivery_text = "J&T"
            delivery_fee = 7000

        message = f"🛒 *New Order Received!*\n\n"
        message += f"*Name:* {name}\n*Phone:* {phone}\n*Address:* {address}\n"
        message += f"*Delivery:* {delivery_text} ({delivery_fee}៛)\n"
        message += f"*IP:* {ip}\n\n*Order Details:*\n"

        for item in cart:
            p = item['product']
            subtotal = p['price'] * item['quantity']
            total += subtotal
            name = p.get('name_en', p.get('name_kh', 'Unknown Product'))
            message += f"{name} x {item['quantity']} = {subtotal:,}៛\n"

        total += delivery_fee
        message += f"\n*Total with Delivery:* {total:,}៛"

        url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
        payload = {
            "chat_id": chat_id,
            "text": message,
            "parse_mode": "Markdown"
        }
        response = requests.post(url, data=payload)
        print("Telegram response:", response.text)

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
    import os
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)