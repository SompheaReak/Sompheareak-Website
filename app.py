import os
import requests
from flask import Flask, render_template, request, redirect, url_for, jsonify, session, abort

app = Flask(__name__)
app.secret_key = 'change_this_to_a_random_secret_key'
app.debug = True

# --- CONFIGURATION ---
ADMIN_USERNAME = 'AdminSompheaReakVitou'
ADMIN_PASSWORD = 'Thesong_Admin@2022?!$'
BOT_TOKEN = "7528700801:AAGTvXjk5qPBnq_qx69ZOW4RMLuGy40w5k8"
CHAT_ID = "-1002654437316"
BANNED_IPS = ['123.45.67.89', '45.119.135.70']

# --- DATA: Products ---
products = [
    {"id": 101, "name_kh": "NINJAGO Season 1 - DX Suit", "price": 30000, "image": "https://raw.githubusercontent.com/TheSong-Store/static/main/images/njoss1dx.jpg", "categories": ["LEGO Ninjago", "Toy"], "subcategory": ["Lego Ninjago", "Season 1"], "stock": 1},
    {"id": 102, "name_kh": "NINJAGO Season 1 - KAI (DX)", "price": 5000, "image": "https://raw.githubusercontent.com/TheSong-Store/static/main/images/njoss1dxkai.jpg", "categories": ["LEGO Ninjago", "Toy"], "subcategory": ["Lego Ninjago", "Season 1"], "stock": 1},
    {"id": 103, "name_kh": "NINJAGO Season 1 - ZANE (DX)", "price": 5000, "image": "https://raw.githubusercontent.com/TheSong-Store/static/main/images/njoss1dxzane.jpg", "categories": ["LEGO Ninjago", "Toy"], "subcategory": ["Lego Ninjago", "Season 1"], "stock": 1},
]

# --- DATA: Subcategories ---
subcategories_map = {
    "Hot Sale": [],
    "LEGO Ninjago": ["Dragon Rising", "Building Set", "Season 1", "Season 2", "Season 3", "Season 4", "Season 5"],
    "LEGO Anime": ["One Piece", "Demon Slayer"],
    "Accessories": ["Gym Bracelet", "Gem Stone Bracelet", "Dragon Bracelet", "Bracelet"],
    "Keychain": ["Gun Keychains"],
    "LEGO": ["Formula 1"],
    "Toy": ["Lego Ninjago", "One Piece", "Lego WWII", "Lego ទាហាន"],
    "Italy Bracelet": ["All", "Football", "Gem", "Flag", "Chain"],
    "Lucky Draw": ["/lucky-draw"]
}

# --- DATA: Category Images (New) ---
category_images = {
    "Hot Sale": "https://images.unsplash.com/photo-1523381210434-271e8be1f52b?w=200",
    "LEGO Ninjago": "https://images.unsplash.com/photo-1560000593-06674681330c?w=200",
    "LEGO Anime": "https://images.unsplash.com/photo-1566576912902-1dcd1b6d0e3d?w=200",
    "Accessories": "https://images.unsplash.com/photo-1515562141207-7a88fb7ce338?w=200",
    "Toy": "https://images.unsplash.com/photo-1558877385-48572c023785?w=200",
    "Keychain": "https://images.unsplash.com/photo-1622619000171-8935c421735d?w=200",
    "Italy Bracelet": "https://images.unsplash.com/photo-1573408301185-9146fe634ad0?w=200",
    "LEGO": "https://images.unsplash.com/photo-1585366119957-e9730b6d0f60?w=200",
    "Lucky Draw": "https://images.unsplash.com/photo-1513201099705-a9746e1e201f?w=200"
}

# --- HELPER FUNCTIONS ---
def notify_telegram(ip, user_agent):
    message = f"📦 *New Visitor*\n*IP:* `{ip}`\n*Device:* `{user_agent}`"
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    try:
        requests.post(url, json={"chat_id": CHAT_ID, "text": message, "parse_mode": "Markdown"})
    except:
        pass

@app.before_request
def block_banned_ips():
    ip = request.headers.get('X-Forwarded-For', request.remote_addr).split(',')[0].strip()
    if ip in BANNED_IPS:
        abort(403)
    if not session.get('notified'):
        notify_telegram(ip, request.headers.get('User-Agent'))
        session['notified'] = True

# --- ROUTES ---
@app.route('/')
def home():
    return redirect(url_for('category', category_name='Hot Sale'))

@app.route('/category/<category_name>')
def category(category_name):
    language = request.args.get('lang', 'kh')
    
    if category_name == 'Lucky Draw':
        return redirect(url_for('lucky_draw'))

    # If subcategories exist and user just clicked main category, go to first subcategory
    subs = subcategories_map.get(category_name, [])
    # Optional: Logic to redirect to first subcategory can go here if desired

    # Filter products
    filtered_products = [p for p in products if category_name in p.get('categories', [])]
    
    return render_template('home.html', 
                         products=filtered_products, 
                         language=language, 
                         category_images=category_images,
                         subcategories_map=subcategories_map,
                         current_category=category_name)

@app.route('/product/<int:product_id>')
def product_detail(product_id):
    product = next((p for p in products if p['id'] == product_id), None)
    return render_template('product.html', product=product)

@app.route('/lucky-draw')
def lucky_draw():
    return render_template('minifigure_game.html')

@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        if request.form.get('username') == ADMIN_USERNAME and request.form.get('password') == ADMIN_PASSWORD:
            session['admin'] = True
            return "Logged in (Dashboard Placeholder)"
        return "Invalid Credentials"
    return render_template('admin_login.html')

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)


