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

# --- ADMIN CONFIG ---
ADMIN_USER = 'AdminSompheaReakVitou'
ADMIN_PASS = 'Thesong_Admin@2022?!$'

# ==========================================
# 1. PRODUCT CATALOG (CLEANED LIST)
# ==========================================
PRODUCT_CATALOG = [
    # --- CHARMS ---
    {"id": 1, "name_kh": "Silver Charm", "price": 400, "image": "/static/images/c01.jpg", "categories": ["Charm"], "subcategory": "General"},

    # --- F1 LOGOS ---
    {"id": 1100, "name_kh": "Classic F1 Logo", "price": 3000, "image": "/static/images/charm-f1–101.jpg", "categories": ["Class F1🏎️"], "subcategory": "F1 Logos"},
    {"id": 1191, "name_kh": "Classic F1", "price": 3000, "image": "/static/images/charm-chain-03.jpg", "categories": ["Class F1🏎️"], "subcategory": "F1 Logos"},
    {"id": 1192, "name_kh": "Classic F1 - Ferri", "price": 3000, "image": "/static/images/charm-f1-301.jpg", "categories": ["Class F1🏎️"], "subcategory": "F1 Logos"},
    
    # --- CAR LOGOS ---
    {"id": 1001, "name_kh": "Car Charm 01", "price": 3000, "image": "/static/images/cc01.jpg", "categories": ["Car Logo"], "subcategory": "Car Brands"},
    {"id": 1002, "name_kh": "Car Charm 02", "price": 3000, "image": "/static/images/cc02.jpg", "categories": ["Car Logo"], "subcategory": "Car Brands"},

    # --- FLAGS ---
    {"id": 2001, "name_kh": "Flag Charm 01", "price": 3000, "image": "/static/images/cf01.jpg", "categories": ["Flag"], "subcategory": "National Flags"},
    {"id": 2002, "name_kh": "Flag Charm 02", "price": 3000, "image": "/static/images/cf02.jpg", "categories": ["Flag"], "subcategory": "National Flags"},

    # --- GEMSTONES ---
    {"id": 3001, "name_kh": "Gemstone Charm 01", "price": 3500, "image": "/static/images/cg01.jpg", "categories": ["Gemstone"], "subcategory": "Gemstones"},
    
    # --- CHAINS ---
    {"id": 4001, "name_kh": "Chain Charm 01", "price": 3000, "image": "/static/images/charm-chain-01.jpg", "categories": ["Chain"], "subcategory": "Chains"},

    # --- FOOTBALL CLUBS ---
    {"id": 5001, "name_kh": "Barcelona", "price": 3000, "image": "/static/images/charm-footballclub-01.jpg", "categories": ["Football Club Logo"], "subcategory": "Football"},
    {"id": 5002, "name_kh": "Real Madrid", "price": 3000, "image": "/static/images/charm-footballclub-02.jpg", "categories": ["Football Club Logo"], "subcategory": "Football"},

    # --- LETTERS ---
    {"id": 1101, "name_kh": "Letter A", "price": 1200, "image": "/static/images/a.jpg", "categories": ["Letter"], "subcategory": "Letters"},
    {"id": 1102, "name_kh": "Letter B", "price": 1200, "image": "/static/images/b.jpg", "categories": ["Letter"], "subcategory": "Letters"},

    # --- CHRISTMAS ---
    {"id": 2001, "name_kh": "Christmas 01", "price": 3000, "image": "/static/images/charm-christmas-01.jpg", "categories": ["Christmas 🎄"], "subcategory": "Holiday"},
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
        print(f"❌ Error during sync: {e}")

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


