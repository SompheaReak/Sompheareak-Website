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
