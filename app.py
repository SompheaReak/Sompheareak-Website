import os
import requests
from flask import Flask, render_template, request, redirect, url_for, jsonify, session
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
# Secure key for sessions
app.secret_key = os.environ.get('SECRET_KEY', 'somphea_reak_2025_studio_pro')

# --- 1. DATABASE SETUP ---
# Use absolute paths to ensure the server finds the DB file
basedir = os.path.abspath(os.path.dirname(__file__))
db_path = os.path.join(basedir, 'shop_v2.db')
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + db_path
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# --- 2. MODELS ---
class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200))
    price = db.Column(db.Integer)
    image = db.Column(db.String(500))
    category = db.Column(db.String(100))
    subcategory = db.Column(db.String(100))
    stock = db.Column(db.Integer, default=0)

class Setting(db.Model):
    key = db.Column(db.String(50), primary_key=True)
    value = db.Column(db.String(50))

# --- 3. CONFIGURATION ---
ADMIN_PASS = 'Thesong_Admin@2022?!$'
BOT_TOKEN = "7528700801:AAGTvXjk5qPBnq_qx69ZOW4RMLuGy40w5k8"
CHAT_ID = "-1002654437316"

# --- 4. HELPERS ---
def get_menu():
    try:
        cats = db.session.query(Product.category).distinct().all()
        return [c[0] for c in cats if c[0]]
    except:
        return []

def send_telegram(message):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = {"chat_id": CHAT_ID, "text": message, "parse_mode": "HTML"}
    try:
        requests.post(url, json=payload, timeout=5)
    except:
        pass

# --- 5. MAIN ROUTES ---

@app.route('/')
def home():
    # Make sure your file is named 'custom-bracelet.html' in the templates folder
    return render_template('custom-bracelet.html')

@app.route('/shop')
def shop():
    menu = get_menu()
    products = Product.query.all()
    return render_template('home.html', products=products, menu=menu, current_category="All Products")

@app.route('/category/<cat_name>')
def category(cat_name):
    menu = get_menu()
    products = Product.query.filter_by(category=cat_name).all()
    subs = db.session.query(Product.subcategory).filter_by(category=cat_name).distinct().all()
    subcategories = [s[0] for s in subs if s[0]]
    return render_template('home.html', products=products, menu=menu, current_category=cat_name, subcategories=subcategories)

# --- 6. API FOR STUDIO ---

@app.route('/api/get-data')
def get_data():
    # Sends both stock numbers AND the Master Switch status
    override = Setting.query.get('stock_override')
    return jsonify({
        "stock": {p.id: p.stock for p in Product.query.all()},
        "override": override.value if override else "off"
    })

@app.route('/api/sync', methods=['POST'])
def sync_catalog():
    data = request.json
    items = data.get('items', [])
    for item in items:
        p = Product.query.get(item['id'])
        # Map 'name_kh' from JS to 'name' in DB
        name_val = item.get('name_kh') or item.get('name') or "Item"
        if not p:
            new_p = Product(
                id=item['id'], name=name_val, price=item['price'], 
                image=item['image'], category=item['categories'][0], 
                subcategory=item.get('subcategory', 'General'), stock=0
            )
            db.session.add(new_p)
        else:
            # Update image and name to keep Admin Panel current
            p.image = item['image']
            p.name = name_val
    db.session.commit()
    return jsonify(success=True)

# --- 7. ADMIN PANEL ---

@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        if request.form.get('password') == ADMIN_PASS:
            session['admin'] = True
            return redirect(url_for('admin_panel'))
    return render_template('admin_login.html')

@app.route('/admin/panel')
def admin_panel():
    if not session.get('admin'): return redirect(url_for('admin_login'))
    all_p = Product.query.all()
    grouped = {}
    for p in all_p:
        cat = p.category or "General"
        if cat not in grouped: grouped[cat] = []
        grouped[cat].append(p)
    override = Setting.query.get('stock_override')
    return render_template('admin_panel.html', grouped=grouped, override=override.value if override else "off")

@app.route('/admin/api/update-stock', methods=['POST'])
def update_stock():
    if not session.get('admin'): return jsonify(success=False), 403
    data = request.json
    p = Product.query.get(data['id'])
    if p:
        p.stock = int(data['amount'])
        db.session.commit()
        return jsonify(success=True)
    return jsonify(success=False)

@app.route('/admin/api/toggle-override', methods=['POST'])
def toggle_override():
    if not session.get('admin'): return jsonify(success=False), 403
    val = request.json.get('value')
    sett = Setting.query.get('stock_override')
    if not sett: sett = Setting(key='stock_override', value=val)
    else: sett.value = val
    db.session.add(sett)
    db.session.commit()
    return jsonify(success=True)

# --- 8. INITIALIZATION ---
with app.app_context():
    db.create_all()

if __name__ == "__main__":
    # Port 5000 is default, but Render uses 'PORT' environment variable
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)

