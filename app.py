App.py Perfect 

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
# 1. PRODUCT CATALOG
# ==========================================
PRODUCT_CATALOG = [
    # --- Charms ---
    {"id": 1, "name_kh": "Silver Charm", "price": 400, "image": "/static/images/c01.jpg", "categories": ["Charm"], "subcategory": "General"},

    # --- F1 Logos ---
    {"id": 1100, "name_kh": "Classic F1 Logo", "price": 3000, "image": "/static/images/charm-f1–101.jpg", "categories": ["Class F1🏎️"], "subcategory": "F1 Logos"},
    {"id": 1191, "name_kh": "Classic F1", "price": 3000, "image": "/static/images/charm-chain-03.jpg", "categories": ["Class F1🏎️"], "subcategory": "F1 Logos"},
    
    # --- Car Logos ---
    {"id": 1001, "name_kh": "Car Charm 01", "price": 3000, "image": "/static/images/cc01.jpg", "categories": ["Car Logo"], "subcategory": "Car Brands"},
    {"id": 1002, "name_kh": "Car Charm 02", "price": 3000, "image": "/static/images/cc02.jpg", "categories": ["Car Logo"], "subcategory": "Car Brands"},

    # --- Flags ---
    {"id": 2001, "name_kh": "Flag Charm 01", "price": 3000, "image": "/static/images/cf01.jpg", "categories": ["Flag"], "subcategory": "National Flags"},

    # --- Gemstones ---
    {"id": 3001, "name_kh": "Gemstone Charm 01", "price": 3500, "image": "/static/images/cg01.jpg", "categories": ["Gemstone"], "subcategory": "Gemstones"},
    
    # --- Chains ---
    {"id": 4001, "name_kh": "Chain Charm 01", "price": 3000, "image": "/static/images/charm-chain-01.jpg", "categories": ["Chain"], "subcategory": "Chains"},

    # --- Football ---
    {"id": 5001, "name_kh": "Barcelona", "price": 3000, "image": "/static/images/charm-footballclub-01.jpg", "categories": ["Football Club Logo"], "subcategory": "Football"},

    # --- Letters ---
    {"id": 1101, "name_kh": "Letter A", "price": 1200, "image": "/static/images/a.jpg", "categories": ["Letter"], "subcategory": "Letters"},
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
    try:
        # Check if table exists to avoid crash
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
    except Exception as e:
        print(f"⚠️ Database Error (Ignored to keep app alive): {e}")

# --- ROUTES ---
@app.route('/')
def home():
    return redirect(url_for('custom_bracelet'))

@app.route('/custom-bracelet')
def custom_bracelet():
    try:
        all_products = Product.query.all()
        products_json = [{
            "id": p.id, "name_kh": p.name_kh, "price": p.price, 
            "image": p.image, "stock": p.stock, 
            "categories": p.categories_str.split(', ')
        } for p in all_products]
    except:
        products_json = [] # Fallback if DB fails
    
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

# --- INIT & RUN ---
with app.app_context():
    try:
        db.create_all()
        sync_catalog()
    except:
        pass

if __name__ == '__main__':
    # CRITICAL FIX FOR RENDER: Bind to 0.0.0.0 and use PORT env var
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port, debug=True)



