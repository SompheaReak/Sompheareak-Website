
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
        file, format="webp", quality="auto", width=900, height=900, crop="limit"
    )

# --- 2. PERMANENT DATABASE CONFIG ---
db_url = os.environ.get('DATABASE_URL', 'sqlite:///fallback.db')
if db_url.startswith("postgres://"):
    db_url = db_url.replace("postgres://", "postgresql://", 1)

app.config['SQLALCHEMY_DATABASE_URI'] = db_url
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {
    "pool_pre_ping": True, "pool_recycle": 300, "pool_timeout": 30      
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
    linked_product_id = db.Column(db.Integer, nullable=True)
    linked_variant_index = db.Column(db.Integer, nullable=True)

class DrawHistory(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    player_id = db.Column(db.String(8), nullable=False)
    item_name = db.Column(db.String(200), nullable=False)
    rarity = db.Column(db.String(50), nullable=False)
    stock_remaining = db.Column(db.Integer, nullable=False)
    timestamp_utc = db.Column(db.DateTime, default=datetime.utcnow)

    @property
    def cambodia_time(self):
        kh_time = self.timestamp_utc + timedelta(hours=7)
        return kh_time.strftime('%d-%b-%Y %I:%M %p')

# --- 5x SPIN CASH REWARD CONFIG ---
REWARD_CONFIG_FILE = 'spin_rewards.json'

def get_reward_config():
    if os.path.exists(REWARD_CONFIG_FILE):
        with open(REWARD_CONFIG_FILE, 'r') as f:
            return json.load(f)
    return {"0": 50.0, "500": 20.0, "1000": 15.0, "2000": 10.0, "5000": 3.0, "10000": 1.5, "50000": 0.5}

def save_reward_config(data):
    with open(REWARD_CONFIG_FILE, 'w') as f:
        json.dump(data, f)

# --- SYNC HELPER FUNCTIONS ---
def _sync_product_to_pool(product_id, variant_index, new_stock):
    linked_prize = MinifigurePool.query.filter_by(linked_product_id=product_id, linked_variant_index=variant_index).first()
    if linked_prize: linked_prize.stock = new_stock
    else:
        product = Product.query.get(product_id)
        if product:
            target_image = product.image
            if variant_index != -1 and product.variants:
                try:
                    variants = json.loads(product.variants)
                    if 0 <= variant_index < len(variants): target_image = variants[variant_index].get('image', target_image)
                except: pass
            
            prize = MinifigurePool.query.filter_by(image=target_image).first()
            if prize:
                prize.stock = new_stock
                prize.linked_product_id = product_id
                prize.linked_variant_index = variant_index

def _sync_pool_to_product(pool_item):
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
                except: pass
            else: product.stock = pool_item.stock
    else:
        products = Product.query.all()
        for p in products:
            if p.variants:
                try:
                    variants = json.loads(p.variants)
                    updated = False
                    for idx, v in enumerate(variants):
                        if v.get('image') == pool_item.image:
                            variants[idx]['stock'] = pool_item.stock
                            updated = True
                            pool_item.linked_product_id = p.id
                            pool_item.linked_variant_index = idx
                    if updated:
                        p.variants = json.dumps(variants)
                        p.stock = sum(int(v.get('stock', 0)) for v in variants)
                        break
                except: pass
            elif p.image == pool_item.image:
                p.stock = pool_item.stock
                pool_item.linked_product_id = p.id
                pool_item.linked_variant_index = -1
                break

# --- GLOBAL ADMIN CONTEXT ---
@app.context_processor
def inject_global_data():
    if request.path.startswith('/admin') and session.get('admin'):
        products = Product.query.order_by(Product.sort_order.asc(), Product.id.desc()).all()
        for p in products: p.parsed_variants = json.loads(p.variants) if p.variants else []
        categories = Category.query.order_by(Category.sort_order).all()
        pending_count = Order.query.filter_by(status='Pending').count()
        return dict(
            global_products=products,
            global_categories=categories,
            pending_count=pending_count
        )
    return dict()

# --- 5. PUBLIC & STORE ROUTES ---
@app.route('/')
def index(): return render_template('index.html')

@app.route('/toy-universe')
def toy_universe(): return render_template('toy.html')

@app.route('/lego')
def lego_store(): return render_template('lego.html')

@app.route('/bracelet')
def shop(): return render_template('bracelet.html')

@app.route('/custom-bracelet')
def custom_bracelet(): return render_template('custom_bracelet.html')

# !!! HERE IS THE MISSING ROUTE !!!
@app.route('/mystery-box')
@app.route('/lucky-draw')
@app.route('/spin')
def mystery_box(): 
    return render_template('lucky_draw.html')

@app.route('/api/checkout', methods=['POST'])
def checkout():
    client_ip = request.headers.get('X-Forwarded-For', request.remote_addr)
    if client_ip and ',' in client_ip: client_ip = client_ip.split(',')[0].strip()
        
    current_time = time.time()
    if client_ip in spam_tracker:
        last_time, count = spam_tracker[client_ip]
        if current_time - last_time < 300:
            if count >= 2: return jsonify({'status': 'error', 'message': 'Too many orders. Try again in 5 minutes.'}), 429
            spam_tracker[client_ip] = (last_time, count + 1)
        else: spam_tracker[client_ip] = (current_time, 1)
    else: spam_tracker[client_ip] = (current_time, 1)

    data = request.json
    try:
        new_order = Order(
            customer_name=data['name'], customer_phone=data['phone'], customer_address=data['address'],
            items_json=json.dumps(data['items']), total_usd=float(data['total']), status="Pending"
        )
        db.session.add(new_order)
        db.session.commit()
        return jsonify({'status': 'success', 'order_id': new_order.id})
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 400

# --- MULTI-PAGE ADMIN ROUTES ---
@app.route('/admin/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        if request.form.get('username') == ADMIN_USERNAME and request.form.get('password') == ADMIN_PASS:
            session['admin'] = True
            return redirect(url_for('admin_dashboard'))
        flash('Invalid Username or Password', 'error')
    return render_template('admin_login.html')

@app.route('/admin/logout')
def logout():
    session.pop('admin', None)
    return redirect(url_for('login'))

@app.route('/admin/panel')
@login_required
def admin_panel():
    return redirect(url_for('admin_dashboard'))

@app.route('/admin/dashboard')
@login_required
def admin_dashboard():
    orders = Order.query.all()
    pending_count = sum(1 for o in orders if o.status == 'Pending')
    return render_template('admin/dashboard.html', orders=orders, pending_count=pending_count)

@app.route('/admin/inventory')
@login_required
def admin_inventory():
    # 1. SMART AUTO-SYNC CATEGORIES
    unique_cats = db.session.query(Product.category, Product.store).distinct().all()
    for c_name, c_store in unique_cats:
        if c_name:
            # Handles comma separated tags perfectly
            for sub_cat in c_name.split(','):
                sub_cat = sub_cat.strip()
                if sub_cat and sub_cat != "Other" and not Category.query.filter_by(name=sub_cat, store=c_store).first():
                    db.session.add(Category(name=sub_cat, store=c_store, sort_order=999))
    db.session.commit()
    
    # 2. LOAD INVENTORY
    products = Product.query.order_by(Product.sort_order.asc(), Product.id.desc()).all()
    for p in products: p.parsed_variants = json.loads(p.variants) if p.variants else []
    categories = Category.query.order_by(Category.sort_order).all()
    
    return render_template('admin/inventory.html', products=products, categories=categories)

@app.route('/admin/orders')
@login_required
def admin_orders():
    orders = Order.query.order_by(Order.timestamp.desc()).all()
    for o in orders: o.parsed_items = json.loads(o.items_json)
    return render_template('admin/orders.html', orders=orders)

@app.route('/admin/spin')
@login_required
def admin_spin():
    codes = RedeemCode.query.order_by(RedeemCode.timestamp.desc()).all()
    pool = MinifigurePool.query.order_by(MinifigurePool.sort_order.asc(), MinifigurePool.id.desc()).all()
    history = DrawHistory.query.order_by(DrawHistory.timestamp_utc.desc()).limit(100).all()
    reward_config = get_reward_config()
    return render_template('admin/spin.html', codes=codes, pool=pool, history=history, reward_config=reward_config)


# --- ADMIN API & FORM ACTIONS ---

@app.route('/admin/product/quick_stock', methods=['POST'])
@login_required
def quick_update_stock():
    data = request.json
    p_id = data.get('product_id')
    v_idx = data.get('variant_index') 
    new_stock = int(data.get('stock', 0))

    product = Product.query.get(p_id)
    if not product: return jsonify({'success': False})

    if v_idx != -1 and product.variants:
        variants = json.loads(product.variants)
        if 0 <= v_idx < len(variants):
            variants[v_idx]['stock'] = new_stock
            product.variants = json.dumps(variants)
            product.stock = sum(int(v.get('stock', 0)) for v in variants)
    else: product.stock = new_stock

    _sync_product_to_pool(p_id, v_idx, new_stock)
    db.session.commit()
    return jsonify({'success': True})

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
                            if product.variants and v_idx != -1:
                                variants = json.loads(product.variants)
                                if 0 <= v_idx < len(variants):
                                    variants[v_idx]['stock'] = max(0, variants[v_idx]['stock'] - qty_bought)
                                    product.variants = json.dumps(variants)
                                    product.stock = sum(v.get('stock', 0) for v in variants)
                                    _sync_product_to_pool(p_id, v_idx, variants[v_idx]['stock'])
                            else:
                                product.stock = max(0, product.stock - qty_bought)
                                _sync_product_to_pool(p_id, -1, product.stock)
            except: pass
            order.stock_deducted = True

        order.status = status
        db.session.commit()
    return redirect(url_for('admin_orders'))

@app.route('/admin/order/delete/<int:id>', methods=['POST'])
@login_required
def delete_order(id):
    order = Order.query.get(id)
    if order:
        db.session.delete(order)
        db.session.commit()
    return redirect(url_for('admin_orders'))

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
                    cat.image = optimize_and_upload(file)['secure_url']
        db.session.commit()
    except: pass
    return redirect(url_for('admin_inventory'))

@app.route('/admin/category/delete/<int:id>', methods=['POST'])
@login_required
def delete_category(id):
    c = Category.query.get(id)
    if c:
        products = Product.query.filter_by(category=c.name, store=c.store).all()
        for p in products: p.category = "Other"
        db.session.delete(c)
        db.session.commit()
    return redirect(url_for('admin_inventory'))

@app.route('/admin/product/reorder', methods=['POST'])
@login_required
def reorder_products():
    for i, pid in enumerate(request.json.get('ids', [])):
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
    return redirect(url_for('admin_inventory'))

@app.route('/admin/product/delete/<int:id>', methods=['POST'])
@login_required
def delete_product(id):
    p = Product.query.get(id)
    if p:
        db.session.delete(p)
        db.session.commit()
    return redirect(url_for('admin_inventory'))

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
            "id": int(v_ids[i]), "image": v_images[i], "name": v_names[i],
            "price": float(v_prices[i]), "stock": stock, "category": v_cats[i] if i < len(v_cats) else p.category
        })
        total_stock += stock
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
                        "id": last_id, "name": f"New Style {last_id}", "price": updated_variants[0]['price'] if updated_variants else 0, 
                        "stock": 1, "image": res['secure_url'], "category": p.category 
                    })
                    total_stock += 1
        p.variants = json.dumps(updated_variants)
        p.stock = total_stock
        if updated_variants:
            p.image = updated_variants[0]['image']
            p.price = updated_variants[0]['price']
        db.session.commit()
    except: pass
    return redirect(url_for('admin_inventory'))

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
            if f and f.filename != '': uploaded_urls.append(optimize_and_upload(f)['secure_url'])
        if uploaded_urls:
            vars_json = []
            total_stock = 0
            for i, url in enumerate(uploaded_urls):
                price = float(v_prices[i]) if i < len(v_prices) else 0
                stock = int(v_stocks[i]) if i < len(v_stocks) else 0
                cat_str = v_categories[i] if i < len(v_categories) else category
                vars_json.append({"id": i, "name": v_names[i] if i < len(v_names) else f"Style {i+1}", "price": price, "stock": stock, "image": url, "category": cat_str})
                total_stock += stock
            new_p = Product(title=title, price=vars_json[0]['price'], stock=total_stock, image=uploaded_urls[0], category=category, store=store, variants=json.dumps(vars_json), sort_order=-1, is_visible=True)
            db.session.add(new_p)
            db.session.commit()
    except: pass
    return redirect(url_for('admin_inventory'))

