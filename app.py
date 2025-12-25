import os
import requests
from flask import Flask, render_template, request, redirect, url_for, jsonify, session, abort
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.secret_key = 'somphea_reak_fixed_key_2025'

# --- DATABASE SETUP ---
basedir = os.path.abspath(os.path.dirname(__file__))
db_path = os.path.join(basedir, 'shop.db')
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + db_path
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# --- CONFIGURATION & CREDENTIALS ---
ADMIN_USER = 'AdminSompheaReakVitou'
ADMIN_PASS = 'Thesong_Admin@2022?!$'

# Telegram Config
BOT_TOKEN = "7528700801:AAGTvXjk5qPBnq_qx69ZOW4RMLuGy40w5k8"
CHAT_ID = "-1002654437316"

# --- SECURITY SYSTEM (From Old App) ---
banned_ips = ['123.45.67.89', '45.119.135.70']

def notify_telegram(ip, user_agent, event_type="Visitor"):
    message = f"📦 *{event_type} Notification*\n*IP:* `{ip}`\n*Device:* `{user_agent}`"
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    try:
        requests.post(url, data={"chat_id": CHAT_ID, "text": message, "parse_mode": "Markdown"})
    except:
        pass

@app.before_request
def security_check():
    # Get IP address securely
    ip = request.headers.get('X-Forwarded-For', request.remote_addr).split(',')[0].strip()
    
    # Block banned IPs
    if ip in banned_ips:
        abort(403)
        
    # Notify Telegram on new session
    if not session.get('notified'):
        notify_telegram(ip, request.headers.get('User-Agent'))
        session['notified'] = True

