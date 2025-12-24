import os
import requests
from flask import Flask, render_template, request, redirect, url_for, jsonify, session
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.secret_key = 'somphea_reak_fixed_key_2025'

# --- DATABASE SETUP ---
basedir = os.path.abspath(os.path.dirname(__file__))
db_path = os.path.join(basedir, 'shop.db')
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + db_path
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# --- CONFIGURATION ---
ADMIN_USER = 'AdminSompheaReakVitou'
ADMIN_PASS = 'Thesong_Admin@2022?!$'

# ==========================================
# 1. PRODUCT CATALOG (PYTHON FORMAT)
# ==========================================
# NOTICE: Comments use '#' not '//'
PRODUCT_CATALOG = [
    # --- Charms ---
    {"id": 1, "name_kh": "Silver Charm", "price": 400, "image": "/static/images/c01.jpg", "categories": ["Charm"], "subcategory": "General"},

    # --- F1 Logos ---
    {"id": 1100, "name_kh": "Classic F1 Logo", "price": 3000, "image": "/static/images/charm-f1–101.jpg", "categories": ["Class F1🏎️"], "subcategory": "F1 Logos"},
    {"id": 1191, "name_kh": "Classic F1", "price": 3000, "image": "/static/images/charm-chain-03.jpg", "categories": ["Class F1🏎️"], "subcategory": "F1 Logos"},
    {"id": 1192, "name_kh": "Classic F1 - Ferri", "price": 3000, "image": "/static/images/charm-f1-301.jpg", "categories": ["Class F1🏎️"], "subcategory": "F1 Logos"},
    {"id": 1193, "name_kh": "Classic F1 - Porsche", "price": 3000, "image": "/static/images/charm-f1-302.jpg", "categories": ["Class F1🏎️"], "subcategory": "F1 Logos"},
    {"id": 1194, "name_kh": "Classic F1 - BMW", "price": 3000, "image": "/static/images/charm-f1-303.jpg", "categories": ["Class F1🏎️"], "subcategory": "F1 Logos"},
    {"id": 1195, "name_kh": "Classic F1 - BMW", "price": 3000, "image": "/static/images/charm-f1-304.jpg", "categories": ["Class F1🏎️"], "subcategory": "F1 Logos"},
    {"id": 1101, "name_kh": "Classic F1 - Mercedes", "price": 3000, "image": "/static/images/cc15.jpg", "categories": ["Class F1🏎️"], "subcategory": "F1 Logos"},
    {"id": 1102, "name_kh": "Classic F1 - Ferrari", "price": 3000, "image": "/static/images/cc04.jpg", "categories": ["Class F1🏎️"], "subcategory": "F1 Logos"},
    {"id": 1103, "name_kh": "Classic F1 - Porsche", "price": 3000, "image": "/static/images/cc12.jpg", "categories": ["Class F1🏎️"], "subcategory": "F1 Logos"},
    {"id": 1104, "name_kh": "Classic F1 - BMW", "price": 3000, "image": "/static/images/cc06.jpg", "categories": ["Class F1🏎️"], "subcategory": "F1 Logos"},

    # --- Pink F1 ---
    {"id": 1200, "name_kh": "Pink F1 Logo", "price": 3000, "image": "/static/images/charm-f1-201.jpg", "categories": ["Pink F1🏎️"], "subcategory": "Pink F1"},
    {"id": 1291, "name_kh": "Classic F1 - Mercedes", "price": 3000, "image": "/static/images/charm-chain-03.jpg", "categories": ["pink F1🏎️"], "subcategory": "Pink F1"},
    {"id": 1292, "name_kh": "Classic F1 - Ferri", "price": 3000, "image": "/static/images/charm-f1-301.jpg", "categories": ["Pink F1🏎️"], "subcategory": "Pink F1"},
    
    # --- Car Logos ---
    {"id": 1001, "name_kh": "Car Charm 01", "price": 3000, "image": "/static/images/cc01.jpg", "categories": ["Car Logo"], "subcategory": "Car Brands"},
    {"id": 1002, "name_kh": "Car Charm 02", "price": 3000, "image": "/static/images/cc02.jpg", "categories": ["Car Logo"], "subcategory": "Car Brands"},
    {"id": 1003, "name_kh": "Car Charm 03", "price": 3000, "image": "/static/images/cc03.jpg", "categories": ["Car Logo"], "subcategory": "Car Brands"},
    {"id": 1004, "name_kh": "Car Charm 04", "price": 3000, "image": "/static/images/cc04.jpg", "categories": ["Car Logo"], "subcategory": "Car Brands"},
    {"id": 1005, "name_kh": "Car Charm 05", "price": 3000, "image": "/static/images/cc05.jpg", "categories": ["Car Logo"], "subcategory": "Car Brands"},
    
    # --- Flags ---
    {"id": 2001, "name_kh": "Flag Charm 01", "price": 3000, "image": "/static/images/cf01.jpg", "categories": ["Flag"], "subcategory": "National Flags"},
    {"id": 2002, "name_kh": "Flag Charm 02", "price": 3000, "image": "/static/images/cf02.jpg", "categories": ["Flag"], "subcategory": "National Flags"},
    {"id": 2003, "name_kh": "Flag Charm 03", "price": 3000, "image": "/static/images/cf03.jpg", "categories": ["Flag"], "subcategory": "National Flags"},
    {"id": 2004, "name_kh": "Flag Charm 04", "price": 3000, "image": "/static/images/cf04.jpg", "categories": ["Flag"], "subcategory": "National Flags"},
    {"id": 2005, "name_kh": "Flag Charm 05", "price": 3000, "image": "/static/images/cf05.jpg", "categories": ["Flag"], "subcategory": "National Flags"},

    # --- Gemstones ---
    {"id": 3001, "name_kh": "Gemstone Charm 01", "price": 3500, "image": "/static/images/cg01.jpg", "categories": ["Gemstone"], "subcategory": "Gemstones"},
    {"id": 3002, "name_kh": "Gemstone Charm 02", "price": 3500, "image": "/static/images/cg02.jpg", "categories": ["Gemstone"], "subcategory": "Gemstones"},
    
    # --- Chains ---
    {"id": 4001, "name_kh": "Chain Charm 01", "price": 3000, "image": "/static/images/charm-chain-01.jpg", "categories": ["Chain"], "subcategory": "Chains"},
    {"id": 4002, "name_kh": "Chain Charm 02", "price": 3000, "image": "/static/images/charm-chain-02.jpg", "categories": ["Chain"], "subcategory": "Chains"},

    # --- Football Clubs ---
    {"id": 5001, "name_kh": "Barcelona", "price": 3000, "image": "/static/images/charm-footballclub-01.jpg", "categories": ["Football Club Logo"], "subcategory": "Football"},
    {"id": 5002, "name_kh": "Real Madrid", "price": 3000, "image": "/static/images/charm-footballclub-02.jpg", "categories": ["Football Club Logo"], "subcategory": "Football"},

    # --- Black Lover ---
    {"id": 6001, "name_kh": "Black Charm 01", "price": 3000, "image": "/static/images/cb01.jpg", "categories": ["Black Lover"], "subcategory": "Black Series"},
    {"id": 6002, "name_kh": "Black Charm 02", "price": 3000, "image": "/static/images/cb02.jpg", "categories": ["Black Lover"], "subcategory": "Black Series"},

    # --- Animals ---
    {"id": 7001, "name_kh": "Cat&Dog Charm 01", "price": 3000, "image": "/static/images/charm-animal-01.jpg", "categories": ["Dog&Cat Lover"], "subcategory": "Animals"},
    {"id": 7002, "name_kh": "Cat&Dog Charm 02", "price": 3000, "image": "/static/images/charm-animal-02.jpg", "categories": ["Dog&Cat Lover"], "subcategory": "Animals"},

    # --- Blue Sea ---
    {"id": 7011, "name_kh": "Blue Sea Lover 01", "price": 3000, "image": "/static/images/charm-bluesealover-01.jpg", "categories": ["Blue Sea Lover🌊"], "subcategory": "Blue Sea"},
    
    # --- Pink Lover ---
    {"id": 8001, "name_kh": "Pink Charm 01", "price": 3000, "image": "/static/images/cp01.jpg", "categories": ["Pink Lover"], "subcategory": "Pink Series"},

    # --- Letters ---
    {"id": 9001, "name_kh": "Pink Letter A", "price": 1200, "image": "/static/images/ap.jpg", "categories": ["Pink Letter"], "subcategory": "Pink Letters"},
    {"id": 1101, "name_kh": "Silver Letter A", "price": 1200, "image": "/static/images/a.jpg", "categories": ["Letter"], "subcategory": "Silver Letters"},
    
    # --- Steav ---
    {"id": 1201, "name_kh": "Steav Charm 01", "price": 3000, "image": "/static/images/cm01.jpg", "categories": ["Steav"], "subcategory": "Steav Style"},

    # --- Cartoon ---
    {"id": 1301, "name_kh": "Cartoon Charm", "price": 3000, "image": "/static/images/ct01.jpg", "categories": ["Cartoon"], "subcategory": "Cartoons"},

    # --- Cutie ---
    {"id": 1401, "name_kh": "Cutie Charm 01", "price": 3000, "image": "/static/images/cw01.jpg", "categories": ["Cutie"], "subcategory": "Cutie Series"},

    # --- Bubble ---
    {"id": 1501, "name_kh": "Bubble Charm 01", "price": 3000, "image": "/static/images/charm-bubble-01.jpg", "categories": ["Slay💅"], "subcategory": "Bubble"},

    # --- Cute Cat ---
    {"id": 1601, "name_kh": "Cute Cat 01", "price": 3000, "image": "/static/images/charm-cutecat-01.jpg", "categories": ["Cute Cat"], "subcategory": "Cats"},

    # --- Rok Jit ---
    {"id": 1701, "name_kh": "Rok Jit 01", "price": 3000, "image": "/static/images/charm-rokjit-01.jpg", "categories": ["Rok Jit💔"], "subcategory": "Rok Jit"},

    # --- 8 Ball ---
    {"id": 1801, "name_kh": "8 Ball 01", "price": 3000, "image": "/static/images/charm-8ball-01.jpg", "categories": ["8 Ball 🎱"], "subcategory": "8 Ball"},

    # --- Cherry ---
    {"id": 1901, "name_kh": "Cherry 01", "price": 3000, "image": "/static/images/charm-cherry-01.jpg", "categories": ["Cherry 🍒"], "subcategory": "Fruits"},

    # --- Christmas ---
    {"id": 2001, "name_kh": "Christmas 01", "price": 3000, "image": "/static/images/charm-christmas-01.jpg", "categories": ["Christmas 🎄"], "subcategory": "Holiday"},

    # --- Flower ---
    {"id": 2101, "name_kh": "Flower 01", "price": 3000, "image": "/static/images/charm-flower-01.jpg", "categories": ["Flower 🌹"], "subcategory": "Flowers"},
]

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
    print("🔄 Syncing Product Catalog...")
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
                id=item['id'],
                name_kh=item['name_kh'],
                price=item['price'],
                image=item['image'],
                categories_str=cat_str,
                subcategory_str=sub_str,
                stock=0
            )
            db.session.add(new_p)
    db.session.commit()
    print("✅ Sync Complete!")

# --- ROUTES ---

@app.route('/')
def home():
    return redirect(url_for('custom_bracelet'))

@app.route('/custom-bracelet')
def custom_bracelet():
    all_products = Product.query.all()
    products_json = [{
        "id": p.id, "name_kh": p.name_kh, "price": p.price, 
        "image": p.image, "stock": p.stock, 
        "categories": p.categories_str.split(', ')
    } for p in all_products]
    
    is_admin = session.get('admin', False)
    return render_template('custom_bracelet.html', products=products_json, is_admin=is_admin)

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

@app.route('/admin/api/sell-items', methods=['POST'])
def sell_items():
    if not session.get('admin'): return jsonify({"success": False, "msg": "Unauthorized"}), 403
    data = request.json
    ids = data.get('ids', [])
    for pid in ids:
        p = Product.query.get(pid)
        if p and p.stock > 0:
            p.stock -= 1
    db.session.commit()
    return jsonify({"success": True})

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

# --- INIT ---
with app.app_context():
    db.create_all()
    sync_catalog()

if __name__ == '__main__':
    app.run(debug=True, port=5000)