@app.route('/api/products/<store_name>')
def get_api(store_name):
    try:
        products = Product.query.filter_by(store=store_name, is_visible=True).order_by(Product.sort_order.asc(), Product.id.desc()).all()
        categories = Category.query.filter_by(store=store_name).order_by(Category.sort_order.asc()).all()
        return jsonify({
            "products": [{"id": p.id, "title": p.title, "price": p.price, "stock": p.stock, "category": p.category, "thumbnail": p.image, "variants": json.loads(p.variants)} for p in products],
            "categories": [{"name": c.name, "image": c.image} for c in categories]
        })
    except Exception as e: return jsonify({"error": str(e)}), 500

# --- 7. GAME API & REWARD SYSTEM ---

def get_player():
    if 'player_id' not in session:
        new_id = str(random.randint(10000000, 99999999))
        session['player_id'] = new_id
        db.session.add(PlayerSession(player_id=new_id, balance=0))
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
    
    if player.balance < cost: return jsonify({"error": "Insufficient Riel."}), 400

    available_items = MinifigurePool.query.filter(MinifigurePool.stock > 0).all()
    if not available_items or sum([item.stock for item in available_items]) < count:
        return jsonify({"error": "Not enough stock!"}), 400

    pool = []
    for item in available_items:
        if item.rarity == 'Legendary': weight = 2
        elif item.rarity == 'Epic': weight = 10
        elif item.rarity == 'Rare': weight = 30
        else: weight = 58 
        pool.extend([item] * weight)

    if not pool: return jsonify({"error": "Error building prize pool"}), 400

    prizes = []
    for _ in range(count):
        winner = random.choice(pool)
        winner.stock -= 1 
        _sync_pool_to_product(winner)
        db.session.add(DrawHistory(player_id=player.player_id, item_name=winner.name, rarity=winner.rarity, stock_remaining=winner.stock))
        prizes.append({"id": winner.id, "name": winner.name, "image": winner.image, "rarity": winner.rarity})
        pool = [i for i in pool if i.stock > 0]
        if not pool and _ < count - 1: break

    player.balance -= cost 

    # --- 5X EXTRA REWARD LOGIC ---
    extra_reward_amount = 0
    if count == 5:
        cfg = get_reward_config()
        amounts = [0, 500, 1000, 2000, 5000, 10000, 50000]
        try:
            weights = [float(cfg.get(str(a), 0)) for a in amounts]
            if sum(weights) <= 0: weights = [100, 0, 0, 0, 0, 0, 0] # Fallback
            extra_reward_amount = random.choices(amounts, weights=weights, k=1)[0]
            if extra_reward_amount > 0:
                player.balance += extra_reward_amount
        except Exception as e: pass

    db.session.commit()
    return jsonify({"success": True, "new_balance": player.balance, "prizes": prizes, "extra_reward": extra_reward_amount})

