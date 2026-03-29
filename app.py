import os
import json
import time
from datetime import datetime
from flask import Flask, render_template, request, redirect, url_for, jsonify, session, flash
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import text
import cloudinary
import cloudinary.uploader

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'somphea_reak_ultra_pro_2025')
app.config['MAX_CONTENT_LENGTH'] = 50 * 1024 * 1024 

# --- 1. CLOUDINARY CONFIG ---
cloudinary.config( 
  cloud_name = "dwwearehy", 
  api_key = os.environ.get("CLOUDINARY_API_KEY"), 
  api_secret = os.environ.get("CLOUDINARY_API_SECRET"),
  secure = True
)

# --- AUTO-COMPRESSOR ENGINE ---
# Converts everything (even HEIC) to lightweight WebP!
def optimize_and_upload(file):
    return cloudinary.uploader.upload(
        file,
        format="webp",       # <--- FIXED: Safely converts all formats to lightweight WebP
        quality="auto",      
        width=900,           
        height=900,          
        crop="limit"         
    )

# --- 2. PERMANENT DATABASE CONFIG ---
db_url = os.environ.get('DATABASE_URL', 'sqlite:///fallback.db')
if db_url.startswith("postgres://"):
    db_url = db_url.replace("postgres://", "postgresql://", 1)

app.config['SQLALCHEMY_DATABASE_URI'] = db_url
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# THE "WAKE UP" FIX FOR SLEEPING DATABASES
app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {
    "pool_pre_ping": True,  
    "pool_recycle": 300,    
    "pool_timeout": 30      
}

db = SQLAlchemy(app)
ADMIN_PASS = 'Thesong_Admin@2022?!$'

# --- ANTI-SPAM MEMORY TRACKER ---
spam_tracker = {}

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
    is_visible = db.Column(db.Boolean, default=True) 