# ==========================================
# 1. PRODUCT CATALOG (Fixed with "Italy Bracelet" Tags)
# ==========================================
PRODUCT_CATALOG = [
    # --- Charm Base
    {"id": 1, "name_kh": "Silver Charm", "price": 400, "image": "/static/images/c01.jpg", "categories": ["Italy Bracelet", "Charm"], "subcategory": "General"},
   
    # --- F1 LOGOS ---
    {"id": 1100, "name_kh": "Classic F1 Logo", "price": 3000, "image": "/static/images/charm-f1–101.jpg", "categories": ["Italy Bracelet", "Class F1🏎️"], "subcategory": "F1 Logos"},
    {"id": 1191, "name_kh": "Classic F1", "price": 3000, "image": "/static/images/charm-chain-03.jpg", "categories": ["Italy Bracelet", "Class F1🏎️"], "subcategory": "F1 Logos"},
    {"id": 1192, "name_kh": "Classic F1 - Ferri", "price": 3000, "image": "/static/images/charm-f1-301.jpg", "categories": ["Italy Bracelet", "Class F1🏎️"], "subcategory": "F1 Logos"},
    {"id": 1193, "name_kh": "Classic F1 - Porsche", "price": 3000, "image": "/static/images/charm-f1-302.jpg", "categories": ["Italy Bracelet", "Class F1🏎️"], "subcategory": "F1 Logos"},
    {"id": 1194, "name_kh": "Classic F1 - BMW", "price": 3000, "image": "/static/images/charm-f1-303.jpg", "categories": ["Italy Bracelet", "Class F1🏎️"], "subcategory": "F1 Logos"},
    {"id": 1195, "name_kh": "Classic F1 - BMW", "price": 3000, "image": "/static/images/charm-f1-304.jpg", "categories": ["Italy Bracelet", "Class F1🏎️"], "subcategory": "F1 Logos"},
    
    {"id": 1101, "name_kh": "Classic F1 - Mercedes", "price": 3000, "image": "/static/images/cc15.jpg", "categories": ["Italy Bracelet", "Class F1🏎️"], "subcategory": "F1 Logos"},
    {"id": 1102, "name_kh": "Classic F1 - Ferrari", "price": 3000, "image": "/static/images/cc04.jpg", "categories": ["Italy Bracelet", "Class F1🏎️"], "subcategory": "F1 Logos"},
    {"id": 1103, "name_kh": "Classic F1 - Porsche", "price": 3000, "image": "/static/images/cc12.jpg", "categories": ["Italy Bracelet", "Class F1🏎️"], "subcategory": "F1 Logos"},
    {"id": 1104, "name_kh": "Classic F1 - BMW", "price": 3000, "image": "/static/images/cc06.jpg", "categories": ["Italy Bracelet", "Class F1🏎️"], "subcategory": "F1 Logos"},

    # --- Pink F1 ---
    {"id": 1200, "name_kh": "Pink F1 Logo", "price": 3000, "image": "/static/images/charm-f1-201.jpg", "categories": ["Italy Bracelet", "Pink F1🏎️"], "subcategory": "Pink Collection"},
    {"id": 1291, "name_kh": "Classic F1 - Mercedes", "price": 3000, "image": "/static/images/charm-chain-03.jpg", "categories": ["Italy Bracelet", "Pink F1🏎️"], "subcategory": "Pink Collection"},
    {"id": 1292, "name_kh": "Classic F1 - Ferri", "price": 3000, "image": "/static/images/charm-f1-301.jpg", "categories": ["Italy Bracelet", "Pink F1🏎️"], "subcategory": "Pink Collection"},
    {"id": 1293, "name_kh": "Classic F1 - Porsche", "price": 3000, "image": "/static/images/charm-f1-302.jpg", "categories": ["Italy Bracelet", "Pink F1🏎️"], "subcategory": "Pink Collection"},
    {"id": 1294, "name_kh": "Classic F1 - BMW", "price": 3000, "image": "/static/images/charm-f1-303.jpg", "categories": ["Italy Bracelet", "Pink F1🏎️"], "subcategory": "Pink Collection"},
    {"id": 1295, "name_kh": "Classic F1 - BMW", "price": 3000, "image": "/static/images/charm-f1-304.jpg", "categories": ["Italy Bracelet", "Pink F1🏎️"], "subcategory": "Pink Collection"},
    {"id": 1201, "name_kh": "Pink F1 - Mercedes", "price": 3000, "image": "/static/images/charm-f1-202.jpg", "categories": ["Italy Bracelet", "Pink F1🏎️"], "subcategory": "Pink Collection"},
    {"id": 1202, "name_kh": "Pink F1 - Ferrari", "price": 3000, "image": "/static/images/charm-f1-203.jpg", "categories": ["Italy Bracelet", "Pink F1🏎️"], "subcategory": "Pink Collection"},
    {"id": 1203, "name_kh": "Pink F1 - Porsche", "price": 3000, "image": "/static/images/charm-f1-204.jpg", "categories": ["Italy Bracelet", "Pink F1🏎️"], "subcategory": "Pink Collection"},
    {"id": 1204, "name_kh": "Pink F1 - BMW", "price": 3000, "image": "/static/images/charm-f1-205.jpg", "categories": ["Italy Bracelet", "Pink F1🏎️"], "subcategory": "Pink Collection"},

    # --- CAR LOGOS ---
    {"id": 1001, "name_kh": "Car Charm 01", "price": 3000, "image": "/static/images/cc01.jpg", "categories": ["Italy Bracelet", "Car Logo"], "subcategory": "Car Brands"},
    {"id": 1002, "name_kh": "Car Charm 02", "price": 3000, "image": "/static/images/cc02.jpg", "categories": ["Italy Bracelet", "Car Logo"], "subcategory": "Car Brands"},
    {"id": 1003, "name_kh": "Car Charm 03", "price": 3000, "image": "/static/images/cc03.jpg", "categories": ["Italy Bracelet", "Car Logo"], "subcategory": "Car Brands"},
    {"id": 1004, "name_kh": "Car Charm 04", "price": 3000, "image": "/static/images/cc04.jpg", "categories": ["Italy Bracelet", "Car Logo"], "subcategory": "Car Brands"},
    {"id": 1005, "name_kh": "Car Charm 05", "price": 3000, "image": "/static/images/cc05.jpg", "categories": ["Italy Bracelet", "Car Logo"], "subcategory": "Car Brands"},
    {"id": 1006, "name_kh": "Car Charm 06", "price": 3000, "image": "/static/images/cc06.jpg", "categories": ["Italy Bracelet", "Car Logo"], "subcategory": "Car Brands"},
    {"id": 1007, "name_kh": "Car Charm 07", "price": 3000, "image": "/static/images/cc07.jpg", "categories": ["Italy Bracelet", "Car Logo"], "subcategory": "Car Brands"}, 
    {"id": 1008, "name_kh": "Car Charm 08", "price": 3000, "image": "/static/images/cc08.jpg", "categories": ["Italy Bracelet", "Car Logo"], "subcategory": "Car Brands"},
    {"id": 1009, "name_kh": "Car Charm 09", "price": 3000, "image": "/static/images/cc09.jpg", "categories": ["Italy Bracelet", "Car Logo"], "subcategory": "Car Brands"},
    {"id": 1010, "name_kh": "Car Charm 10", "price": 3000, "image": "/static/images/cc10.jpg", "categories": ["Italy Bracelet", "Car Logo"], "subcategory": "Car Brands"},
    {"id": 1011, "name_kh": "Car Charm 11", "price": 3000, "image": "/static/images/cc11.jpg", "categories": ["Italy Bracelet", "Car Logo"], "subcategory": "Car Brands"},
    {"id": 1012, "name_kh": "Car Charm 12", "price": 3000, "image": "/static/images/cc12.jpg", "categories": ["Italy Bracelet", "Car Logo"], "subcategory": "Car Brands"},
    {"id": 1013, "name_kh": "Car Charm 13", "price": 3000, "image": "/static/images/cc13.jpg", "categories": ["Italy Bracelet", "Car Logo"], "subcategory": "Car Brands"},
    {"id": 1014, "name_kh": "Car Charm 14", "price": 3000, "image": "/static/images/cc14.jpg", "categories": ["Italy Bracelet", "Car Logo"], "subcategory": "Car Brands"},
    {"id": 1015, "name_kh": "Car Charm 15", "price": 3000, "image": "/static/images/cc15.jpg", "categories": ["Italy Bracelet", "Car Logo"], "subcategory": "Car Brands"},

    # --- FLAGS ---
    *[{"id": 2000+i, "name_kh": f"Flag Charm {i:02d}", "price": 3000, "image": f"/static/images/cf{i:02d}.jpg", "categories": ["Italy Bracelet", "Flag"], "subcategory": "Football"} for i in range(1, 20)],
    
    # --- GEMSTONES ---
    *[{"id": 3000+i, "name_kh": f"Gemstone {i:02d}", "price": 3500 if i < 21 else 5000, "image": f"/static/images/cg{i:02d}.jpg", "categories": ["Italy Bracelet", "Gemstone"], "subcategory": "Gemstones"} for i in range(1, 25)],

    # --- CHAINS ---
    *[{"id": 4000+i, "name_kh": f"Chain {i:02d}", "price": 3000, "image": f"/static/images/charm-chain-{i:02d}.jpg", "categories": ["Italy Bracelet", "Chain"], "subcategory": "Chain"} for i in range(1, 17)],

    # --- FOOTBALL ---
    *[{"id": 5000+i, "name_kh": f"Club Logo {i:02d}", "price": 3000, "image": f"/static/images/charm-footballclub-{i:02d}.jpg", "categories": ["Italy Bracelet", "Football Club Logo"], "subcategory": "Football"} for i in range(1, 16)],

    # --- BLACK LOVER ---
    *[{"id": 6000+i, "name_kh": f"Black {i:02d}", "price": 3000, "image": f"/static/images/cb{i:02d}.jpg", "categories": ["Italy Bracelet", "Black Lover"], "subcategory": "Black Collection"} for i in range(1, 8)],

    # --- ANIMAL / PET ---
    *[{"id": 7000+i, "name_kh": f"Pet {i:02d}", "price": 3000, "image": f"/static/images/charm-animal-{i:02d}.jpg", "categories": ["Italy Bracelet", "Dog&Cat Lover"], "subcategory": "Animals"} for i in range(1, 8)],

    # --- BLUE SEA ---
    *[{"id": 7010+i, "name_kh": f"Blue {i:02d}", "price": 3000, "image": f"/static/images/charm-bluesealover-{i:02d}.jpg", "categories": ["Italy Bracelet", "Blue Sea Lover🌊"], "subcategory": "Blue Collection"} for i in range(1, 16)],

    # --- PINK LOVER ---
    *[{"id": 8000+i, "name_kh": f"Pink {i:02d}", "price": 3000, "image": f"/static/images/cp{i:02d}.jpg", "categories": ["Italy Bracelet", "Pink Lover"], "subcategory": "Pink Collection"} for i in range(1, 10)],

    # --- PINK LETTERS ---
    *[{"id": 9000+i, "name_kh": f"Pink Letter {chr(64+i)}", "price": 1200, "image": f"/static/images/{chr(96+i)}p.jpg", "categories": ["Italy Bracelet", "Pink Letter"], "subcategory": "Letters"} for i in range(1, 27)],

    # --- SILVER LETTERS ---
    *[{"id": 1100+i, "name_kh": f"Silver Letter {chr(64+i)}", "price": 1200, "image": f"/static/images/{chr(96+i)}.jpg", "categories": ["Italy Bracelet", "Letter"], "subcategory": "Letters"} for i in range(1, 27)],

    # --- STEAV ---
    *[{"id": 1200+i, "name_kh": f"Steav {i:02d}", "price": 3000 if i < 13 else 4000, "image": f"/static/images/cm{i:02d}.jpg", "categories": ["Italy Bracelet", "Steav"], "subcategory": "Steav"} for i in range(1, 14)],

    # --- CUTIE ---
    *[{"id": 1400+i, "name_kh": f"Cutie {i:02d}", "price": 3000 if i < 6 else 4000, "image": f"/static/images/cw{i:02d}.jpg", "categories": ["Italy Bracelet", "Cutie"], "subcategory": "Cutie"} for i in range(1, 17)],

    # --- BUBBLE ---
    *[{"id": 1500+i, "name_kh": f"Bubble {i:02d}", "price": 3000, "image": f"/static/images/charm-bubble-{i:02d}.jpg", "categories": ["Italy Bracelet", "Slay💅"], "subcategory": "Bubble"} for i in range(1, 13)],

    # --- CUTE CAT ---
    *[{"id": 1600+i, "name_kh": f"Cute Cat {i:02d}", "price": 3000, "image": f"/static/images/charm-cutecat-{i:02d}.jpg", "categories": ["Italy Bracelet", "Cute Cat"], "subcategory": "Animals"} for i in range(1, 13)],

    # --- ROK JIT ---
    *[{"id": 1700+i, "name_kh": f"Rok Jit {i:02d}", "price": 3000, "image": f"/static/images/charm-rokjit-{i:02d}.jpg", "categories": ["Italy Bracelet", "Rok Jit💔"], "subcategory": "Rok Jit"} for i in range(1, 9)],

    # --- 8 BALL ---
    {"id": 1801, "name_kh": "8 Ball 01", "price": 3000, "image": "/static/images/charm-8ball-01.jpg", "categories": ["Italy Bracelet", "8 Ball 🎱"]},
    {"id": 1802, "name_kh": "8 Ball 02", "price": 3000, "image": "/static/images/charm-8ball-02.jpg", "categories": ["Italy Bracelet", "8 Ball 🎱"]},
    {"id": 1803, "name_kh": "8 Ball 03", "price": 3000, "image": "/static/images/charm-8ball-03.jpg", "categories": ["Italy Bracelet", "8 Ball 🎱"]},

    # --- CHERRY ---
    {"id": 1901, "name_kh": "Cherry 01", "price": 3000, "image": "/static/images/charm-cherry-01.jpg", "categories": ["Italy Bracelet", "Cherry 🍒"]},

    # --- CHRISTMAS ---
    *[{"id": 2000+i, "name_kh": f"Xmas {i:02d}", "price": 3000, "image": f"/static/images/charm-christmas-{i:02d}.jpg", "categories": ["Italy Bracelet", "Christmas 🎄"], "subcategory": "Holiday"} for i in range(1, 10)],
    *[{"id": 2010+i, "name_kh": f"Xmas {i+10}", "price": 3000, "image": f"/static/images/charm-christmas-{i+10}.jpg", "categories": ["Italy Bracelet", "Christmas 🎄"], "subcategory": "Holiday"} for i in range(1, 10)],
    *[{"id": 2020+i, "name_kh": f"Xmas {i+20}", "price": 3000, "image": f"/static/images/charm-christmas-{i+20}.jpg", "categories": ["Italy Bracelet", "Christmas 🎄"], "subcategory": "Holiday"} for i in range(1, 10)],

    # --- FLOWER ---
    *[{"id": 2100+i, "name_kh": f"Flower {i:02d}", "price": 3000, "image": f"/static/images/charm-flower-{i:02d}.jpg", "categories": ["Italy Bracelet", "Flower 🌹"], "subcategory": "Nature"} for i in range(1, 10)],
]