@app.route('/api/spin/pool', methods=['GET'])
def get_live_pool():
    items = MinifigurePool.query.all()
    return jsonify({"pool": [{"id": i.id, "name": i.name, "image": i.image, "rarity": i.rarity, "stock": i.stock} for i in items]})

# --- 8. SPINNER ADMIN ROUTES ---

@app.route('/admin/spin/update_rewards', methods=['POST'])
@login_required
def update_spin_rewards():
    data = {
        "0": float(request.form.get("pct_0", 50)),
        "500": float(request.form.get("pct_500", 20)),
        "1000": float(request.form.get("pct_1000", 15)),
        "2000": float(request.form.get("pct_2000", 10)),
        "5000": float(request.form.get("pct_5000", 3)),
        "10000": float(request.form.get("pct_10000", 1.5)),
        "50000": float(request.form.get("pct_50000", 0.5)),
    }
    save_reward_config(data)
    flash('5x Spin Probabilities updated!', 'success')
    return redirect(url_for('admin_spin'))

@app.route('/admin/spin/generate_codes', methods=['POST'])
@login_required
def generate_codes():
    quantity = int(request.form.get('quantity', 5))
    value = int(request.form.get('value', 1000))
    for _ in range(quantity): db.session.add(RedeemCode(code=''.join(random.choice(string.ascii_uppercase + string.digits) for i in range(8)), value=value))
    db.session.commit()
    return redirect(url_for('admin_spin'))

