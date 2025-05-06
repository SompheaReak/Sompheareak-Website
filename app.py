import os 
import requests
# Admin login credentials
ADMIN_USERNAME = 'AdminSompheaReakVitou'
ADMIN_PASSWORD = 'Thesong_Admin@2022?!$'
from flask import Flask, render_template, request, redirect, url_for, jsonify, session, abort
import datetime
def notify_telegram(ip, user_agent):
    bot_token = "7663680888:AAH...YOUR_TOKEN"
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
banned_ips = ['123.45.67.89', '111.222.333.444']  # Replace with real IPs

app = Flask(__name__)
@app.before_request
def block_banned_ips():
    ip = request.remote_addr
    user_agent = request.headers.get('User-Agent')

    # Block banned IPs first
    if ip in banned_ips:
        abort(403)

    # Then log only allowed visitors
    notify_telegram(ip, user_agent)

app.secret_key = 'your_secret_key'
app.debug = True

# Products data
products = [
    {"id": 1, "name_kh": "M416 - ប្រាក់មាស", "name_en": "M416 - Gold Plate", "price": 6000, "image": "/static/images/m416-gold.jpg", "categories": ["Keychain"], "subcategory": "Gun Keychains"},
    {"id": 2, "name_kh": "M416 - ពណ៌ដើម", "name_en": "M416 - Default", "price": 6000, "image": "/static/images/m416-default.jpg", "categories": ["Keychain"], "subcategory": "Gun Keychains"},
 {"id": 3, "name_kh": "AKM - ប្រាក់មាស", "name_en": "AKM - Gold Plate", "price": 6000, "image": "/static/images/akm-gold.jpg", "categories": ["Keychain"], "subcategory": "Gun Keychains"},
    {"id": 4, "name_kh": "AKM - ពណ៌ដើម", "name_en": "AKM - Default", "price": 6000, "image": "/static/images/akm-default.jpg", "categories": ["Keychain"], "subcategory": "Gun Keychains"},
    {"id": 5, "name_kh": "Scar L - ពណ៌ដើម", "name_en": "Scar L - Default", "price": 6000, "image": "/static/images/scarl-default.jpg", "categories": ["Keychain"], "subcategory": "Gun Keychains"},
    {"id": 6, "name_kh": "Scar L - ពណ៌មាស", "name_en": "Scar L - Gold", "price": 6000, "image": "/static/images/scarl-gold.jpg", "categories": ["Keychain"], "subcategory": "Gun Keychains"},
    {"id": 7, "name_kh": "ក្រវិលស", "name_en": "White Chalcedony", "price": 6000, "image": "/static/images/bc-01.jpg", "categories": ["Accessories"], "subcategory": "Gem Stone Bracelets"},
    {"id": 8, "name_kh": "ក្រវិលពណ៌ផ្កាឈូក", "name_en": "Pink Opal", "price": 6000, "image": "/static/images/bc-02.jpg", "categories": ["Accessories"], "subcategory": "Gem Stone Bracelets"},
    {"id": 9, "name_kh": "គ្រីស្ទាល់ពណ៌ផ្កាឈូក", "name_en": "Pink Crystal", "price": 5500, "image": "/static/images/bc-03.jpg", "categories": ["Accessories"], "subcategory": "Gem Stone Bracelets"},
    {"id": 10, "name_kh": "គ្រីស្ទាល់ស្ករត្រសក់", "name_en": "Strawberry Crystal", "price": 9000, "image": "/static/images/bc-04.jpg", "categories": ["Accessories"], "subcategory": "Gem Stone Bracelets"},
    {"id": 11, "name_kh": "Lego Ninjago Season 1 - DX Suit", "name_en": "Lego Ninjago Season 1 - DX Suit", "price": 30000, "image": "/static/images/njoss1dx.jpg", "categories": ["LEGO Ninjago", "Toy"], "subcategory": ["Lego Ninjago","Season 1"]},
    {"id": 12, "name_kh": "Kai (DX)", "name_en": "Lego Ninjago Season 1 - Kai", "price": 5000, "image": "/static/images/njoss1dxkai.jpg", "categories": ["LEGO Ninjago", "Toy"], "subcategory": ["Lego Ninjago","Season 1"]},
    {"id": 13, "name_kh": "Zane (DX)", "name_en": "Lego Ninjago Season 1 - Zane", "price": 5000, "image": "/static/images/njoss1dxzane.jpg", "categories": ["LEGO Ninjago", "Toy"], "subcategory": ["Lego Ninjago","Season 1"]},
    {"id": 14, "name_kh": "Jay (DX)", "name_en": "Lego Ninjago Season 1 - Jay", "price": 5000, "image": "/static/images/njoss1dxjay.jpg", "categories": ["LEGO Ninjago", "Toy"], "subcategory": ["Lego Ninjago","Season 1"]},
    {"id": 15, "name_kh": "Cole (DX)", "name_en": "Lego Ninjago Season 1 - Cole", "price": 5000, "image": "/static/images/njoss1dxcole.jpg", "categories": ["LEGO Ninjago", "Toy"], "subcategory": ["Lego Ninjago","Season 1"]},
    {"id": 16, "name_kh": "Nya (DX)", "name_en": "Lego Ninjago Season 1 - Nya", "price": 5000, "image": "/static/images/njoss1dxnya.jpg", "categories": ["LEGO Ninjago", "Toy"], "subcategory": ["Lego Ninjago","Season 1"]},
    {"id": 17, "name_kh": "Lloyd (DX)", "name_en": "Lego Ninjago Season 1 - Lloyd", "price": 5000, "image": "/static/images/njoss1dxlloyd.jpg", "categories": ["LEGO Ninjago", "Toy"], "subcategory": ["Lego Ninjago","Season 1"]},
    {"id": 18, "name_kh": "Lego Ninjago Season 1 - Pilot Suit", "name_en": "Lego Ninjago Season 1 - Pilot Suit", "price": 25000, "image": "/static/images/njoss1pilot.jpg", "categories": ["LEGO Ninjago", "Toy"], "subcategory": ["Lego Ninjago","Season 1"]},
    {"id": 19, "name_kh": "Lego Ninjago Season 1 - Kai", "name_en": "Lego Ninjago Season 1 - Kai", "price": 5000, "image": "/static/images/njoss1pilotkai.jpg", "categories": ["LEGO Ninjago", "Toy"], "subcategory": ["Lego Ninjago","Season 1"]},
    {"id": 20, "name_kh": "Lego Ninjago Season 1 - Zane", "name_en": "Lego Ninjago Season 1 - Zane", "price": 5000, "image": "/static/images/njoss1pilotzane.jpg", "categories": ["LEGO Ninjago", "Toy"], "subcategory": ["Lego Ninjago","Season 1"]},
    {"id": 21, "name_kh": "Lego Ninjago Season 1 - Jay", "name_en": "Lego Ninjago Season 1 - Jay", "price": 5000, "image": "/static/images/njoss1pilotjay.jpg", "categories": ["LEGO Ninjago", "Toy"], "subcategory": ["Lego Ninjago","Season 1"]},
    {"id": 22, "name_kh": "Lego Ninjago Season 1 - Cole", "name_en": "Lego Ninjago Season 1 - Cole", "price": 5000, "image": "/static/images/njoss1pilotcole.jpg", "categories": ["LEGO Ninjago", "Toy"], "subcategory": ["Lego Ninjago","Season 1"]},
    {"id": 23, "name_kh": "Lego Ninjago Season 1 - Lloyd", "name_en": "Lego Ninjago Season 1 - Lloyd", "price": 5000, "image": "/static/images/njoss1pilotlloyd.jpg", "categories": ["LEGO Ninjago", "Toy"], "subcategory": ["Lego Ninjago","Season 1"]},
    {"id": 24, "name_kh": "ខ្សៃដៃថ្មធម្មជាតិ - ", "name_en": "Gem Stone Bracelet - ", "price": 5000, "image": "/static/images/bc-05.jpg", "categories": ["Accessories"], "subcategory": "Gem Stone Bracelets"},
    {"id": 25, "name_kh": "ខ្សៃដៃថ្មធម្មជាតិ - ", "name_en": "Gem Stone Bracelet - ", "price": 5000, "image": "/static/images/bc-06.jpg", "categories": ["Accessories"], "subcategory": "Gem Stone Bracelets"},
    {"id": 26, "name_kh": "ខ្សៃដៃថ្មធម្មជាតិ - ", "name_en": "Gem Stone Bracelet - ", "price": 5000, "image": "/static/images/bc-07.jpg", "categories": ["Accessories"], "subcategory": "Gem Stone Bracelets"},
    {"id": 27, "name_kh": "ខ្សៃដៃថ្មធម្មជាតិ - ", "name_en": "Gem Stone Bracelet - ", "price": 5000, "image": "/static/images/bc-08.jpg", "categories": ["Accessories"], "subcategory": "Gem Stone Bracelets"},
    {"id": 28, "name_kh": "ខ្សៃដៃថ្មធម្មជាតិ - ", "name_en": "Gem Stone Bracelet - ", "price": 5000, "image": "/static/images/bc-09.jpg", "categories": ["Accessories"], "subcategory": "Gem Stone Bracelets"},
    {"id": 29, "name_kh": "ខ្សៃដៃថ្មធម្មជាតិ - ", "name_en": "Gem Stone Bracelet - ", "price": 5000, "image": "/static/images/bc-10.jpg", "categories": ["Accessories"], "subcategory": "Gem Stone Bracelets"},
    {"id": 30, "name_kh": "ខ្សៃដៃ - ", "name_en": "Gym Bracelet - ", "price": 5000, "image": "/static/images/gymblack1.jpg", "categories": ["Accessories"], "subcategory": "Gym Bracelet"},
    {"id": 31, "name_kh": "ខ្សៃដៃ - ", "name_en": "Gym Bracelet - ", "price": 5000, "image": "/static/images/gymblack2.jpg", "categories": ["Accessories"], "subcategory": "Gym Bracelet"},
    {"id": 32, "name_kh": "ខ្សៃដៃ - ", "name_en": "Gym Bracelet - ", "price": 5000, "image": "/static/images/gymsilver1.jpg", "categories": ["Accessories"], "subcategory": "Gym Bracelet"},
    {"id": 33, "name_kh": "ខ្សៃដៃ - ", "name_en": "Gym Bracelet - ", "price": 5000, "image": "/static/images/gymsilver2.jpg", "categories": ["Accessories"], "subcategory": "Gym Bracelet"},
    {"id": 34, "name_kh": "ខ្សៃដៃ - ", "name_en": "Gym Bracelet - ", "price": 5000, "image": "/static/images/gymgold1.jpg", "categories": ["Accessories"], "subcategory": "Gym Bracelet"},
    {"id": 35, "name_kh": "ខ្សៃដៃ - ", "name_en": "Gym Bracelet - ", "price": 5000, "image": "/static/images/gymgold2.jpg", "categories": ["Accessories"], "subcategory": "Gym Bracelet"},
    {"id": 36, "name_kh": "WWII Germany 01", "name_en": "WWII Germany 01", "price": 1250, "image": "/static/images/wwii-01.jpg", "categories": ["toy"], "subcategory": "Lego WWII"},
    {"id": 37, "name_kh": "WWII Germany 02", "name_en": "WWII Germany 02", "price": 1250, "image": "/static/images/wwii-02.jpg", "categories": ["toy"], "subcategory": "Lego WWII"},
    {"id": 38, "name_kh": "WWII Germany 03", "name_en": "WWII Germany 03", "price": 1250, "image": "/static/images/wwii-03.jpg", "categories": ["toy"], "subcategory": "Lego WWII"},
    {"id": 39, "name_kh": "WWII Germany 04", "name_en": "WWII Germany 04", "price": 1250, "image": "/static/images/wwii-04.jpg", "categories": ["toy"], "subcategory": "Lego WWII"},
    {"id": 40, "name_kh": "WWII Germany 05", "name_en": "WWII Germany 05", "price": 1250, "image": "/static/images/wwii-05.jpg", "categories": ["toy"], "subcategory": "Lego WWII"},
    {"id": 41, "name_kh": "WWII Germany 06", "name_en": "WWII Germany 06", "price": 1250, "image": "/static/images/wwii-06.jpg", "categories": ["toy"], "subcategory": "Lego WWII"},
    {"id": 42, "name_kh": "WWII USA 01", "name_en": "WWII USA 01", "price": 1250, "image": "/static/images/wwii-07.jpg", "categories": ["toy"], "subcategory": "Lego WWII"},
    {"id": 43, "name_kh": "WWII USA 02", "name_en": "WWII USA 02", "price": 1250, "image": "/static/images/wwii-08.jpg", "categories": ["toy"], "subcategory": "Lego WWII"},
    {"id": 44, "name_kh": "WWII USA 03", "name_en": "WWII USA 03", "price": 1250, "image": "/static/images/wwii-09.jpg", "categories": ["toy"], "subcategory": "Lego WWII"},
    {"id": 45, "name_kh": "WWII USA 04", "name_en": "WWII USA 04", "price": 1250, "image": "/static/images/wwii-10.jpg", "categories": ["toy"], "subcategory": "Lego WWII"},
    {"id": 46, "name_kh": "WWII USA 05", "name_en": "WWII USA 05", "price": 1250, "image": "/static/images/wwii-11.jpg", "categories": ["toy"], "subcategory": "Lego WWII"},
    {"id": 47, "name_kh": "WWII SOVIET 01", "name_en": "WWII SOVIET 01", "price": 1250, "image": "/static/images/wwii-12.jpg", "categories": ["toy"], "subcategory": "Lego WWII"},
    {"id": 48, "name_kh": "WWII SOVIET 02", "name_en": "WWII SOVIET 02", "price": 1250, "image": "/static/images/wwii-13.jpg", "categories": ["toy"], "subcategory": "Lego WWII"},
    {"id": 49, "name_kh": "WWII SOVIET 03", "name_en": "WWII SOVIET 03", "price": 1250, "image": "/static/images/wwii-14.jpg", "categories": ["toy"], "subcategory": "Lego WWII"},
    {"id": 50, "name_kh": "WWII SOVIET 04", "name_en": "WWII SOVIET 04", "price": 1250, "image": "/static/images/wwii-15.jpg", "categories": ["toy"], "subcategory": "Lego WWII"},
    {"id": 51, "name_kh": "WWII SOVIET 05", "name_en": "WWII SOVIET 05", "price": 1250, "image": "/static/images/wwii-16.jpg", "categories": ["toy"], "subcategory": "Lego WWII"},
    {"id": 52, "name_kh": "WWII SOVIET 06", "name_en": "WWII SOVIET 06", "price": 1250, "image": "/static/images/wwii-17.jpg", "categories": ["toy"], "subcategory": "Lego WWII"},
    {"id": 53, "name_kh": "WWII SOVIET 07", "name_en": "WWII SOVIET 07", "price": 1250, "image": "/static/images/wwii-18.jpg", "categories": ["toy"], "subcategory": "Lego WWII"},
    {"id": 54, "name_kh": "WWII SOVIET 08", "name_en": "WWII SOVIET 08", "price": 1250, "image": "/static/images/wwii-19.jpg", "categories": ["toy"], "subcategory": "Lego WWII"},
    {"id": 55, "name_kh": "ខ្សែដៃ - ក្បាលនាគប្រាក់", "name_en": "Dragon Bracelet - ", "price": 6000, "image": "/static/images/dragon01.jpg", "categories": ["Accessories"], "subcategory": "Dragon Bracelet"},
    {"id": 56, "name_kh": "ខ្សែដៃ - ក្បាលនាគប្រាក់", "name_en": "Dragon Bracelet - ", "price": 6000, "image": "/static/images/dragon10.jpg", "categories": ["Accessories"], "subcategory": "Dragon Bracelet"},
    {"id": 57, "name_kh": "ខ្សែដៃ - ក្បាលនាគប្រាក់", "name_en": "Dragon Bracelet - ", "price": 6000, "image": "/static/images/dragon02.jpg", "categories": ["Accessories"], "subcategory": "Dragon Bracelet"},
    {"id": 58, "name_kh": "ខ្សែដៃ - ក្បាលនាគប្រាក់", "name_en": "Dragon Bracelet - ", "price": 6000, "image": "/static/images/dragon05.jpg", "categories": ["Accessories"], "subcategory": "Dragon Bracelet"},
    {"id": 59, "name_kh": "ខ្សែដៃ - ក្បាលនាគប្រាក់", "name_en": "Dragon Bracelet - ", "price": 6000, "image": "/static/images/dragon07.jpg", "categories": ["Accessories"], "subcategory": "Dragon Bracelet"},
    {"id": 60, "name_kh": "ខ្សែដៃ - ក្បាលនាគប្រាក់", "name_en": "Dragon Bracelet - ", "price": 6000, "image": "/static/images/dragon04.jpg", "categories": ["Accessories"], "subcategory": "Dragon Bracelet"},
    {"id": 61, "name_kh": "ខ្សែដៃ - ក្បាលនាគប្រាក់", "name_en": "Dragon Bracelet - ", "price": 6000, "image": "/static/images/dragon08.jpg", "categories": ["Accessories"], "subcategory": "Dragon Bracelet"},
    {"id": 62, "name_kh": "ខ្សែដៃ - ក្បាលនាគប្រាក់", "name_en": "Dragon Bracelet - ", "price": 6000, "image": "/static/images/dragon09.jpg", "categories": ["Accessories"], "subcategory": "Dragon Bracelet"},
    {"id": 63, "name_kh": "ខ្សែដៃ - ក្បាលនាគប្រាក់", "name_en": "Dragon Bracelet - ", "price": 6000, "image": "/static/images/dragon06.jpg", "categories": ["Accessories"], "subcategory": "Dragon Bracelet"},
    {"id": 64, "name_kh": "ខ្សែដៃ - ក្បាលនាគប្រាក់", "name_en": "Dragon Bracelet - ", "price": 6000, "image": "/static/images/dragon03.jpg", "categories": ["Accessories"], "subcategory": "Dragon Bracelet"},
    {"id": 65, "name_kh": "ខ្សែដៃ -", "name_en": "Bracelet - ", "price": 6000, "image": "/static/images/bcl01.jpg", "categories": ["Accessories"], "subcategory": "Bracelet"},
    {"id": 66, "name_kh": "ខ្សែដៃ -", "name_en": "Bracelet - ", "price": 6000, "image": "/static/images/bcl02.jpg", "categories": ["Accessories"], "subcategory": "Bracelet"},
    {"id": 67, "name_kh": "ខ្សែដៃ -", "name_en": "Bracelet - ", "price": 6000, "image": "/static/images/bcl03.jpg", "categories": ["Accessories"], "subcategory": "Bracelet"},
    {"id": 68, "name_kh": "ខ្សែដៃ -", "name_en": "Bracelet - ", "price": 6000, "image": "/static/images/bcl04.jpg", "categories": ["Accessories"], "subcategory": "Bracelet"},
    {"id": 69, "name_kh": "ខ្សែដៃ -", "name_en": "Bracelet - ", "price": 6000, "image": "/static/images/bcl05.jpg", "categories": ["Accessories"], "subcategory": "Bracelet"},
    {"id": 70, "name_kh": "ខ្សែដៃ -", "name_en": "Bracelet - ", "price": 6000, "image": "/static/images/bcl06.jpg", "categories": ["Accessories"], "subcategory": "Bracelet"},
    {"id": 71, "name_kh": "ខ្សែដៃ -", "name_en": "Bracelet - ", "price": 6000, "image": "/static/images/bcl07.jpg", "categories": ["Accessories"], "subcategory": "Bracelet"},
    {"id": 72, "name_kh": "ខ្សែដៃ -", "name_en": "Bracelet - ", "price": 6000, "image": "/static/images/bcl08.jpg", "categories": ["Accessories"], "subcategory": "Bracelet"},
    {"id": 73, "name_kh": "ខ្សែដៃ -", "name_en": "Bracelet -", "price": 6000, "image": "/static/images/bc11.jpg", "categories": ["Accessories"], "subcategory": "Bracelet"},
    {"id": 74, "name_kh": "ខ្សែដៃ -", "name_en": "Bracelet -", "price": 6000, "image": "/static/images/bc12.jpg", "categories": ["Accessories"], "subcategory": "Bracelet"},
    {"id": 75, "name_kh": "ខ្សែដៃ -", "name_en": "Bracelet -", "price": 6000, "image": "/static/images/bc13.jpg", "categories": ["Accessories"], "subcategory": "Bracelet"},
    {"id": 76, "name_kh": "ខ្សែដៃ -", "name_en": "Bracelet -", "price": 6000, "image": "/static/images/bc14.jpg", "categories": ["Accessories"], "subcategory": "Bracelet"},
    {"id": 77, "name_kh": "ខ្សែដៃ -", "name_en": "Bracelet -", "price": 6000, "image": "/static/images/bc15.jpg", "categories": ["Accessories"], "subcategory": "Bracelet"},
    {"id": 78, "name_kh": "ខ្សែដៃ -", "name_en": "Bracelet -", "price": 6000, "image": "/static/images/bc16.jpg", "categories": ["Accessories"], "subcategory": "Bracelet"},
    {"id": 79, "name_kh": "ខ្សែដៃ -", "name_en": "Bracelet -", "price": 6000, "image": "/static/images/bc17.jpg", "categories": ["Accessories"], "subcategory": "Bracelet"},
    {"id": 80, "name_kh": "ខ្សែដៃ -", "name_en": "Bracelet -", "price": 6000, "image": "/static/images/bc18.jpg", "categories": ["Accessories"], "subcategory": "Bracelet"},
    {"id": 81, "name_kh": "ខ្សែដៃ -", "name_en": "Bracelet -", "price": 6000, "image": "/static/images/bc19.jpg", "categories": ["Accessories"], "subcategory": "Bracelet"},
    {"id": 82, "name_kh": "ខ្សែដៃ -", "name_en": "Bracelet -", "price": 6000, "image": "/static/images/bc20.jpg", "categories": ["Accessories"], "subcategory": "Bracelet"},
    {"id": 83, "name_kh": "ខ្សែដៃ -", "name_en": "Bracelet -", "price": 6000, "image": "/static/images/bc21.jpg", "categories": ["Accessories"], "subcategory": "Bracelet"},
    {"id": 84, "name_kh": "ខ្សែដៃ -", "name_en": "Bracelet -", "price": 6000, "image": "/static/images/bc22.jpg", "categories": ["Accessories"], "subcategory": "Bracelet"},
    {"id": 85, "name_kh": "ខ្សែដៃ -", "name_en": "Bracelet -", "price": 6000, "image": "/static/images/bc23.jpg", "categories": ["Accessories"], "subcategory": "Bracelet"},
    {"id": 86, "name_kh": "ខ្សែដៃ -", "name_en": "Bracelet -", "price": 6000, "image": "/static/images/bc24.jpg", "categories": ["Accessories"], "subcategory": "Bracelet"},
    {"id": 87, "name_kh": "ខ្សែដៃ -", "name_en": "Bracelet -", "price": 6000, "image": "/static/images/bc25.jpg", "categories": ["Accessories"], "subcategory": "Bracelet"},
    {"id": 88, "name_kh": "ខ្សែដៃ -", "name_en": "Bracelet -", "price": 6000, "image": "/static/images/bc26.jpg", "categories": ["Accessories"], "subcategory": "Bracelet"},
    {"id": 89, "name_kh": "ខ្សែដៃ -", "name_en": "Bracelet -", "price": 6000, "image": "/static/images/bc27.jpg", "categories": ["Accessories"], "subcategory": "Bracelet"},
    {"id": 90, "name_kh": "ខ្សែដៃ -", "name_en": "Bracelet -", "price": 6000, "image": "/static/images/bc28.jpg", "categories": ["Accessories"], "subcategory": "Bracelet"},
    {"id": 91, "name_kh": "ខ្សែដៃ -", "name_en": "Bracelet -", "price": 6000, "image": "/static/images/bc29.jpg", "categories": ["Accessories"], "subcategory": "Bracelet"},
    {"id": 92, "name_kh": "ខ្សែដៃ -", "name_en": "Bracelet -", "price": 6000, "image": "/static/images/bc30.jpg", "categories": ["Accessories"], "subcategory": "Bracelet"},
    {"id": 93, "name_kh": "ខ្សែដៃ -", "name_en": "Bracelet -", "price": 6000, "image": "/static/images/bc31.jpg", "categories": ["Accessories"], "subcategory": "Bracelet"},
   ]
