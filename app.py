import os
import time
import json
import re
from flask import Flask, render_template, request, redirect, url_for, jsonify, session
from flask_sqlalchemy import SQLAlchemy

# --- INITIALIZATION ---
app = Flask(__name__)

# --- SECURE CONFIG ---
app.secret_key = os.environ.get('SECRET_KEY', 'somphea_reak_studio_pro_2025')
ADMIN_PASS = os.environ.get('ADMIN_PASS', 'Thesong_Admin@2022?!$')

# --- DATABASE SETUP ---
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
    # Added subcategory to store things like "Season 1", "Formula 1"
    subcategory = db.Column(db.String(200)) 
    stock = db.Column(db.Integer, default=999)

class Setting(db.Model):
    key = db.Column(db.String(50), primary_key=True)
    value = db.Column(db.String(50))

# --- MEMORY CACHE ---
MEM_CACHE = {
    "products": [],
    "subcategories": [],
    "last_sync": 0,
    "ttl": 300
}

def get_data_fast(force=False):
    global MEM_CACHE
    now = time.time()
    if not force and MEM_CACHE["products"] and (now - MEM_CACHE["last_sync"] < MEM_CACHE["ttl"]):
        return MEM_CACHE["products"], MEM_CACHE["subcategories"]
    
    all_p = Product.query.all()
    categories_query = db.session.query(Product.category).distinct().all()
    subcats = [cat[0] for cat in categories_query if cat[0]]
    
    MEM_CACHE["products"] = all_p
    MEM_CACHE["subcategories"] = subcats
    MEM_CACHE["last_sync"] = now
    return all_p, subcats

# --- LEGO SORTING LOGIC ---
def natural_sort_key(s):
    """Sorts strings like 'Season 1', 'Season 2', 'Season 10' correctly"""
    return [int(text) if text.isdigit() else text.lower()
            for text in re.split('([0-9]+)', s)]

def organize_lego(products):
    data = {
        "ninjago": {},
        "one_piece": [],
        "f1": [],
        "sets": [],
        "military": [],
        "other": []
    }
    
    for p in products:
        # Check if it's a LEGO or Toy product
        cat_str = (p.category or "").lower()
        sub_str = (p.subcategory or "").lower()
        
        if "lego" not in cat_str and "toy" not in cat_str and "lego" not in sub_str:
            continue

        # 1. NINJAGO
        if "ninjago" in cat_str or "ninjago" in sub_str:
            # Extract Season Name
            season = "General"
            if p.subcategory:
                # Assuming subcategory is stored like "Lego Ninjago,Season 1"
                parts = p.subcategory.split(',')
                for part in parts:
                    if "Season" in part or "Dragon Rising" in part or "Pilot" in part:
                        season = part.strip()
                        break
            
            if season not in data["ninjago"]:
                data["ninjago"][season] = []
            data["ninjago"][season].append(p)
        
        # 2. ONE PIECE
        elif "one piece" in sub_str or "anime" in cat_str:
            data["one_piece"].append(p)
            
        # 3. F1
        elif "formula 1" in sub_str or "f1" in sub_str or "speed" in sub_str:
            data["f1"].append(p)
            
        # 4. BUILDING SETS
        elif "building set" in sub_str or "set" in sub_str:
            data["sets"].append(p)

        # 5. MILITARY
        elif "wwii" in sub_str or "military" in sub_str:
            data["military"].append(p)
            
        else:
            data["other"].append(p)

    # Sort Ninjago Seasons
    sorted_seasons = sorted(data["ninjago"].keys(), key=natural_sort_key)
    data["ninjago_sorted"] = [(s, data["ninjago"][s]) for s in sorted_seasons]
    
    return data

# --- ROUTES ---

@app.route('/')
def home():
    all_p, subcategories = get_data_fast()
    return render_template('home.html', products=all_p, subcategories=subcategories)

@app.route('/lego')
def lego_world():
    all_p, _ = get_data_fast()
    lego_data = organize_lego(all_p)
    return render_template('lego.html', data=lego_data)

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
    if not session.get('admin'): return redirect(url_for('admin_login'))
    all_p = Product.query.order_by(Product.name.asc()).all()
    grouped = {}
    for p in all_p:
        cat = p.category or "General"
        if cat not in grouped: grouped[cat] = []
        grouped[cat].append(p)
    override = db.session.get(Setting, 'stock_override')
    return render_template('admin_panel.html', grouped=grouped, override=override.value if override else "off")

# --- API ---
@app.route('/api/get-data')
def get_data():
    all_p, _ = get_data_fast()
    override = db.session.get(Setting, 'stock_override')
    return jsonify({
        "stock": {p.id: p.stock for p in all_p},
        "override": override.value if override else "off"
    })

@app.route('/api/sync', methods=['POST'])
def sync_catalog():
    data = request.json
    items = data.get('items', [])
    existing_ids = {p.id for p in Product.query.with_entities(Product.id).all()}
    
    for item in items:
        # Handle Subcategory List -> String conversion
        sub = item.get('subcategory')
        if isinstance(sub, list):
            sub = ",".join(sub)
        
        if item['id'] not in existing_ids:
            db.session.add(Product(
                id=item['id'], 
                name=item.get('name_kh') or item['name'], 
                price=item['price'], 
                image=item['image'], 
                category=item['categories'][0] if item.get('categories') else "General",
                subcategory=sub
            ))
        else:
            # Optional: Update existing items if needed (useful for adding subcategory to old items)
            p = db.session.get(Product, item['id'])
            p.subcategory = sub
            
    db.session.commit()
    get_data_fast(force=True)
    return jsonify(success=True)

@app.route('/admin/api/reset-all', methods=['POST'])
def reset_all():
    if not session.get('admin'): return jsonify(success=False), 403
    Product.query.update({Product.stock: 999})
    db.session.commit()
    get_data_fast(force=True)
    return jsonify(success=True)

@app.route('/admin/api/update-stock', methods=['POST'])
def update_stock():
    if not session.get('admin'): return jsonify(success=False), 403
    data = request.json
    p = db.session.get(Product, data['id'])
    if p:
        p.stock = int(data['amount'])
        db.session.commit()
        get_data_fast(force=True)
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
        if p: p.stock = max(0, p.stock - int(item['qty']))
    db.session.commit()
    get_data_fast(force=True)
    return jsonify(success=True)

with app.app_context():
    db.create_all()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))