# --- SUBCATEGORIES MAP (Restored for Home Page Navigation) ---
subcategories_map = {
    "Hot Sale": [],
    "LEGO Ninjago": ["Dragon Rising","Building Set","Season 1", "Season 2", "Season 13"],
    "LEGO Anime": ["One Piece","Demon Slayer"],
    "Accessories": ["Gym Bracelet", "Gem Stone Bracelet","Dragon Bracelet","Bracelet"],
    "Keychain": ["Gun Keychains"],
    "LEGO": ["Formula 1"],
    "Toy": ["Lego Ninjago", "One Piece","Lego WWII"],
    "Italy Bracelet": ["All","Football","Gem","Flag","Chain"],
    "Lucky Draw": ["/lucky-draw"], 
}

# --- NAVIGATION MENU ---
NAV_MENU = ["Hot Sale", "LEGO", "Keychain", "Accessories", "Toy", "Italy Bracelet", "Lucky Draw"]

# --- DATABASE MODEL ---
class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name_kh = db.Column(db.String(200), nullable=False)
    price = db.Column(db.Integer, nullable=False)
    image = db.Column(db.String(500), nullable=False)
    categories_str = db.Column(db.String(500), default="") 
    subcategory_str = db.Column(db.String(500), default="") 
    stock = db.Column(db.Integer, default=0)

