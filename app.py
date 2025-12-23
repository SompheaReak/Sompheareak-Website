import os
import requests
from flask import Flask, render_template, request, redirect, url_for, jsonify, session, abort
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.secret_key = 'somphea_reak_ultra_secret_2025'

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
    stock = db.Column(db.Integer, default=10)

# --- DATA SYNC ENGINE ---
def sync_hardcoded_data():
    if Product.query.first(): 
        return 
    
    print("🔄 Syncing data...")
    # List of charms (Cleaned Python Syntax)
    hardcoded_charms = [
        # --- Charms
        {"id": 1, "name_kh": "Silver Charm", "price": 400, "image": "/static/images/c01.jpg", "categories": ["Charm"]},
        # --- F1 LOGOS
        {"id": 1100, "name_kh": "Classic F1 Logo", "price": 3000, "image": "/static/images/charm-f1–101.jpg", "categories": ["Class F1🏎️"]},
        {"id": 1191, "name_kh": "Classic F1", "price": 3000, "image": "/static/images/charm-chain-03.jpg", "categories": ["Class F1🏎️"]},
        {"id": 1192, "name_kh": "Classic F1 - Ferri", "price": 3000, "image": "/static/images/charm-f1-301.jpg", "categories": ["Class F1🏎️"]},
        {"id": 1193, "name_kh": "Classic F1 - Porsche", "price": 3000, "image": "/static/images/charm-f1-302.jpg", "categories": ["Class F1🏎️"]},
        {"id": 1194, "name_kh": "Classic F1 - BMW", "price": 3000, "image": "/static/images/charm-f1-303.jpg", "categories": ["Class F1🏎️"]},
        {"id": 1195, "name_kh": "Classic F1 - BMW", "price": 3000, "image": "/static/images/charm-f1-304.jpg", "categories": ["Class F1🏎️"]},
        {"id": 1101, "name_kh": "Classic F1 - Mercedes", "price": 3000, "image": "/static/images/cc15.jpg", "categories": ["Class F1🏎️"]},
        {"id": 1102, "name_kh": "Classic F1 - Ferrari", "price": 3000, "image": "/static/images/cc04.jpg", "categories": ["Class F1🏎️"]},
        {"id": 1103, "name_kh": "Classic F1 - Porsche", "price": 3000, "image": "/static/images/cc12.jpg", "categories": ["Class F1🏎️"]},
        {"id": 1104, "name_kh": "Classic F1 - BMW", "price": 3000, "image": "/static/images/cc06.jpg", "categories": ["Class F1🏎️"]},
        # --- Flags
        {"id": 2001, "name_kh": "Flag Charm 01", "price": 3000, "image": "/static/images/cf01.jpg", "categories": ["Flag"], "subcategory": "Football"},
        {"id": 2002, "name_kh": "Flag Charm 02", "price": 3000, "image": "/static/images/cf02.jpg", "categories": ["Flag"], "subcategory": "Football"},
        {"id": 2003, "name_kh": "Flag Charm 03", "price": 3000, "image": "/static/images/cf03.jpg", "categories": ["Flag"], "subcategory": "Football"},
        # Add more here following the same format...
    ]

    for item in hardcoded_charms:
        # Determine Grouping
        group_name = item.get('subcategory', item['categories'][0])
        if isinstance(group_name, list): group_name = group_name[0]
            
        new_p = Product(
            id=item['id'],
            name_kh=item['name_kh'],
            price=item['price'],
            image=item['image'],
            categories_str=", ".join(item['categories']),
            subcategory_str=group_name,
            stock=10
        )
        db.session.add(new_p)
    db.session.commit()
    print("✅ Sync complete.")

# --- ROUTES ---

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
            return redirect(url_for('admin_panel'))
    return render_template('admin_login.html')

@app.route('/admin/logout')
def logout():
    session.pop('admin', None)
    return redirect(url_for('admin_login'))

# --- DB INIT ---
with app.app_context():
    db.create_all()
    sync_hardcoded_data()

if __name__ == '__main__':
    app.run(debug=True, port=5000)

