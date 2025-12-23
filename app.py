import os
import requests
from flask import Flask, render_template, request, redirect, url_for, jsonify, session, abort
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.secret_key = 'somphea_reak_shop_secret_key'

# --- DATABASE SETUP ---
basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'shop.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# --- ADMIN CREDENTIALS ---
ADMIN_USERNAME = 'AdminSompheaReakVitou'
ADMIN_PASSWORD = 'Thesong_Admin@2022?!$'

# --- PRODUCT MODEL ---
class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name_kh = db.Column(db.String(200), nullable=False)
    price = db.Column(db.Integer, nullable=False)
    image = db.Column(db.String(500), nullable=False)
    categories_str = db.Column(db.String(500), default="") 
    subcategory_str = db.Column(db.String(500), default="") 
    stock = db.Column(db.Integer, default=10) # Manage this from Admin

# --- DATA IMPORTER (Run this once to move your JS list to DB) ---
def seed_database():
    if Product.query.first(): return 
    
    # PASTE YOUR FULL LIST HERE
    catalog = [
        {"id": 1101, "name_kh": "Letter Charm A", "price": 1200, "image": "/static/images/a.jpg", "categories": ["Letter", "Italy Bracelet"], "subcategory": "SILVER/GOLD LETTERS"},
        {"id": 1102, "name_kh": "Letter Charm B", "price": 1200, "image": "/static/images/b.jpg", "categories": ["Letter", "Italy Bracelet"], "subcategory": "SILVER/GOLD LETTERS"},
        # ... Paste the rest of your 200+ items here ...
    ]

    for item in catalog:
        # We ensure "Italy Bracelet" is in the category string for the studio filter
        cats = ", ".join(item['categories'])
        sub = item.get('subcategory', 'General')
        
        new_p = Product(
            id=item['id'], name_kh=item['name_kh'], price=item['price'],
            image=item['image'], categories_str=cats,
            subcategory_str=sub, stock=10
        )
        db.session.add(new_p)
    db.session.commit()
    print("✅ Database successfully populated from your list!")

# --- STUDIO ROUTES ---

@app.route('/custom-bracelet')
def custom_bracelet():
    # Fetch charms and pass them as JSON to the JS engine
    charms_db = Product.query.filter(Product.categories_str.contains('Italy Bracelet')).all()
    charms_list = []
    for c in charms_db:
        charms_list.append({
            "id": c.id, "name_kh": c.name_kh, "price": c.price,
            "image": c.image, "stock": c.stock,
            "categories": [cat.strip() for cat in c.categories_str.split(',')]
        })
    return render_template('custom_bracelet.html', charms_json=charms_list)

@app.route('/api/deduct-stock', methods=['POST'])
def deduct_stock():
    """Reduces stock by 1 for each item in the design"""
    data = request.json
    ids = data.get('ids', [])
    for pid in ids:
        p = Product.query.get(pid)
        if p and p.stock > 0:
            p.stock -= 1
    db.session.commit()
    return jsonify({"success": True})

# --- ADMIN ROUTES ---

@app.route('/admin/products')
def admin_products():
    if not session.get('admin'): return redirect(url_for('admin_login'))
    
    # Group items by their subcategory (Letter, Flag, Gem, etc)
    all_p = Product.query.all()
    grouped = {}
    for p in all_p:
        sub = p.subcategory_str if p.subcategory_str else "General"
        if sub not in grouped: grouped[sub] = []
        grouped[sub].append(p)
        
    return render_template('admin_products.html', grouped=grouped)

@app.route('/admin/update-stock', methods=['POST'])
def update_stock():
    if not session.get('admin'): return jsonify({"success": False}), 403
    data = request.json
    p = Product.query.get(data.get('id'))
    if p:
        p.stock = int(data.get('amount'))
        db.session.commit()
        return jsonify({"success": True})
    return jsonify({"success": False})

@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        if request.form['username'] == ADMIN_USERNAME and request.form['password'] == ADMIN_PASSWORD:
            session['admin'] = True
            return redirect(url_for('admin_products'))
    return render_template('admin_login.html')

with app.app_context():
    db.create_all()
    seed_database()

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)