# --- SYNC ENGINE ---
def sync_catalog():
    try:
        inspector = db.inspect(db.engine)
        if not inspector.has_table("product"):
            db.create_all()
            
        print("🔄 Syncing Catalog...")
        for item in PRODUCT_CATALOG:
            existing = Product.query.get(item['id'])
            cat_str = ", ".join(item.get('categories', []))
            sub_str = item.get('subcategory', 'General')
            
            if existing:
                existing.name_kh = item['name_kh']
                existing.price = item['price']
                existing.image = item['image']
                existing.categories_str = cat_str
                existing.subcategory_str = sub_str
            else:
                new_p = Product(
                    id=item['id'], name_kh=item['name_kh'], price=item['price'],
                    image=item['image'], categories_str=cat_str, subcategory_str=sub_str, stock=0
                )
                db.session.add(new_p)
        db.session.commit()
        print("✅ Sync Complete!")
    except Exception as e:
        print(f"⚠️ Database Error: {e}")

# --- SHOP ROUTES ---

@app.route('/')
def home():
    # Keep behavior from current app (Redirect to Custom Bracelet)
    return redirect(url_for('custom_bracelet'))

@app.route('/category/<category_name>')
def category_view(category_name):
    # Logic for accessing legacy categories if needed
    if category_name == 'Italy Bracelet': return redirect(url_for('custom_bracelet'))
    if category_name == 'Lucky Draw': return redirect(url_for('lucky_draw'))
    
    products = Product.query.filter(Product.categories_str.contains(category_name)).all()
    subs = subcategories_map.get(category_name, [])
    
    return render_template('home.html', 
                           products=products, 
                           current_category=category_name, 
                           menu=NAV_MENU,
                           subcategories=subs,
                           cart=session.get('cart', []))

