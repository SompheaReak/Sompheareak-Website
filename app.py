import os
import requests
from flask import Flask, render_template, request, redirect, url_for, jsonify, session
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.secret_key = 'somphea_reak_ultimate_key_2025'

# --- DATABASE SETUP ---
basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'shop.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# --- CONFIGURATION ---
ADMIN_USER = 'AdminSompheaReakVitou'
ADMIN_PASS = 'Thesong_Admin@2022?!$'

# ==========================================
# 1. PRODUCT CATALOG (ADD ITEMS HERE)
# ==========================================
# You write the code here -> It appears in Admin Panel
PRODUCT_CATALOG = [
    # --- F1 LOGOS ---
    {"id": 1100, "name_kh": "Classic F1 Logo", "price": 3000, "image": "/static/images/charm-f1–101.jpg", "categories": ["Class F1🏎️"], "subcategory": "F1 Logos"},
    {"id": 1191, "name_kh": "Classic F1", "price": 3000, "image": "/static/images/charm-chain-03.jpg", "categories": ["Class F1🏎️"], "subcategory": "F1 Logos"},
    
    # --- CAR LOGOS ---
    {"id": 1001, "name_kh": "Car Charm 01", "price": 3000, "image": "/static/images/cc01.jpg", "categories": ["Car Logo"], "subcategory": "Car Brands"},
    
    # --- FLAGS ---
    {"id": 2001, "name_kh": "Flag Charm 01", "price": 3000, "image": "/static/images/cf01.jpg", "categories": ["Flag"], "subcategory": "National Flags"},
    
    # --- PASTE THE REST OF YOUR LIST HERE ---
]

# --- DATABASE MODEL ---
class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name_kh = db.Column(db.String(200), nullable=False)
    price = db.Column(db.Integer, nullable=False)
    image = db.Column(db.String(500), nullable=False)
    categories_str = db.Column(db.String(500), default="") 
    subcategory_str = db.Column(db.String(500), default="") 
    stock = db.Column(db.Integer, default=0) # Default stock 0 (User can't buy until you set it)

# --- SYNC ENGINE ---
def sync_catalog():
    print("🔄 Syncing Product Catalog...")
    for item in PRODUCT_CATALOG:
        existing = Product.query.get(item['id'])
        
        # Prepare category string
        cat_str = ", ".join(item.get('categories', []))
        sub_str = item.get('subcategory', 'General')
        
        if existing:
            # Update info but KEEP STOCK (so your admin edits aren't lost)
            existing.name_kh = item['name_kh']
            existing.price = item['price']
            existing.image = item['image']
            existing.categories_str = cat_str
            existing.subcategory_str = sub_str
        else:
            # Create new item
            new_p = Product(
                id=item['id'],
                name_kh=item['name_kh'],
                price=item['price'],
                image=item['image'],
                categories_str=cat_str,
                subcategory_str=sub_str,
                stock=0 # Start at 0 for safety
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
    # Fetch all items
    all_products = Product.query.all()
    # Send data to frontend
    products_json = [{
        "id": p.id, "name_kh": p.name_kh, "price": p.price, 
        "image": p.image, "stock": p.stock, 
        "categories": p.categories_str.split(', ')
    } for p in all_products]
    
    # Determine if Admin is viewing
    is_admin = session.get('admin', False)
    
    return render_template('custom_bracelet.html', products=products_json, is_admin=is_admin)

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

@app.route('/admin/api/sell-items', methods=['POST'])
def sell_items():
    # Only Admin can call this
    if not session.get('admin'): return jsonify({"success": False, "msg": "Unauthorized"}), 403
    
    data = request.json
    ids = data.get('ids', [])
    
    # Deduct Stock
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