@app.route('/admin/spin/add_pool_catalog', methods=['POST'])
@login_required
def add_pool_catalog():
    for item_data in request.form.getlist('catalog_items[]'):
        parts = item_data.split('|')
        if len(parts) == 2:
            p_id, v_idx = int(parts[0]), int(parts[1])
            product = Product.query.get(p_id)
            if product:
                image, name, stock = product.image, product.title, product.stock
                if v_idx != -1 and product.variants:
                    try:
                        variants = json.loads(product.variants)
                        if 0 <= v_idx < len(variants):
                            image = variants[v_idx].get('image', image)
                            name = f"{variants[v_idx].get('name', 'Variant')} {product.title}"
                            stock = variants[v_idx].get('stock', 0)
                    except: pass
                if not MinifigurePool.query.filter_by(linked_product_id=p_id, linked_variant_index=v_idx).first():
                    db.session.add(MinifigurePool(name=name, rarity=request.form.get('rarity', 'Common'), stock=stock, image=image, linked_product_id=p_id, linked_variant_index=v_idx))
    db.session.commit()
    return redirect(url_for('admin_spin'))

@app.route('/admin/spin/add_pool', methods=['POST'])
@login_required
def add_spin_pool():
    rarity = request.form.get('rarity')
    stock = int(request.form.get('stock', 1))
    for file in request.files.getlist('images'):
        if file and file.filename != '': db.session.add(MinifigurePool(name=request.form.get('name', '').strip() or f"Mystery {rarity} Prize", rarity=rarity, stock=stock, image=optimize_and_upload(file)['secure_url']))
    db.session.commit()
    return redirect(url_for('admin_spin'))