# --- Subcategories Map ---
subcategories_map = {
    "Accessories": ["Gym Bracelet", "Gem Stone Bracelet","Dragon Bracelet","Bracelet"],
    "LEGO Ninjago": ["Season 1", "Season 2", "Season 3", "Season 4", "Season 5", "Season 6", "Season 7", "Season 8"],
    "Keychain": ["Gun Keychains"],
    "Hot Sale": [],
    "Toy": ["Lego Ninjago", "Lego WWII", "Lego ទាហាន"]
}

# --- Routes ---

@app.route('/')
def home():
    language = request.args.get('lang', 'kh')
    cart = session.get('cart', [])
    return render_template('home.html', products=products, language=language, cart=cart, current_category=None, current_subcategory=None, subcategories=[])

@app.route('/category/<category_name>')
def category(category_name):
    language = request.args.get('lang', 'kh')
    filtered_products = [
        p for p in products
        if category_name in p.get('categories', [])
    ]
    subs = subcategories_map.get(category_name, [])
    cart = session.get('cart', [])
    return render_template(
        'home.html',
        products=filtered_products,
        language=language,
        cart=cart,
        current_category=category_name,
        current_subcategory=None,
        subcategories=subs
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

@app.route('/add-to-cart', methods=["POST"])
def add_to_cart():
    product_id = int(request.form['product_id'])
    quantity = int(request.form['quantity'])
    product = next((p for p in products if p["id"] == product_id), None)

    if product:
        cart = session.get('cart', [])
        cart.append({"product": product, "quantity": quantity})
        session['cart'] = cart

    return jsonify({"success": True, "cart_count": len(session.get('cart', []))})

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
        print("==> Checkout POST triggered")
        bot_token = "7663680888:AAHhInaDKP8QNxw8l87dQaNPsRTZFQXy1J4"
        chat_id = "-1002660809745"

        name = request.form['name']
        phone = request.form['phone']
        address = request.form['address']
        delivery_method = request.form['delivery']

    delivery_text = ""
    delivery_fee = 0

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
    message += f"*IP:* `{ip}`\n"
    message += f"*Name:* {name}\n*Phone:* {phone}\n*Address:* {address}\n"
    message += f"*Delivery:* {delivery_text} ({delivery_fee}៛)\n\n*Order Details:*\n"

    total = 0
    for item in cart:
        p = item['product']
        subtotal = p['price'] * item['quantity']
        total += subtotal
        message += f"- {p['name_en']} x {item['quantity']} = {subtotal}៛\n"

    total += delivery_fee
    message += f"\n*Total with Delivery:* {total}៛"

    # Send to Telegram
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