@app.route('/custom-bracelet')
def custom_bracelet():
    # Filter for Italy Bracelet items for the Studio
    all_products = Product.query.all()
    # Filter items that have 'Italy Bracelet' OR 'Charm' to be safe
    studio_items = [p for p in all_products if "Italy Bracelet" in p.categories_str or "Charm" in p.categories_str]
    
    products_json = [{
        "id": p.id, "name_kh": p.name_kh, "price": p.price, 
        "image": p.image, "stock": p.stock, 
        "categories": p.categories_str.split(', ')
    } for p in studio_items]
    
    return render_template('custom_bracelet.html', products=products_json)

@app.route('/lucky-draw')
def lucky_draw():
    return render_template('minifigure_game.html')

@app.route('/add-to-cart', methods=['POST'])
def add_to_cart():
    p_id = request.form.get('product_id')
    if p_id:
        cart = session.get('cart', [])
        cart.append(p_id)
        session['cart'] = cart
        return jsonify({"success": True, "cart_count": len(cart)})
    return jsonify({"success": False})

# --- ADMIN ROUTES ---

@app.route('/admin/panel')
def admin_panel():
    if not session.get('admin'): return redirect(url_for('admin_login'))
    
    all_products = Product.query.all()
    stats = {
        "total": len(all_products),
        "out": len([p for p in all_products if p.stock <= 0]),
        "low": len([p for p in all_products if 0 < p.stock <= 5])
    }
    
    grouped = {}
    for p in all_products:
        sub = p.subcategory_str if p.subcategory_str else "General"
        if sub not in grouped: grouped[sub] = []
        grouped[sub].append(p)
        
    return render_template('admin_panel.html', grouped=grouped, stats=stats)