class Category(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    store = db.Column(db.String(50), nullable=False)
    image = db.Column(db.String(500), nullable=True, default="https://via.placeholder.com/150?text=Upload")
    sort_order = db.Column(db.Integer, default=0)

class Order(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    customer_name = db.Column(db.String(100), nullable=False)
    customer_phone = db.Column(db.String(20), nullable=False)
    customer_address = db.Column(db.Text, nullable=False)
    items_json = db.Column(db.Text, nullable=False) 
    total_usd = db.Column(db.Float, nullable=False)
    status = db.Column(db.String(20), default="Pending")
    stock_deducted = db.Column(db.Boolean, default=False)
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

@app.route('/api/checkout', methods=['POST'])
def checkout():
    client_ip = request.headers.get('X-Forwarded-For', request.remote_addr)
    if client_ip and ',' in client_ip:
        client_ip = client_ip.split(',')[0].strip()
        
    current_time = time.time()
    
    if client_ip in spam_tracker:
        last_time, count = spam_tracker[client_ip]
        if current_time - last_time < 300:
            if count >= 2: 
                return jsonify({'status': 'error', 'message': 'Too many orders placed. Please try again in 5 minutes.'}), 429
            spam_tracker[client_ip] = (last_time, count + 1)
        else:
            spam_tracker[client_ip] = (current_time, 1)
    else:
        spam_tracker[client_ip] = (current_time, 1)

    data = request.json
    try:
        new_order = Order(
            customer_name=data['name'], customer_phone=data['phone'], customer_address=data['address'],
            items_json=json.dumps(data['items']), total_usd=float(data['total']), status="Pending", stock_deducted=False
        )
        db.session.add(new_order)
        db.session.commit()
        return jsonify({'status': 'success', 'order_id': new_order.id})
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 400

# --- 5. ADMIN AUTH ---
@app.route('/admin/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST' and request.form.get('password') == ADMIN_PASS:
        session['admin'] = True
        return redirect(url_for('admin_panel'))
    return render_template('admin_login.html')

@app.route('/admin/logout')
def logout():
    session.pop('admin', None)
    return redirect(url_for('login'))

@app.route('/admin/panel')
def admin_panel():
    if not session.get('admin'): return redirect(url_for('login'))
    
    unique_cats = db.session.query(Product.category, Product.store).distinct().all()
    for c_name, c_store in unique_cats:
        if c_name != "Other" and not Category.query.filter_by(name=c_name, store=c_store).first():
            db.session.add(Category(name=c_name, store=c_store, sort_order=999))
    db.session.commit()
    
    products = Product.query.order_by(Product.sort_order.asc(), Product.id.desc()).all()
    for p in products: p.parsed_variants = json.loads(p.variants) if p.variants else []
        
    categories = Category.query.order_by(Category.sort_order).all()
    orders = Order.query.order_by(Order.timestamp.desc()).all()
    for o in orders: o.parsed_items = json.loads(o.items_json)

    return render_template('admin_panel.html', products=products, categories=categories, orders=orders)

# --- 6. ADMIN ACTIONS ---
@app.route('/admin/order/status/<int:id>/<string:status>', methods=['POST'])
def update_order_status(id, status):
    if not session.get('admin'): return redirect(url_for('login'))
    order = Order.query.get(id)
    if order:
        if status == 'Completed' and not order.stock_deducted:
            try:
                items = json.loads(order.items_json)
                for item in items:
                    parts = str(item.get('cartId', '')).split('-')
                    if len(parts) == 2:
                        p_id = int(parts[0])
                        v_idx = int(parts[1])
                        qty_bought = int(item.get('qty', 1))
                        
                        product = Product.query.get(p_id)
                        if product and product.variants:
                            variants = json.loads(product.variants)
                            if 0 <= v_idx < len(variants):
                                variants[v_idx]['stock'] = max(0, variants[v_idx]['stock'] - qty_bought)
                                product.variants = json.dumps(variants)
                                product.stock = sum(v.get('stock', 0) for v in variants)
            except Exception as e:
                pass
            
            order.stock_deducted = True

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

@app.route('/admin/categories/update', methods=['POST'])
def update_categories():
    if not session.get('admin'): return redirect(url_for('login'))
    cat_ids = request.form.getlist('cat_ids[]')
    cat_names = request.form.getlist('cat_names[]')
    
    try:
        for i, cid in enumerate(cat_ids):
            cat = Category.query.get(int(cid))
            if cat:
                cat.name = cat_names[i]
                cat.sort_order = i
                file = request.files.get(f'cat_image_{cid}')
                if file and file.filename != '':
                    res = optimize_and_upload(file)
                    cat.image = res['secure_url']
        db.session.commit()
        flash('Categories updated successfully!', 'success')
    except Exception as e:
        flash(f'Upload Error: Check API Keys. Details: {str(e)}', 'error')
        
    return redirect(url_for('admin_panel'))

@app.route('/admin/category/delete/<int:id>', methods=['POST'])
def delete_category(id):
    if not session.get('admin'): return redirect(url_for('login'))
    c = Category.query.get(id)
    if c:
        products = Product.query.filter_by(category=c.name, store=c.store).all()
        for p in products: p.category = "Other"
        db.session.delete(c)
        db.session.commit()
    return redirect(url_for('admin_panel'))

@app.route('/admin/product/reorder', methods=['POST'])
def reorder_products():
    if not session.get('admin'): return jsonify({'status': 'unauthorized'}), 401
    data = request.json
    for i, pid in enumerate(data.get('ids', [])):
        p = Product.query.get(int(pid))
        if p: p.sort_order = i
    db.session.commit()
    return jsonify({'status': 'success'})

@app.route('/admin/product/toggle/<int:id>', methods=['POST'])
def toggle_product(id):
    if not session.get('admin'): return redirect(url_for('login'))
    p = Product.query.get(id)
    if p:
        p.is_visible = not p.is_visible
        db.session.commit()
        flash(f'Product visibility updated.', 'success')
    return redirect(url_for('admin_panel'))

@app.route('/admin/product/update/<int:id>', methods=['POST'])
def update_product(id):
    if not session.get('admin'): return redirect(url_for('login'))
    p = Product.query.get_or_404(id)
    
    p.title = request.form.get('title')
    p.category = request.form.get('category')
    p.store = request.form.get('store')
    
    v_ids = request.form.getlist('v_ids[]')
    v_images = request.form.getlist('v_images[]')
    v_names = request.form.getlist('v_names[]')
    v_prices = request.form.getlist('v_prices[]')
    v_stocks = request.form.getlist('v_stocks[]')
    
    updated_variants = []
    total_stock = 0
    
    for i in range(len(v_ids)):
        stock = int(v_stocks[i])
        updated_variants.append({
            "id": int(v_ids[i]), "image": v_images[i], "name": v_names[i],
            "price": float(v_prices[i]), "stock": stock
        })
        total_stock += stock

    new_files = request.files.getlist('new_images')
    try:
        if new_files and new_files[0].filename != '':
            last_id = max([v['id'] for v in updated_variants]) if updated_variants else 0
            for f in new_files:
                if f and f.filename != '':
                    res = optimize_and_upload(f)
                    last_id += 1
                    updated_variants.append({"id": last_id, "name": f"New Style {last_id}", "price": updated_variants[0]['price'] if updated_variants else 0, "stock": 1, "image": res['secure_url']})
                    total_stock += 1
                    
        p.variants = json.dumps(updated_variants)
        p.stock = total_stock
        if updated_variants:
            p.image = updated_variants[0]['image']
            p.price = updated_variants[0]['price']
        
        db.session.commit()
        flash('Product updated successfully!', 'success')
    except Exception as e:
        flash(f'Cloud Error: Cannot upload new styles. ({str(e)})', 'error')
        
    return redirect(url_for('admin_panel'))

@app.route('/admin/product/add', methods=['POST'])
def add_product():
    if not session.get('admin'): return redirect(url_for('login'))
    title = request.form.get('title')
    category = request.form.get('category')
    store = request.form.get('store')
    
    v_names = request.form.getlist('variant_names[]')
    v_prices = request.form.getlist('variant_prices[]')
    v_stocks = request.form.getlist('variant_stocks[]')
    files = request.files.getlist('images')
    
    uploaded_urls = []
    try:
        for f in files:
            if f and f.filename != '':
                res = optimize_and_upload(f)
                uploaded_urls.append(res['secure_url'])
                
        if uploaded_urls:
            vars_json = []
            total_stock = 0
            for i, url in enumerate(uploaded_urls):
                price = float(v_prices[i]) if i < len(v_prices) else 0
                stock = int(v_stocks[i]) if i < len(v_stocks) else 0
                vars_json.append({"id": i, "name": v_names[i] if i < len(v_names) else f"Style {i+1}", "price": price, "stock": stock, "image": url})
                total_stock += stock
            
            new_p = Product(title=title, price=vars_json[0]['price'], stock=total_stock, image=uploaded_urls[0], category=category, store=store, variants=json.dumps(vars_json), sort_order=-1, is_visible=True)
            db.session.add(new_p)
            db.session.commit()
            flash('Product published successfully!', 'success')
        else:
            flash('Warning: No valid images found to upload.', 'error')
            
    except Exception as e:
        flash(f'Upload Failed! Please check your Cloudinary API keys. Details: {str(e)}', 'error')

    return redirect(url_for('admin_panel'))

@app.route('/admin/product/delete/<int:id>', methods=['POST'])
def delete_product(id):
    if not session.get('admin'): return redirect(url_for('login'))
    p = Product.query.get(id)
    if p:
        db.session.delete(p)
        db.session.commit()
        flash('Product deleted successfully.', 'success')
    return redirect(url_for('admin_panel'))

@app.route('/api/products/<store_name>')
def get_api(store_name):
    try:
        products = Product.query.filter_by(store=store_name, is_visible=True).order_by(Product.sort_order.asc(), Product.id.desc()).all()
        categories = Category.query.filter_by(store=store_name).order_by(Category.sort_order.asc()).all()
        return jsonify({
            "products": [{"id": p.id, "title": p.title, "price": p.price, "stock": p.stock, "category": p.category, "thumbnail": p.image, "variants": json.loads(p.variants)} for p in products],
            "categories": [{"name": c.name, "image": c.image} for c in categories]
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.errorhandler(413)
def request_entity_too_large(error):
    flash('File too large! Please upload fewer images or compress them (Max 50MB combined).', 'error')
    return redirect(url_for('admin_panel'))

with app.app_context():
    db.create_all()
    try:
        db.session.execute(text("ALTER TABLE product ADD COLUMN sort_order INTEGER DEFAULT 0"))
        db.session.commit()
    except:
        db.session.rollback()
        
    try:
        db.session.execute(text('ALTER TABLE "order" ADD COLUMN stock_deducted BOOLEAN DEFAULT FALSE'))
        db.session.commit()
    except:
        db.session.rollback()
        
    try:
        db.session.execute(text('ALTER TABLE product ADD COLUMN is_visible BOOLEAN DEFAULT TRUE'))
        db.session.commit()
    except:
        db.session.rollback()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))


