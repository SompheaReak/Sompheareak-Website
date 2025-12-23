import os
import requests
from flask import Flask, render_template, request, redirect, url_for, jsonify, session, abort
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import func

app = Flask(__name__)
app.secret_key = 'somphea_reak_shop_secret_key'

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
    categories_str = db.Column(db.String(500), default="") 
    subcategory_str = db.Column(db.String(500), default="") 
    stock = db.Column(db.Integer, default=0) # Stock management field

# --- ROUTES ---

@app.route('/custom-bracelet')
def custom_bracelet():
    # Fetch charms and pass as JSON for the builder logic
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

@app.route('/process-order', methods=['POST'])
def process_order():
    """Decreases stock for all charms used in a design"""
    data = request.json
    charm_ids = data.get('charm_ids', [])
    customer_info = data.get('customer', {})
    
    items_ordered = []
    total_price = 0

    for cid in charm_ids:
        product = Product.query.get(cid)
        if product and product.stock > 0:
            product.stock -= 1 # DECREASE STOCK
            items_ordered.append(product.name_kh)
            total_price += product.price
    
    db.session.commit()

    # Notify via Telegram
    msg = f"🛒 *New Bracelet Order*\n*Customer:* {customer_info.get('name')}\n*Phone:* {customer_info.get('phone')}\n*Items:* {', '.join(items_ordered)}\n*Total:* {total_price:,}៛"
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    requests.post(url, data={"chat_id": CHAT_ID, "text": msg, "parse_mode": "Markdown"})

    return jsonify({"success": True})

# --- ADMIN ROUTES ---

@app.route('/admin/products')
def admin_products():
    if not session.get('admin'): return redirect(url_for('admin_login'))
    
    # Group products by subcategory for easier management
    all_products = Product.query.all()
    grouped_charms = {}
    
    for p in all_products:
        sub = p.subcategory_str if p.subcategory_str else "Uncategorized"
        if sub not in grouped_charms:
            grouped_charms[sub] = []
        grouped_charms[sub].append(p)
        
    return render_template('admin_products.html', grouped_charms=grouped_charms)

@app.route('/admin/update-stock', methods=['POST'])
def update_stock():
    if not session.get('admin'): return jsonify({"success": False}), 403
    p_id = request.json.get('id')
    amount = request.json.get('amount')
    product = Product.query.get(p_id)
    if product:
        product.stock = int(amount)
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

with app.app_context():
    db.create_all()

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)