@app.route('/admin/api/update-stock', methods=['POST'])
def update_stock():
    if not session.get('admin'): return jsonify({"success": False}), 403
    data = request.json
    p = Product.query.get(data['id'])
    if p:
        p.stock = int(data['amount'])
        db.session.commit()
        return jsonify({"success": True})
    return jsonify({"success": False})

@app.route('/admin/api/process-receipt', methods=['POST'])
def process_receipt():
    """Batch deducts stock based on items in the receipt drawer"""
    if not session.get('admin'): return jsonify({"success": False}), 403
    data = request.json
    
    try:
        items = data.get('items', [])
        for item in items:
            product = Product.query.get(item['id'])
            if product:
                product.stock = max(0, product.stock - int(item['qty']))
        
        db.session.commit()
        return jsonify({"success": True})
    except Exception as e:
        db.session.rollback()
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        if request.form['username'] == ADMIN_USER and request.form['password'] == ADMIN_PASS:
            session['admin'] = True
            return redirect(url_for('admin_panel'))
    return render_template('admin_login.html')

@app.route('/admin/logout')
def logout():
    session.pop('admin', None)
    return redirect(url_for('admin_login'))

@app.errorhandler(403)
def forbidden(e):
    return "Access Denied: Your IP is blocked.", 403

# --- STARTUP ---
with app.app_context():
    try:
        db.create_all()
        sync_catalog()
    except:
        pass

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port, debug=True)
