import os
import time
from flask import Flask, render_template, request, redirect, url_for, jsonify, session
from flask_sqlalchemy import SQLAlchemy

# --- INITIALIZATION ---
app = Flask(__name__)

# --- SECURE CONFIG (Fetched from Render Environment Variables) ---
# Set these in Render Dashboard -> Environment to stop GitHub security alerts
app.secret_key = os.environ.get('SECRET_KEY', 'somphea_reak_studio_pro_2025')
ADMIN_PASS = os.environ.get('ADMIN_PASS', 'Thesong_Admin@2022?!$')
BOT_TOKEN = os.environ.get('TELEGRAM_BOT_TOKEN', '7528700801:AAGTvXjk5qPBnq_qx69ZOW4RMLuGy40w5k8')
CHAT_ID = os.environ.get('TELEGRAM_CHAT_ID', '-1002654437316')

# --- DATABASE SETUP (The Old Way) ---
basedir = os.path.abspath(os.path.dirname(__file__))
db_path = os.path.join(basedir, 'shop_v2.db')
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + db_path
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# --- MODELS ---
class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200))
    price = db.Column(db.Integer)
    image = db.Column(db.String(500))
    category = db.Column(db.String(100))
    stock = db.Column(db.Integer, default=999)

class Setting(db.Model):
    key = db.Column(db.String(50), primary_key=True)
    value = db.Column(db.String(50))

# --- SPEED OPTIMIZATION (Memory Cache) ---
# This stops the lag by keeping data in RAM instead of reading the disk every time.
MEM_CACHE = {
    "products": [],
    "subcategories": [],
    "last_sync": 0,
    "ttl": 300 # Refresh RAM from DB every 5 minutes
}

def get_data_fast(force=False):
    global MEM_CACHE
    now = time.time()
    if not force and MEM_CACHE["products"] and (now - MEM_CACHE["last_sync"] < MEM_CACHE["ttl"]):
        return MEM_CACHE["products"], MEM_CACHE["subcategories"]
    
    # Fetch from SQLite
    all_p = Product.query.all()
    categories_query = db.session.query(Product.category).distinct().all()
    subcats = [cat[0] for cat in categories_query if cat[0]]
    
    MEM_CACHE["products"] = all_p
    MEM_CACHE["subcategories"] = subcats
    MEM_CACHE["last_sync"] = now
    return all_p, subcats

# --- ROUTES ---

@app.route('/')
def home():
    all_p, subcategories = get_data_fast()
    return render_template('home.html', products=all_p, subcategories=subcategories)

@app.route('/custom-bracelet')
def custom_bracelet():
    return render_template('custom_bracelet.html')

@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        if request.form.get('password') == ADMIN_PASS:
            session['admin'] = True
            return redirect(url_for('admin_panel'))
    return render_template('admin_login.html')

@app.route('/admin/logout')
def admin_logout():
    session.pop('admin', None)
    return redirect(url_for('home'))

@app.route('/admin/panel')
def admin_panel():
    if not session.get('admin'):
        return redirect(url_for('admin_login'))
    
    # Admin Panel always gets fresh data directly from SQLite
    all_p = Product.query.order_by(Product.name.asc()).all()
    grouped = {}
    for p in all_p:
        cat = p.category or "General"
        if cat not in grouped: grouped[cat] = []
        grouped[cat].append(p)
    override = db.session.get(Setting, 'stock_override')
    return render_template('admin_panel.html', grouped=grouped, override=override.value if override else "off")

# --- API ENDPOINTS ---

@app.route('/api/get-data')
def get_data():
    all_p, _ = get_data_fast()
    override = db.session.get(Setting, 'stock_override')
    return jsonify({
        "stock": {p.id: p.stock for p in all_p},
        "override": override.value if override else "off"
    })

@app.route('/admin/api/update-stock', methods=['POST'])
def update_stock():
    if not session.get('admin'): return jsonify(success=False), 403
    data = request.json
    p = db.session.get(Product, data['id'])
    if p:
        p.stock = int(data['amount'])
        db.session.commit()
        get_data_fast(force=True) # Refresh memory
    return jsonify(success=True)

@app.route('/admin/api/toggle-override', methods=['POST'])
def toggle_override():
    if not session.get('admin'): return jsonify(success=False), 403
    val = request.json.get('value')
    sett = db.session.get(Setting, 'stock_override')
    if not sett:
        sett = Setting(key='stock_override', value=val)
        db.session.add(sett)
    else: sett.value = val
    db.session.commit()
    return jsonify(success=True)

@app.route('/admin/api/process-receipt', methods=['POST'])
def process_receipt():
    if not session.get('admin'): return jsonify(success=False), 403
    data = request.json
    for item in data.get('items', []):
        p = db.session.get(Product, item['id'])
        if p:
            p.stock = max(0, p.stock - int(item['qty']))
    db.session.commit()
    get_data_fast(force=True) # Refresh memory
    return jsonify(success=True)

@app.route('/api/sync', methods=['POST'])
def sync_catalog():
    data = request.json
    items = data.get('items', [])
    existing_ids = {p.id for p in Product.query.with_entities(Product.id).all()}
    for item in items:
        if item['id'] not in existing_ids:
            db.session.add(Product(
                id=item['id'], 
                name=item.get('name_kh') or item['name'], 
                price=item['price'], 
                image=item['image'], 
                category=item['categories'][0] if item.get('categories') else "General"
            ))
    db.session.commit()
    get_data_fast(force=True) # Refresh memory
    return jsonify(success=True)

@app.route('/admin/api/reset-all', methods=['POST'])
def reset_all():
    if not session.get('admin'): return jsonify(success=False), 403
    Product.query.update({Product.stock: 999})
    db.session.commit()
    get_data_fast(force=True) # Refresh memory
    return jsonify(success=True)

# --- BOOTSTRAP ---
with app.app_context():
    db.create_all()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))