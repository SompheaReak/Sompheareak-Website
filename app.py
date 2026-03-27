import os
import json
from datetime import datetime
from flask import Flask, render_template, request, redirect, url_for, jsonify, session, flash
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import text
import cloudinary
import cloudinary.uploader

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'somphea_reak_order_system_2025')

# --- 1. CLOUDINARY CONFIG ---
cloudinary.config( 
  cloud_name = "dwwearehy", 
  api_key = os.environ.get("CLOUDINARY_API_KEY"), 
  api_secret = os.environ.get("CLOUDINARY_API_SECRET"),
  secure = True
)

# --- 2. DATABASE CONFIG ---
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'sqlite:///fallback.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
ADMIN_PASS = 'Thesong_Admin@2022?!$'

# --- 3. MODELS ---
class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    price = db.Column(db.Float, nullable=False)
    stock = db.Column(db.Integer, default=0) 
    image = db.Column(db.String(500), nullable=False) 
    category = db.Column(db.String(100), nullable=False)
    store = db.Column(db.String(50), nullable=False) 
    variants = db.Column(db.Text, nullable=True)
    sort_order = db.Column(db.Integer, default=0)

class Category(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    store = db.Column(db.String(50), nullable=False)
    image = db.Column(db.String(500), nullable=True, default="https://via.placeholder.com/150?text=Upload")
    sort_order = db.Column(db.Integer, default=0)

# NEW: ORDER MODEL
class Order(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    customer_name = db.Column(db.String(100), nullable=False)
    customer_phone = db.Column(db.String(20), nullable=False)
    customer_address = db.Column(db.Text, nullable=False)
    items_json = db.Column(db.Text, nullable=False) # Stores the whole cart
    total_usd = db.Column(db.Float, nullable=False)
    status = db.Column(db.String(20), default="Pending") # Pending, Completed, Cancelled
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

# --- 4. PUBLIC ROUTES ---
@app.route('/')
def index(): return render_template('index.html')

@app.route('/toy-universe')
def toy_universe(): return render_template('toy.html')

@app.route('/bracelet')
def shop(): return render_template('bracelet.html')

@app.route('/custom-bracelet')
def custom_bracelet(): return render_template('custom_bracelet.html')

# --- 5. CHECKOUT API (Receive from Website) ---
@app.route('/api/checkout', methods=['POST'])
def checkout():
    data = request.json
    try:
        new_order = Order(
            customer_name=data['name'],
            customer_phone=data['phone'],
            customer_address=data['address'],
            items_json=json.dumps(data['items']),
            total_usd=float(data['total']),
            status="Pending"
        )
        db.session.add(new_order)
        db.session.commit()
        return jsonify({'status': 'success', 'order_id': new_order.id})
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 400

# --- 6. ADMIN DASHBOARD ---
@app.route('/admin/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST' and request.form.get('password') == ADMIN_PASS:
        session['admin'] = True
        return redirect(url_for('admin_panel'))
    return render_template('admin_login.html')

@app.route('/admin/panel')
def admin_panel():
    if not session.get('admin'): return redirect(url_for('login'))
    
    products = Product.query.order_by(Product.sort_order.asc(), Product.id.desc()).all()
    for p in products: p.parsed_variants = json.loads(p.variants) if p.variants else []
        
    categories = Category.query.order_by(Category.sort_order).all()
    orders = Order.query.order_by(Order.timestamp.desc()).all()
    for o in orders: o.parsed_items = json.loads(o.items_json)

    return render_template('admin_panel.html', products=products, categories=categories, orders=orders)

@app.route('/admin/order/status/<int:id>/<string:status>', methods=['POST'])
def update_order_status(id, status):
    if not session.get('admin'): return redirect(url_for('login'))
    order = Order.query.get(id)
    if order:
        order.status = status
        db.session.commit()
    return redirect(url_for('admin_panel'))

@app.route('/admin/order/delete/<int:id>', methods=['POST'])
def delete_order(id):
    if not session.get('admin'): return redirect(url_for('login'))
    order = Order.query.get(id)
    if order:
        db.session.delete(order)
        db.session.commit()
    return redirect(url_for('admin_panel'))

# --- 7. OTHER ADMIN ACTIONS (ADD/DELETE/REORDER) ---
# [Keep existing routes for categories and product updates as previously defined...]

@app.route('/admin/categories/update', methods=['POST'])
def update_categories():
    if not session.get('admin'): return redirect(url_for('login'))
    cat_ids = request.form.getlist('cat_ids[]')
    cat_names = request.form.getlist('cat_names[]')
    for i, cid in enumerate(cat_ids):
        cat = Category.query.get(int(cid))
        if cat:
            cat.name = cat_names[i]
            cat.sort_order = i
            file = request.files.get(f'cat_image_{cid}')
            if file and file.filename != '':
                res = cloudinary.uploader.upload(file)
                cat.image = res['secure_url']
    db.session.commit()
    return redirect(url_for('admin_panel'))

@app.route('/admin/product/update/<int:id>', methods=['POST'])
def update_product(id):
    if not session.get('admin'): return redirect(url_for('login'))
    p = Product.query.get_or_404(id)
    p.title = request.form.get('title'); p.category = request.form.get('category'); p.store = request.form.get('store')
    v_ids = request.form.getlist('v_ids[]'); v_images = request.form.getlist('v_images[]'); v_names = request.form.getlist('v_names[]'); v_prices = request.form.getlist('v_prices[]'); v_stocks = request.form.getlist('v_stocks[]')
    updated_variants = []; total_stock = 0
    for i in range(len(v_ids)):
        stock = int(v_stocks[i])
        updated_variants.append({"id": int(v_ids[i]), "image": v_images[i], "name": v_names[i], "price": float(v_prices[i]), "stock": stock})
        total_stock += stock
    new_files = request.files.getlist('new_images')
    if new_files and new_files[0].filename != '':
        last_id = max([v['id'] for v in updated_variants]) if updated_variants else 0
        for f in new_files:
            if f and f.filename != '':
                res = cloudinary.uploader.upload(f); last_id += 1
                updated_variants.append({"id": last_id, "name": f"New Style {last_id}", "price": updated_variants[0]['price'] if updated_variants else 0, "stock": 1, "image": res['secure_url']})
                total_stock += 1
    p.variants = json.dumps(updated_variants); p.stock = total_stock
    if updated_variants: p.image = updated_variants[0]['image']; p.price = updated_variants[0]['price']
    db.session.commit()
    return redirect(url_for('admin_panel'))

@app.route('/admin/product/add', methods=['POST'])
def add_product():
    if not session.get('admin'): return redirect(url_for('login'))
    title = request.form.get('title'); category = request.form.get('category'); store = request.form.get('store')
    v_names = request.form.getlist('variant_names[]'); v_prices = request.form.getlist('variant_prices[]'); v_stocks = request.form.getlist('variant_stocks[]'); files = request.files.getlist('images')
    uploaded_urls = []
    for f in files:
        if f and f.filename != '':
            res = cloudinary.uploader.upload(f); uploaded_urls.append(res['secure_url'])
    if uploaded_urls:
        vars_json = []; total_stock = 0
        for i, url in enumerate(uploaded_urls):
            price = float(v_prices[i]) if i < len(v_prices) else 0; stock = int(v_stocks[i]) if i < len(v_stocks) else 0
            vars_json.append({"id": i, "name": v_names[i] if i < len(v_names) else f"Style {i+1}", "price": price, "stock": stock, "image": url})
            total_stock += stock
        new_p = Product(title=title, price=vars_json[0]['price'], stock=total_stock, image=uploaded_urls[0], category=category, store=store, variants=json.dumps(vars_json), sort_order=-1)
        db.session.add(new_p); db.session.commit()
    return redirect(url_for('admin_panel'))

@app.route('/admin/product/delete/<int:id>', methods=['POST'])
def delete_product(id):
    if not session.get('admin'): return redirect(url_for('login'))
    p = Product.query.get(id); db.session.delete(p); db.session.commit()
    return redirect(url_for('admin_panel'))

@app.route('/api/products/<store_name>')
def get_api(store_name):
    products = Product.query.filter_by(store=store_name).order_by(Product.sort_order.asc(), Product.id.desc()).all()
    categories = Category.query.filter_by(store=store_name).order_by(Category.sort_order.asc()).all()
    return jsonify({
        "products": [{"id": p.id, "title": p.title, "price": p.price, "stock": p.stock, "category": p.category, "thumbnail": p.image, "variants": json.loads(p.variants)} for p in products],
        "categories": [{"name": c.name, "image": c.image} for c in categories]
    })

with app.app_context():
    db.create_all()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))