@app.route('/admin/spin/update_stock/<int:id>', methods=['POST'])
@login_required
def update_spin_stock(id):
    item = MinifigurePool.query.get(id)
    if item:
        item.stock = int(request.form.get('stock', 0))
        _sync_pool_to_product(item)
        db.session.commit()
    return redirect(url_for('admin_spin'))

@app.route('/admin/spin/pool/update_bulk', methods=['POST'])
@login_required
def admin_spin_update_bulk():
    item = MinifigurePool.query.get(request.json.get('id'))
    if item:
        item.rarity, item.sort_order, item.stock = request.json.get('rarity', item.rarity), int(request.json.get('sort_order', item.sort_order)), int(request.json.get('stock', item.stock))
        _sync_pool_to_product(item)
        db.session.commit()
    return jsonify({"status": "success"})

@app.route('/admin/spin/pool/update_order/<int:item_id>', methods=['POST'])
@login_required
def update_spin_pool_order(item_id):
    MinifigurePool.query.get_or_404(item_id).sort_order = int(request.form.get('sort_order', 0))
    db.session.commit()
    return redirect(url_for('admin_spin'))

@app.route('/admin/spin/pool/update_rarity/<int:item_id>', methods=['POST'])
@login_required
def admin_spin_update_rarity(item_id):
    MinifigurePool.query.get_or_404(item_id).rarity = request.form.get('rarity')
    db.session.commit()
    return redirect(url_for('admin_spin'))

@app.route('/admin/spin/pool/bulk_delete', methods=['POST'])
@login_required
def admin_spin_bulk_delete_pool():
    if request.form.get('item_ids'):
        MinifigurePool.query.filter(MinifigurePool.id.in_([int(x) for x in request.form.get('item_ids').split(',') if x.isdigit()])).delete(synchronize_session=False)
        db.session.commit()
    return redirect(url_for('admin_spin'))

@app.route('/admin/spin/code/bulk_delete', methods=['POST'])
@login_required
def admin_spin_bulk_delete_code():
    if request.form.get('code_ids'):
        RedeemCode.query.filter(RedeemCode.id.in_([int(x) for x in request.form.get('code_ids').split(',') if x.isdigit()])).delete(synchronize_session=False)
        db.session.commit()
    return redirect(url_for('admin_spin'))

@app.route('/admin/spin/history/bulk_delete', methods=['POST'])
@login_required
def admin_spin_bulk_delete_history():
    if request.form.get('history_ids'):
        DrawHistory.query.filter(DrawHistory.id.in_([int(x) for x in request.form.get('history_ids').split(',') if x.isdigit()])).delete(synchronize_session=False)
        db.session.commit()
    return redirect(url_for('admin_spin'))

@app.route('/admin/spin/pool/delete/<int:item_id>', methods=['POST'])
@login_required
def admin_spin_delete_pool(item_id):
    db.session.delete(MinifigurePool.query.get_or_404(item_id))
    db.session.commit()
    return redirect(url_for('admin_spin'))

@app.route('/admin/spin/history/delete/<int:draw_id>', methods=['POST'])
@login_required
def admin_spin_delete_history(draw_id):
    db.session.delete(DrawHistory.query.get_or_404(draw_id))
    db.session.commit()
    return redirect(url_for('admin_spin'))

@app.errorhandler(413)
def request_entity_too_large(error): return redirect(request.referrer)

with app.app_context():
    db.create_all()
    try: db.session.execute(text('ALTER TABLE minifigure_pool ADD COLUMN sort_order INTEGER DEFAULT 0')); db.session.commit()
    except: db.session.rollback()
    try: db.session.execute(text('ALTER TABLE minifigure_pool ADD COLUMN linked_product_id INTEGER')); db.session.execute(text('ALTER TABLE minifigure_pool ADD COLUMN linked_variant_index INTEGER')); db.session.commit()
    except: db.session.rollback()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))



