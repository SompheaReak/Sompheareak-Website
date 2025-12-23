import os
import requests
from flask import Flask, render_template, request, redirect, url_for, jsonify, session, abort
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.secret_key = 'somphea_reak_shop_ultra_secure_key'

# --- DATABASE SETUP ---
basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'shop.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# --- CONFIGURATION ---
ADMIN_USERNAME = 'AdminSompheaReakVitou'
ADMIN_PASSWORD = 'Thesong_Admin@2022?!$'
BOT_TOKEN = "7528700801:AAGTvXjk5qPBnq_qx69ZOW4RMLuGy40w5k8"
CHAT_ID = "-1002654437316"

class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name_kh = db.Column(db.String(200), nullable=False)
    price = db.Column(db.Integer, nullable=False)
    image = db.Column(db.String(500), nullable=False)
    categories_str = db.Column(db.String(500), default="") # e.g. "Italy Bracelet, Hot Sale"
    subcategory_str = db.Column(db.String(500), default="") # e.g. "Flag"
    stock = db.Column(db.Integer, default=0)

# --- STUDIO ROUTES ---

@app.route('/custom-bracelet')
def custom_bracelet():
    # Pass items with their real-time stock to the builder
    charms_db = Product.query.filter(Product.categories_str.contains('Italy Bracelet')).all()
    charms_list = []
    for c in charms_db:
        charms_list.append({
            "id": c.id,
            "name_kh": c.name_kh,
            "price": c.price,
            "image": c.image,
            "categories": [cat.strip() for cat in c.categories_str.split(',')],
            "stock": c.stock
        })
    return render_template('custom_bracelet.html', charms_json=charms_list)

@app.route('/api/deduct-stock', methods=['POST'])
def deduct_stock():
    """Decreases stock when an order is finalized"""
    data = request.json
    item_ids = data.get('ids', [])
    for pid in item_ids:
        p = Product.query.get(pid)
        if p and p.stock > 0:
            p.stock -= 1
    db.session.commit()
    return jsonify({"success": True})

# --- ADMIN ROUTES ---

@app.route('/admin/products')
def admin_products():
    if not session.get('admin'): return redirect(url_for('admin_login'))
    
    # Group products by subcategory for the stock panel
    all_products = Product.query.all()
    grouped = {}
    for p in all_products:
        cat = p.subcategory_str if p.subcategory_str else "General"
        if cat not in grouped: grouped[cat] = []
        grouped[cat].append(p)
        
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

@app.route('/admin/add-product', methods=['GET', 'POST'])
def add_product():
    if not session.get('admin'): return redirect(url_for('admin_login'))
    if request.method == 'POST':
        new_p = Product(
            name_kh=request.form['name_kh'],
            price=int(request.form['price']),
            image=request.form['image'],
            categories_str=request.form.get('category', ''),
            subcategory_str=request.form.get('subcategory', ''),
            stock=int(request.form.get('stock', 0))
        )
        db.session.add(new_p)
        db.session.commit()
        return redirect(url_for('admin_products'))
    return render_template('add_product.html')

@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        if request.form['username'] == ADMIN_USERNAME and request.form['password'] == ADMIN_PASSWORD:
            session['admin'] = True
            return redirect(url_for('admin_products'))
    return render_template('admin_login.html')

with app.app_context():
    db.create_all()

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)

