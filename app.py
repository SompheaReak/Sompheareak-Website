
import os
import json
import time
import random
import string
import uuid
from datetime import datetime, timedelta
from functools import wraps
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

def optimize_and_upload(file):
    return cloudinary.uploader.upload(
        file,
        format="webp",
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

app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {
    "pool_pre_ping": True,  
    "pool_recycle": 300,    
    "pool_timeout": 30      
}

db = SQLAlchemy(app)

# --- SECURITY CONFIG ---
ADMIN_USERNAME = 'admin'
ADMIN_PASS = 'Thesong_Admin@2022?!$'

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get('admin'):
            flash('Please log in to access the admin panel.', 'error')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

spam_tracker = {}

# --- 3. STORE MODELS ---
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

# --- 4. SPINNER GAME MODELS ---
class PlayerSession(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    player_id = db.Column(db.String(8), unique=True, nullable=False) 
    balance = db.Column(db.Integer, default=0)

class RedeemCode(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(8), unique=True, nullable=False)
    value = db.Column(db.Integer, nullable=False)  
    status = db.Column(db.String(20), default="Active") 
    redeemed_by = db.Column(db.String(8), nullable=True) 
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

class MinifigurePool(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    image = db.Column(db.String(500), nullable=False)
    rarity = db.Column(db.String(50), nullable=False)
    stock = db.Column(db.Integer, default=0)
    sort_order = db.Column(db.Integer, default=0)
    
    # --- NEW COLUMNS FOR SYNCING ---
    linked_product_id = db.Column(db.Integer, nullable=True)
    linked_variant_index = db.Column(db.Integer, nullable=True)

    @property
    def is_catalog_linked(self):
        return self.linked_product_id is not None

class DrawHistory(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    player_id = db.Column(db.String(8), nullable=False)
    item_name = db.Column(db.String(200), nullable=False)
    rarity = db.Column(db.String(50), nullable=False)
    stock_remaining = db.Column(db.Integer, nullable=False)
    timestamp_utc = db.Column(db.DateTime, default=datetime.utcnow)

    # Cambodia Time (UTC+7)
    @property
    def cambodia_time(self):
        kh_time = self.timestamp_utc + timedelta(hours=7)
        return kh_time.strftime('%d-%b-%Y %I:%M %p')


# --- SYNC HELPER FUNCTIONS ---
def _sync_product_to_pool(product_id, variant_index, new_stock):
    """Updates the Spin Pool when the Store Stock changes"""
    linked_prize = MinifigurePool.query.filter_by(linked_product_id=product_id, linked_variant_index=variant_index).first()
    if linked_prize:
        linked_prize.stock = new_stock

def _sync_pool_to_product(pool_item):
    """Updates the Store Stock when the Spin Pool Stock changes (wins or admin edits)"""
    if pool_item.linked_product_id is not None:
        product = Product.query.get(pool_item.linked_product_id)
        if product:
            if pool_item.linked_variant_index != -1 and product.variants:
                try:
                    variants = json.loads(product.variants)
                    if 0 <= pool_item.linked_variant_index < len(variants):
                        variants[pool_item.linked_variant_index]['stock'] = pool_item.stock
                        product.variants = json.dumps(variants)
                        product.stock = sum(int(v.get('stock', 0)) for v in variants)
                except Exception:
                    pass
            else:
                product.stock = pool_item.stock


# --- 5. PUBLIC & STORE ROUTES ---
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

# --- 6. UNIFIED ADMIN ROUTES ---
@app.route('/admin/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        if username == ADMIN_USERNAME and password == ADMIN_PASS:
            session['admin'] = True
            flash('Login Successful!', 'success')
            return redirect(url_for('admin_panel'))
        else:
            flash('Invalid Username or Password', 'error')
    return render_template('admin_login.html')

@app.route('/admin/logout')
def logout():
    session.pop('admin', None)
    flash('You have been logged out.', 'success')
    return redirect(url_for('login'))

@app.route('/admin/panel')
@login_required
def admin_panel():
    # Store Data
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

    # Spinner Game Data (Added sorting functionality)
    codes = RedeemCode.query.order_by(RedeemCode.timestamp.desc()).all()
    pool = MinifigurePool.query.order_by(MinifigurePool.sort_order.asc(), MinifigurePool.id.desc()).all()
    history = DrawHistory.query.order_by(DrawHistory.timestamp_utc.desc()).limit(100).all()

    return render_template('admin_panel.html', products=products, categories=categories, orders=orders, codes=codes, pool=pool, history=history)

# Quick API to edit stock instantly from the Modal
@app.route('/admin/product/quick_stock', methods=['POST'])
@login_required
def quick_update_stock():
    data = request.json
    p_id = data.get('product_id')
    v_idx = data.get('variant_index') 
    new_stock = int(data.get('stock', 0))

    product = Product.query.get(p_id)
    if not product:
        return jsonify({'success': False, 'message': 'Product not found'})

    if v_idx != -1 and product.variants:
        variants = json.loads(product.variants)
        if 0 <= v_idx < len(variants):
            variants[v_idx]['stock'] = new_stock
            product.variants = json.dumps(variants)
            product.stock = sum(int(v.get('stock', 0)) for v in variants)
    else:
        product.stock = new_stock

    # --- SYNC ---
    _sync_product_to_pool(p_id, v_idx, new_stock)
    
    db.session.commit()
    return jsonify({'success': True, 'new_stock': new_stock, 'total_stock': product.stock})


@app.route('/admin/order/status/<int:id>/<string:status>', methods=['POST'])
@login_required
def update_order_status(id, status):
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
                        if product:
                            # Handle Variant Stock Deduction
                            if product.variants and v_idx != -1:
                                variants = json.loads(product.variants)
                                if 0 <= v_idx < len(variants):
                                    variants[v_idx]['stock'] = max(0, variants[v_idx]['stock'] - qty_bought)
                                    product.variants = json.dumps(variants)
                                    product.stock = sum(v.get('stock', 0) for v in variants)
                                    # SYNC
                                    _sync_product_to_pool(p_id, v_idx, variants[v_idx]['stock'])
                            # Handle Normal Single Product Stock Deduction
                            else:
                                product.stock = max(0, product.stock - qty_bought)
                                # SYNC
                                _sync_product_to_pool(p_id, -1, product.stock)
            except Exception as e:
                pass
            
            order.stock_deducted = True

        order.status = status
        db.session.commit()
        flash(f'Order {id} marked as {status}.', 'success')
    return redirect(url_for('admin_panel'))

@app.route('/admin/order/delete/<int:id>', methods=['POST'])
@login_required
def delete_order(id):
    order = Order.query.get(id)
    if order:
        db.session.delete(order)
        db.session.commit()
        flash('Order deleted.', 'success')
    return redirect(url_for('admin_panel'))

@app.route('/admin/categories/update', methods=['POST'])
@login_required
def update_categories():
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
@login_required
def delete_category(id):
    c = Category.query.get(id)
    if c:
        products = Product.query.filter_by(category=c.name, store=c.store).all()
        for p in products: p.category = "Other"
        db.session.delete(c)
        db.session.commit()
        flash('Category deleted.', 'success')
    return redirect(url_for('admin_panel'))

@app.route('/admin/product/reorder', methods=['POST'])
@login_required
def reorder_products():
    data = request.json
    for i, pid in enumerate(data.get('ids', [])):
        p = Product.query.get(int(pid))
        if p: p.sort_order = i
    db.session.commit()
    return jsonify({'status': 'success'})

@app.route('/admin/product/toggle/<int:id>', methods=['POST'])
@login_required
def toggle_product(id):
    p = Product.query.get(id)
    if p:
        p.is_visible = not p.is_visible
        db.session.commit()
        flash(f'Product visibility updated.', 'success')
    return redirect(url_for('admin_panel'))

@app.route('/admin/product/delete/<int:id>', methods=['POST'])
@login_required
def delete_product(id):
    p = Product.query.get(id)
    if p:
        db.session.delete(p)
        db.session.commit()
        flash('Product successfully deleted.', 'success')
    return redirect(url_for('admin_panel'))

@app.route('/admin/product/update/<int:id>', methods=['POST'])
@login_required
def update_product(id):
    p = Product.query.get_or_404(id)
    p.title = request.form.get('title')
    p.category = request.form.get('category')
    p.store = request.form.get('store')
    
    v_ids = request.form.getlist('v_ids[]')
    v_images = request.form.getlist('v_images[]')
    v_names = request.form.getlist('v_names[]')
    v_prices = request.form.getlist('v_prices[]')
    v_stocks = request.form.getlist('v_stocks[]')
    v_cats = request.form.getlist('v_categories[]')
    
    updated_variants = []
    total_stock = 0
    
    for i in range(len(v_ids)):
        stock = int(v_stocks[i])
        updated_variants.append({
            "id": int(v_ids[i]), 
            "image": v_images[i], 
            "name": v_names[i],
            "price": float(v_prices[i]), 
            "stock": stock,
            "category": v_cats[i] if i < len(v_cats) else p.category
        })
        total_stock += stock
        # SYNC
        _sync_product_to_pool(p.id, int(v_ids[i]), stock)

    new_files = request.files.getlist('new_images')
    try:
        if new_files and new_files[0].filename != '':
            last_id = max([v['id'] for v in updated_variants]) if updated_variants else 0
            for f in new_files:
                if f and f.filename != '':
                    res = optimize_and_upload(f)
                    last_id += 1
                    updated_variants.append({
                        "id": last_id, "name": f"New Style {last_id}", 
                        "price": updated_variants[0]['price'] if updated_variants else 0, 
                        "stock": 1, "image": res['secure_url'], "category": p.category 
                    })
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
@login_required
def add_product():
    title = request.form.get('title')
    category = request.form.get('category')
    store = request.form.get('store')
    
    v_names = request.form.getlist('variant_names[]')
    v_prices = request.form.getlist('variant_prices[]')
    v_stocks = request.form.getlist('variant_stocks[]')
    v_categories = request.form.getlist('variant_categories[]')
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
                cat_str = v_categories[i] if i < len(v_categories) else category
                
                vars_json.append({
                    "id": i, "name": v_names[i] if i < len(v_names) else f"Style {i+1}", 
                    "price": price, "stock": stock, "image": url, "category": cat_str 
                })
                total_stock += stock
            
            new_p = Product(title=title, price=vars_json[0]['price'], stock=total_stock, image=uploaded_urls[0], category=category, store=store, variants=json.dumps(vars_json), sort_order=-1, is_visible=True)
            db.session.add(new_p)
            db.session.commit()
            flash('Product published successfully!', 'success')
        else:
            flash('Warning: No valid images found to upload.', 'error')
            
    except Exception as e:
        flash(f'Upload Failed! Details: {str(e)}', 'error')

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


# --- 7. SPINNER GAME FRONTEND & API LOGIC ---

@app.route('/mystery-box')
@app.route('/lucky-draw')
@app.route('/spin')
def mystery_box(): 
    return render_template('lucky_draw.html')

def get_player():
    if 'player_id' not in session:
        # Generate an 8-digit random ID
        new_id = str(random.randint(10000000, 99999999))
        session['player_id'] = new_id
        new_player = PlayerSession(player_id=new_id, balance=0)
        db.session.add(new_player)
        db.session.commit()
    
    player = PlayerSession.query.filter_by(player_id=session['player_id']).first()
    if not player:
        player = PlayerSession(player_id=session['player_id'], balance=0)
        db.session.add(player)
        db.session.commit()
    return player

@app.route('/api/spin/balance', methods=['GET'])
def get_balance():
    player = get_player()
    return jsonify({"balance": player.balance, "player_id": player.player_id})

@app.route('/api/spin/redeem', methods=['POST'])
def redeem_riel_code():
    player = get_player()
    code_input = request.json.get('code', '').strip().upper()
    code_entry = RedeemCode.query.filter_by(code=code_input).first()
    
    if not code_entry: return jsonify({"error": "Invalid Code"}), 400
    if code_entry.status == "Redeemed": return jsonify({"error": "Code already used"}), 400
        
    code_entry.status = "Redeemed"
    code_entry.redeemed_by = player.player_id
    player.balance += code_entry.value
    db.session.commit()
    return jsonify({"success": True, "new_balance": player.balance, "value": code_entry.value})

@app.route('/api/spin/play', methods=['POST'])
def execute_spin():
    player = get_player()
    count = int(request.json.get('count', 1)) 
    cost = 1000 if count == 1 else 5000
    
    if player.balance < cost:
        return jsonify({"error": "Insufficient Riel. Please redeem a code."}), 400

    available_items = MinifigurePool.query.filter(MinifigurePool.stock > 0).all()
    if not available_items or sum([item.stock for item in available_items]) < count:
        return jsonify({"error": "Not enough stock in the prize pool!"}), 400

    # Build Weighted Pool for Draw
    pool = []
    for item in available_items:
        if item.rarity == 'Legendary': weight = 2
        elif item.rarity == 'Epic': weight = 10
        elif item.rarity == 'Rare': weight = 30
        else: weight = 58 
        pool.extend([item] * weight)

    if not pool:
        return jsonify({"error": "Error building prize pool"}), 400

    prizes = []
    for _ in range(count):
        winner = random.choice(pool)
        winner.stock -= 1 # DEDUCT STOCK PERMANENTLY
        
        # --- SYNC: Deduct from linked store product ---
        _sync_pool_to_product(winner)
        
        # Log to Admin Panel with Cambodia Time tracking
        history = DrawHistory(
            player_id=player.player_id, 
            item_name=winner.name, 
            rarity=winner.rarity, 
            stock_remaining=winner.stock
        )
        db.session.add(history)
        
        prizes.append({
            "id": winner.id, "name": winner.name, 
            "image": winner.image, "rarity": winner.rarity
        })
        # Remove out of stock items for the next iteration if doing 5x spin
        pool = [i for i in pool if i.stock > 0]
        if not pool and _ < count - 1:
            break

    player.balance -= cost # DEDUCT RIEL
    db.session.commit()
    return jsonify({"success": True, "new_balance": player.balance, "prizes": prizes})

@app.route('/api/spin/pool', methods=['GET'])
def get_live_pool():
    items = MinifigurePool.query.all()
    data = [{"id": i.id, "name": i.name, "image": i.image, "rarity": i.rarity, "stock": i.stock} for i in items]
    return jsonify({"pool": data})


# --- 8. SPINNER ADMIN ROUTES ---
@app.route('/admin/spin/generate_codes', methods=['POST'])
@login_required
def generate_codes():
    quantity = int(request.form.get('quantity', 5))
    value = int(request.form.get('value', 1000))
    characters = string.ascii_uppercase + string.digits
    for _ in range(quantity):
        code_str = ''.join(random.choice(characters) for i in range(8))
        db.session.add(RedeemCode(code=code_str, value=value))
    db.session.commit()
    flash(f'Generated {quantity} codes!', 'success')
    return redirect(url_for('admin_panel'))

@app.route('/admin/spin/add_pool_catalog', methods=['POST'])
@login_required
def add_pool_catalog():
    selected_items = request.form.getlist('catalog_items[]')
    rarity = request.form.get('rarity', 'Common')
    
    added_count = 0
    for item_data in selected_items:
        parts = item_data.split('|')
        if len(parts) == 2:
            p_id = int(parts[0])
            v_idx = int(parts[1])
            
            product = Product.query.get(p_id)
            if product:
                image = product.image
                name = product.title
                stock = product.stock
                
                # Fetch specific variant info if it's a multi-variant product
                if v_idx != -1 and product.variants:
                    variants = json.loads(product.variants)
                    if 0 <= v_idx < len(variants):
                        image = variants[v_idx].get('image', image)
                        name = f"{variants[v_idx].get('name', 'Variant')} {product.title}"
                        stock = variants[v_idx].get('stock', 0)
                
                # Check if it's already linked to prevent duplicates
                existing = MinifigurePool.query.filter_by(linked_product_id=p_id, linked_variant_index=v_idx).first()
                if existing:
                    existing.stock = stock
                    existing.image = image
                    existing.name = name
                    added_count += 1
                else:
                    new_item = MinifigurePool(name=name, rarity=rarity, stock=stock, image=image, linked_product_id=p_id, linked_variant_index=v_idx)
                    db.session.add(new_item)
                    added_count += 1
                
    if added_count > 0:
        db.session.commit()
        flash(f'Successfully linked {added_count} catalog items to the Prize Pool!', 'success')
    else:
        flash('No valid items selected to link.', 'error')
        
    return redirect(url_for('admin_panel'))

@app.route('/admin/spin/add_pool', methods=['POST'])
@login_required
def add_spin_pool():
    name_input = request.form.get('name', '').strip()
    rarity = request.form.get('rarity')
    stock = int(request.form.get('stock', 1)) # Default 1 now
    
    files = request.files.getlist('images')
    
    uploaded_count = 0
    try:
        for file in files:
            if file and file.filename != '':
                res = optimize_and_upload(file) # Uses Cloudinary
                item_name = name_input if name_input else f"Mystery {rarity} Prize"
                
                new_item = MinifigurePool(name=item_name, rarity=rarity, stock=stock, image=res['secure_url'])
                db.session.add(new_item)
                uploaded_count += 1
                
        if uploaded_count > 0:
            db.session.commit()
            flash(f'{uploaded_count} Prize(s) added to game pool!', 'success')
        else:
            flash('No valid images found to upload.', 'error')
            
    except Exception as e:
        flash(f'Upload failed: {str(e)}', 'error')
        
    return redirect(url_for('admin_panel'))

@app.route('/admin/spin/update_stock/<int:id>', methods=['POST'])
@login_required
def update_spin_stock(id):
    item = MinifigurePool.query.get(id)
    if item:
        item.stock = int(request.form.get('stock', 0))
        # SYNC
        _sync_pool_to_product(item)
        db.session.commit()
        flash('Prize stock updated.', 'success')
    return redirect(url_for('admin_panel'))

# NEW ROUTE: For handling the Bulk Matrix Changes from Admin Panel
@app.route('/admin/spin/pool/update_bulk', methods=['POST'])
@login_required
def admin_spin_update_bulk():
    data = request.json
    item = MinifigurePool.query.get(data.get('id'))
    if item:
        item.rarity = data.get('rarity', item.rarity)
        item.sort_order = int(data.get('sort_order', item.sort_order))
        item.stock = int(data.get('stock', item.stock))
        
        # SYNC TO STORE
        _sync_pool_to_product(item)
        db.session.commit()
    return jsonify({"status": "success"})


@app.route('/admin/spin/pool/update_order/<int:item_id>', methods=['POST'])
@login_required
def update_spin_pool_order(item_id):
    item = MinifigurePool.query.get_or_404(item_id)
    item.sort_order = int(request.form.get('sort_order', 0))
    db.session.commit()
    return redirect(url_for('admin_panel'))


# --- INDIVIDUAL & BULK DELETE ROUTES FOR GAME ---
@app.route('/admin/spin/pool/update_rarity/<int:item_id>', methods=['POST'])
@login_required
def admin_spin_update_rarity(item_id):
    item = MinifigurePool.query.get_or_404(item_id)
    item.rarity = request.form.get('rarity')
    db.session.commit()
    flash('Item rarity updated successfully!', 'success')
    return redirect(url_for('admin_panel'))

@app.route('/admin/spin/pool/bulk_delete', methods=['POST'])
@login_required
def admin_spin_bulk_delete_pool():
    item_ids = request.form.get('item_ids', '')
    if item_ids:
        ids = [int(x) for x in item_ids.split(',') if x.isdigit()]
        MinifigurePool.query.filter(MinifigurePool.id.in_(ids)).delete(synchronize_session=False)
        db.session.commit()
        flash(f'Deleted {len(ids)} items from the Prize Pool!', 'success')
    return redirect(url_for('admin_panel'))

@app.route('/admin/spin/code/bulk_delete', methods=['POST'])
@login_required
def admin_spin_bulk_delete_code():
    code_ids = request.form.get('code_ids', '')
    if code_ids:
        ids = [int(x) for x in code_ids.split(',') if x.isdigit()]
        RedeemCode.query.filter(RedeemCode.id.in_(ids)).delete(synchronize_session=False)
        db.session.commit()
        flash(f'Deleted {len(ids)} codes!', 'success')
    return redirect(url_for('admin_panel'))

@app.route('/admin/spin/history/bulk_delete', methods=['POST'])
@login_required
def admin_spin_bulk_delete_history():
    history_ids = request.form.get('history_ids', '')
    if history_ids:
        ids = [int(x) for x in history_ids.split(',') if x.isdigit()]
        DrawHistory.query.filter(DrawHistory.id.in_(ids)).delete(synchronize_session=False)
        db.session.commit()
        flash(f'Deleted {len(ids)} history records!', 'success')
    return redirect(url_for('admin_panel'))

@app.route('/admin/spin/pool/delete/<int:item_id>', methods=['POST'])
@login_required
def admin_spin_delete_pool(item_id):
    item = MinifigurePool.query.get_or_404(item_id)
    db.session.delete(item)
    db.session.commit()
    flash('Prize Pool item deleted!', 'success')
    return redirect(url_for('admin_panel'))

@app.route('/admin/spin/history/delete/<int:draw_id>', methods=['POST'])
@login_required
def admin_spin_delete_history(draw_id):
    draw = DrawHistory.query.get_or_404(draw_id)
    db.session.delete(draw)
    db.session.commit()
    flash('Live draw history record deleted!', 'success')
    return redirect(url_for('admin_panel'))


# --- 9. STARTUP & MIGRATIONS ---
@app.errorhandler(413)
def request_entity_too_large(error):
    flash('File too large!', 'error')
    return redirect(url_for('admin_panel'))

with app.app_context():
    db.create_all()
    
    # --- AUTO MIGRATIONS FOR THE NEW SYNC FEATURES ---
    try:
        db.session.execute(text('ALTER TABLE minifigure_pool ADD COLUMN sort_order INTEGER DEFAULT 0'))
        db.session.commit()
    except Exception:
        db.session.rollback()
        
    try:
        db.session.execute(text('ALTER TABLE minifigure_pool ADD COLUMN linked_product_id INTEGER'))
        db.session.execute(text('ALTER TABLE minifigure_pool ADD COLUMN linked_variant_index INTEGER'))
        db.session.commit()
    except Exception:
        db.session.rollback()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))