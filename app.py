import os
import json
import time
import random
import string
import uuid
from datetime import datetime, timedelta
from functools import wraps
from flask import Flask, render_template, request, redirect, url_for, jsonify, session, flash, render_template_string
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
    store = db.Column(db.String(100), nullable=False) 
    variants = db.Column(db.Text, nullable=True)
    sort_order = db.Column(db.Integer, default=0)
    is_visible = db.Column(db.Boolean, default=True)
    discount_percent = db.Column(db.Float, default=0.0) 
    use_custom_thumbnail = db.Column(db.Boolean, default=False)
    detail_images = db.Column(db.Text, nullable=True)

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
    delivery_fee = db.Column(db.Float, default=0.0)
    status = db.Column(db.String(20), default="Pending")
    stock_deducted = db.Column(db.Boolean, default=False)
    promo_code_used = db.Column(db.String(50), nullable=True)
    
    # NEW TELEGRAM COLUMNS FOR CART SYNC
    telegram_id = db.Column(db.String(100), nullable=True)
    telegram_name = db.Column(db.String(200), nullable=True)
    telegram_user_payload = db.Column(db.Text, nullable=True) # <-- Stores full Telegram info (username, photo)
    
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

class PromoCode(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(50), unique=True, nullable=False)
    discount_type = db.Column(db.String(20), nullable=False) 
    discount_value = db.Column(db.Float, nullable=False)
    min_order_value = db.Column(db.Float, default=0.0)
    max_uses = db.Column(db.Integer, default=0)
    current_uses = db.Column(db.Integer, default=0)
    is_active = db.Column(db.Boolean, default=True)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

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

REWARD_CONFIG_FILE = 'spin_rewards.json'

def get_reward_config():
    if os.path.exists(REWARD_CONFIG_FILE):
        with open(REWARD_CONFIG_FILE, 'r') as f: 
            return json.load(f)
    return {"0": 50.0, "500": 20.0, "1000": 15.0, "2000": 10.0, "5000": 3.0, "10000": 1.5, "50000": 0.5}

def save_reward_config(data):
    with open(REWARD_CONFIG_FILE, 'w') as f: 
        json.dump(data, f)

def _sync_product_to_pool(product_id, variant_index, new_stock):
    linked_prize = MinifigurePool.query.filter_by(linked_product_id=product_id, linked_variant_index=variant_index).first()
    if linked_prize: 
        linked_prize.stock = new_stock
    else:
        product = Product.query.get(product_id)
        if product:
            target_image = product.image
            if variant_index != -1 and product.variants:
                try:
                    variants = json.loads(product.variants)
                    if 0 <= variant_index < len(variants): 
                        target_image = variants[variant_index].get('image', target_image)
                except Exception as e: 
                    print(f"Error parsing variants: {e}")
            
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
                except Exception as e: 
                    print(f"Error updating product variants: {e}")
            else: 
                product.stock = pool_item.stock
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
                except Exception: 
                    pass
            elif p.image == pool_item.image:
                p.stock = pool_item.stock
                pool_item.linked_product_id = p.id
                pool_item.linked_variant_index = -1
                break

@app.context_processor
def inject_global_data():
    if request.path.startswith('/admin') and session.get('admin'):
        products = Product.query.order_by(Product.sort_order.asc(), Product.id.desc()).all()
        for p in products: 
            p.parsed_variants = json.loads(p.variants) if p.variants else []
        categories = Category.query.order_by(Category.sort_order).all()
        promo_codes = PromoCode.query.order_by(PromoCode.timestamp.desc()).all()
        pending_count = Order.query.filter_by(status='Pending').count()
        return dict(global_products=products, global_categories=categories, global_redeem_codes=promo_codes, pending_count=pending_count)
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
@app.route('/minifigure')
def minifigure_store(): return render_template('minifigure.html')
@app.route('/mystery-box')
@app.route('/lucky-draw')
@app.route('/spin')
def mystery_box(): return render_template('lucky_draw.html')

@app.route('/checkout', methods=['POST'])
def checkout_page():
    cart_data_raw = request.form.get('cart_data', '[]')
    redeem_code = request.form.get('applied_redeem_code', '').strip().upper()
    try: 
        cart_items = json.loads(cart_data_raw)
    except: 
        cart_items = []
        
    if not cart_items: 
        return redirect(url_for('index'))
        
    subtotal = sum(float(item.get('price', 0)) * int(item.get('qty', 1)) for item in cart_items)
    discount_amount = 0
    if redeem_code:
        promo = PromoCode.query.filter_by(code=redeem_code, is_active=True).first()
        if promo and (promo.max_uses == 0 or promo.current_uses < promo.max_uses):
            if subtotal >= promo.min_order_value:
                if promo.discount_type == 'percent': 
                    discount_amount = subtotal * (promo.discount_value / 100.0)
                elif promo.discount_type == 'flat': 
                    discount_amount = promo.discount_value
                    
    final_total = max(0, subtotal - discount_amount)
    
    checkout_html = """
    <!DOCTYPE html>
    <html lang="en">
    <head><title>Secure Checkout</title><script src="https://cdn.tailwindcss.com"></script><link href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;600;800;900&display=swap" rel="stylesheet"></head>
    <body class="bg-slate-50 text-slate-800 p-4 md:p-10 font-['Plus_Jakarta_Sans']">
        <div class="max-w-2xl mx-auto bg-white p-6 md:p-8 rounded-3xl shadow-xl border border-slate-100">
            <h1 class="text-2xl font-black text-slate-900 mb-6 flex items-center gap-2"><svg class="w-6 h-6 text-[#ff5000]" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 3h2l.4 2M7 13h10l4-8H5.4M7 13L5.4 5M7 13l-2.293 2.293c-.63.63-.184 1.707.707 1.707H17m0 0a2 2 0 100 4 2 2 0 000-4zm-8 2a2 2 0 11-4 0 2 2 0 014 0z"></path></svg> Secure Checkout</h1>
            <div class="bg-slate-50 p-4 rounded-xl border border-slate-200 mb-6 space-y-1">
                <div class="flex justify-between items-center text-sm font-bold text-slate-500"><span>Subtotal</span><span>${{ "%.2f"|format(subtotal) }}</span></div>
                {% if discount_amount > 0 %}
                <div class="flex justify-between items-center text-sm font-bold text-emerald-500"><span>Discount Code ({{ redeem_code }})</span><span>-${{ "%.2f"|format(discount_amount) }}</span></div>
                {% endif %}
                <div class="flex justify-between items-end mt-2 border-t border-slate-200 pt-3">
                    <span class="text-xs font-black uppercase text-slate-900 tracking-wider">Total</span>
                    <div class="text-right">
                        <span class="text-xl font-black text-[#ff5000] leading-none block">${{ "%.2f"|format(final_total) }}</span>
                        <span class="text-[10px] font-bold text-slate-400 block">{{ (final_total * 4000)|int }} ៛</span>
                    </div>
                </div>
            </div>
            <form action="/place_order" method="POST" class="space-y-4">
                <input type="hidden" name="cart_data" value="{{ cart_data_raw }}">
                <input type="hidden" name="promo_code_used" value="{{ redeem_code if discount_amount > 0 else '' }}">
                <input type="hidden" name="final_total" value="{{ final_total }}">
                <div><label class="text-[10px] font-black text-slate-400 uppercase tracking-wider pl-1 block mb-1">Full Name</label><input type="text" name="name" required class="w-full bg-slate-50 border border-slate-200 rounded-xl px-4 py-3 text-sm font-bold text-slate-900 outline-none focus:border-[#ff5000] focus:ring-2 focus:ring-orange-500/10"></div>
                <div><label class="text-[10px] font-black text-slate-400 uppercase tracking-wider pl-1 block mb-1">Phone Number</label><input type="tel" name="phone" required class="w-full bg-slate-50 border border-slate-200 rounded-xl px-4 py-3 text-sm font-bold text-slate-900 outline-none focus:border-[#ff5000] focus:ring-2 focus:ring-orange-500/10"></div>
                <div><label class="text-[10px] font-black text-slate-400 uppercase tracking-wider pl-1 block mb-1">Delivery Address</label><textarea name="address" rows="3" required class="w-full bg-slate-50 border border-slate-200 rounded-xl px-4 py-3 text-sm font-bold text-slate-900 outline-none focus:border-[#ff5000] focus:ring-2 focus:ring-orange-500/10"></textarea></div>
                <div class="flex gap-3 pt-2">
                    <button type="button" onclick="history.back()" class="w-1/3 bg-slate-100 hover:bg-slate-200 text-slate-600 py-3.5 rounded-2xl text-xs font-black uppercase tracking-wider transition-all">Cancel</button>
                    <button type="submit" class="w-2/3 bg-[#ff5000] hover:bg-orange-600 text-white py-3.5 rounded-2xl text-xs font-black uppercase tracking-wider shadow-lg shadow-orange-500/20 transition-all">Confirm Order</button>
                </div>
            </form>
        </div>
    </body>
    </html>
    """
    return render_template_string(checkout_html, subtotal=subtotal, discount_amount=discount_amount, final_total=final_total, redeem_code=redeem_code, cart_data_raw=cart_data_raw)

@app.route('/place_order', methods=['POST'])
def place_order():
    client_ip = request.headers.get('X-Forwarded-For', request.remote_addr)
    if client_ip and ',' in client_ip: 
        client_ip = client_ip.split(',')[0].strip()
        
    current_time = time.time()
    if client_ip in spam_tracker:
        last_time, count = spam_tracker[client_ip]
        if current_time - last_time < 300:
            if count >= 2: 
                return "Too many orders. Please try again in 5 minutes.", 429
            spam_tracker[client_ip] = (last_time, count + 1)
        else: 
            spam_tracker[client_ip] = (current_time, 1)
    else: 
        spam_tracker[client_ip] = (current_time, 1)

    try:
        new_order = Order(
            customer_name=request.form.get('name'), 
            customer_phone=request.form.get('phone'), 
            customer_address=request.form.get('address'),
            items_json=request.form.get('cart_data'), 
            total_usd=float(request.form.get('final_total', 0)), 
            status="Pending",
            promo_code_used=request.form.get('promo_code_used')
        )
        db.session.add(new_order)
        db.session.commit()
        
        success_html = """
        <!DOCTYPE html><html lang="en"><head><title>Success</title><script src="https://cdn.tailwindcss.com"></script><link href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;600;800;900&display=swap" rel="stylesheet"></head>
        <body class="bg-slate-50 flex items-center justify-center min-h-screen text-center p-4 font-['Plus_Jakarta_Sans']">
            <div class="max-w-md w-full bg-white p-8 rounded-3xl shadow-xl border border-slate-100">
                <div class="w-16 h-16 bg-emerald-100 text-emerald-500 rounded-full flex items-center justify-center mx-auto mb-4"><svg class="w-8 h-8" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="3" d="M5 13l4 4L19 7"></path></svg></div>
                <h1 class="text-2xl font-black text-slate-900 mb-2">Order Confirmed!</h1>
                <p class="text-sm font-bold text-slate-500 mb-8">We have received your order #{{ order_id }}. We will contact you shortly.</p>
                <a href="/" class="block w-full bg-[#ff5000] text-white px-6 py-4 rounded-2xl text-xs font-black uppercase tracking-wider shadow-lg shadow-orange-500/20">Return to Homepage</a>
            </div><script>localStorage.removeItem('universal_store_cart');</script>
        </body></html>
        """
        return render_template_string(success_html, order_id=new_order.id)
    except Exception as e: 
        db.session.rollback()
        return f"Error: {str(e)}", 400

# =======================================================
# NEW: UPDATED CHECKOUT API ROUTE FOR UNIVERSAL CART
# =======================================================
@app.route('/api/checkout', methods=['POST'])
def checkout():
    data = request.json
    try:
        # 1. Parse Telegram details if sent from frontend
        tg_user = data.get('telegram_user')
        tg_id = str(tg_user.get('id')) if tg_user and tg_user.get('id') else None
        
        tg_name = None
        if tg_user:
            tg_name = tg_user.get('first_name', '')
            last_name = tg_user.get('last_name')
            if last_name:
                tg_name += f" {last_name}"

        # Convert the entire Telegram User object into a JSON string to save in the database
        tg_payload = json.dumps(tg_user) if tg_user else None

        # 2. Build the order
        new_order = Order(
            customer_name=data.get('name'), 
            customer_phone=data.get('phone'), 
            customer_address=data.get('address'),
            items_json=json.dumps(data.get('items', [])), 
            total_usd=float(data.get('total', 0) or 0), 
            delivery_fee=float(data.get('deliveryFee', 0) or 0),
            telegram_id=tg_id,           
            telegram_name=tg_name,       
            telegram_user_payload=tg_payload, # <-- FULL TELEGRAM INFO SAVED HERE
            status="Pending"
        )
        db.session.add(new_order)
        db.session.commit()
        return jsonify({'status': 'success', 'order_id': new_order.id})
    except Exception as e: 
        db.session.rollback()
        print(f"API Checkout Error: {e}")
        return jsonify({'status': 'error', 'message': str(e)}), 400

# --- ADMIN ROUTES ---
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
    return render_template('admin/dashboard.html', orders=orders, pending_count=sum(1 for o in orders if o.status == 'Pending'))

@app.route('/admin/inventory')
@login_required
def admin_inventory():
    unique_cats = db.session.query(Product.category, Product.store).distinct().all()
    for c_name, c_store in unique_cats:
        if c_name:
            for sub_cat in c_name.split(','):
                sub_cat = sub_cat.strip()
                if sub_cat and sub_cat != "Other" and not Category.query.filter_by(name=sub_cat).first():
                    db.session.add(Category(name=sub_cat, store="toy", sort_order=999))
    db.session.commit()
    return render_template('admin/inventory.html', products=Product.query.order_by(Product.sort_order.asc(), Product.id.desc()).all(), categories=Category.query.order_by(Category.sort_order).all())

@app.route('/admin/orders')
@login_required
def admin_orders():
    orders = Order.query.order_by(Order.timestamp.desc()).all()
    valid_orders = []
    
    for o in orders:
        try:
            o.parsed_items = json.loads(o.items_json) if o.items_json else []
        except Exception as e:
            print(f"Warning: Could not load items for order {o.id}: {e}")
            o.parsed_items = []
            
        o.items = o.parsed_items
        for item in o.items:
            if 'id' not in item:
                item['id'] = item.get('cartId', item.get('variantId', str(uuid.uuid4())[:8]))
                
        o.created_at = o.timestamp
        o.total_amount = o.total_usd
        
        # EXTRACT THE TELEGRAM PROFILE FOR THE ADMIN TEMPLATE
        try:
            o.telegram_user = json.loads(o.telegram_user_payload) if o.telegram_user_payload else None
        except Exception:
            o.telegram_user = None

        valid_orders.append(o)
        
    return render_template('admin/orders.html', global_orders=valid_orders)

@app.route('/admin/orders/confirm/<int:id>', methods=['POST'])
@login_required
def confirm_admin_order(id):
    order = Order.query.get(id)
    if order and order.status == 'Pending':
        if not order.stock_deducted:
            try:
                for item in json.loads(order.items_json):
                    parts = str(item.get('variantId', item.get('cartId', ''))).split('-')
                    if len(parts) >= 2 and parts[0].isdigit():
                        p_id = int(parts[0])
                        v_idx = int(parts[1]) if parts[1].isdigit() else -1
                        qty = int(item.get('qty', 1))
                        product = Product.query.get(p_id)
                        if product:
                            if product.variants and v_idx != -1:
                                variants = json.loads(product.variants)
                                if 0 <= v_idx < len(variants):
                                    variants[v_idx]['stock'] = max(0, int(variants[v_idx].get('stock', 0)) - qty)
                                    product.variants = json.dumps(variants)
                                    product.stock = sum(int(v.get('stock', 0)) for v in variants)
                                    _sync_product_to_pool(p_id, v_idx, variants[v_idx]['stock'])
                            else: 
                                product.stock = max(0, product.stock - qty)
                                _sync_product_to_pool(p_id, -1, product.stock)
                    elif item.get('cartId') and str(item.get('cartId')).isdigit():
                        product = Product.query.get(int(item.get('cartId')))
                        if product:
                            product.stock = max(0, product.stock - int(item.get('qty', 1)))
                            _sync_product_to_pool(product.id, -1, product.stock)
            except Exception as e: 
                print(f"Stock deduction error: {e}")
            
            if order.promo_code_used:
                promo = PromoCode.query.filter_by(code=order.promo_code_used).first()
                if promo: 
                    promo.current_uses += 1
            order.stock_deducted = True
        
        order.status = 'Processing'
        db.session.commit()
        flash('Order Confirmed and Stock Deducted!', 'success')
    return redirect(url_for('admin_orders'))

@app.route('/admin/orders/update/<int:id>', methods=['POST'])
@login_required
def update_admin_order(id):
    order = Order.query.get(id)
    if order:
        order.customer_name = request.form.get('customer_name', order.customer_name)
        order.customer_phone = request.form.get('customer_phone', order.customer_phone)
        order.customer_address = request.form.get('customer_address', order.customer_address)
        order.status = request.form.get('status', order.status)
        
        if 'total_usd' in request.form:
            try: 
                order.total_usd = float(request.form.get('total_usd'))
            except ValueError: 
                pass
            
        if 'delivery_fee' in request.form:
            try: 
                order.delivery_fee = float(request.form.get('delivery_fee'))
            except ValueError: 
                pass
        
        item_ids = request.form.getlist('item_ids[]')
        item_qtys = request.form.getlist('item_qtys[]')
        
        if item_ids and item_qtys:
            try:
                items = json.loads(order.items_json) if order.items_json else []
                for i, item_id in enumerate(item_ids):
                    for item in items:
                        if str(item.get('id', item.get('cartId', item.get('variantId', '')))) == str(item_id):
                            item['qty'] = int(item_qtys[i])
                order.items_json = json.dumps(items)
            except Exception as e:
                print(f"Error updating items: {e}")
        
        db.session.commit()
        flash('Order Information Updated Successfully!', 'success')
    return redirect(url_for('admin_orders'))

@app.route('/admin/spin')
@login_required
def admin_spin():
    return render_template('admin/spin.html', codes=RedeemCode.query.order_by(RedeemCode.timestamp.desc()).all(), pool=MinifigurePool.query.order_by(MinifigurePool.sort_order.asc(), MinifigurePool.id.desc()).all(), history=DrawHistory.query.order_by(DrawHistory.timestamp_utc.desc()).limit(100).all(), reward_config=get_reward_config())

@app.route('/admin/redeem')
@login_required
def admin_redeem(): 
    return render_template('admin/redeem.html')

@app.route('/admin/redeem/add', methods=['POST'])
@login_required
def add_promo_code():
    code = request.form.get('code', '').strip().upper()
    if PromoCode.query.filter_by(code=code).first(): 
        flash('Code already exists!', 'error')
    else:
        db.session.add(PromoCode(code=code, discount_type=request.form.get('discount_type'), discount_value=float(request.form.get('discount_value', 0)), min_order_value=float(request.form.get('min_order_value', 0)), max_uses=int(request.form.get('max_uses', 0))))
        db.session.commit()
    return redirect(url_for('admin_redeem'))

@app.route('/admin/redeem/toggle/<int:id>', methods=['POST'])
@login_required
def toggle_promo_code(id):
    code = PromoCode.query.get(id)
    if code: 
        code.is_active = not code.is_active
        db.session.commit()
    return redirect(url_for('admin_redeem'))

@app.route('/admin/redeem/delete/<int:id>', methods=['POST'])
@login_required
def delete_promo_code(id):
    code = PromoCode.query.get(id)
    if code: 
        db.session.delete(code)
        db.session.commit()
    return redirect(url_for('admin_redeem'))

@app.route('/admin/product/quick_stock', methods=['POST'])
@login_required
def quick_update_stock():
    data = request.json
    p_id = data.get('product_id')
    v_idx = data.get('variant_index') 
    new_stock = int(data.get('stock', 0))

    product = Product.query.get(p_id)
    if not product: 
        return jsonify({'success': False})

    if v_idx != -1 and product.variants:
        variants = json.loads(product.variants)
        if 0 <= v_idx < len(variants):
            variants[v_idx]['stock'] = new_stock
            product.variants = json.dumps(variants)
            product.stock = sum(int(v.get('stock', 0)) for v in variants)
    else: 
        product.stock = new_stock

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
                for item in json.loads(order.items_json):
                    parts = str(item.get('variantId', item.get('cartId', ''))).split('-')
                    if len(parts) >= 2:
                        p_id, v_idx, qty = int(parts[0]), int(parts[1]), int(item.get('qty', 1))
                        product = Product.query.get(p_id)
                        if product:
                            if product.variants and v_idx != -1:
                                variants = json.loads(product.variants)
                                if 0 <= v_idx < len(variants):
                                    variants[v_idx]['stock'] = max(0, int(variants[v_idx].get('stock', 0)) - qty)
                                    product.variants = json.dumps(variants)
                                    product.stock = sum(int(v.get('stock', 0)) for v in variants)
                                    _sync_product_to_pool(p_id, v_idx, variants[v_idx]['stock'])
                            else: 
                                product.stock = max(0, product.stock - qty)
                                _sync_product_to_pool(p_id, -1, product.stock)
            except Exception as e: 
                print(f"Error completing order stock sync: {e}")
                
            if order.promo_code_used:
                promo = PromoCode.query.filter_by(code=order.promo_code_used).first()
                if promo: promo.current_uses += 1
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

@app.route('/admin/order/bulk_delete', methods=['POST'])
@login_required
def bulk_delete_orders():
    raw_ids = request.form.get('order_ids', '')
    if raw_ids:
        ids_to_delete = [int(x) for x in raw_ids.split(',') if x.isdigit()]
        if ids_to_delete: 
            Order.query.filter(Order.id.in_(ids_to_delete)).delete(synchronize_session=False)
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
    except Exception as e: 
        db.session.rollback()
        print(f"Update Category error: {e}")
    return redirect(url_for('admin_inventory'))

@app.route('/admin/category/delete/<int:id>', methods=['POST'])
@login_required
def delete_category(id):
    c = Category.query.get(id)
    if c:
        products = Product.query.filter_by(category=c.name).all()
        for p in products: 
            p.category = "Other"
        db.session.delete(c)
        db.session.commit()
    return redirect(url_for('admin_inventory'))

@app.route('/admin/product/reorder', methods=['POST'])
@app.route('/admin/products/reorder', methods=['POST'])
@login_required
def admin_reorder_products():
    data = request.get_json()
    product_ids = data.get('product_ids', data.get('ids', []))
    try:
        for index, prod_id in enumerate(product_ids):
            product = Product.query.get(int(prod_id))
            if product:
                product.sort_order = index
                
        db.session.commit()
        return jsonify({"status": "success", "message": "Product sort order updated successfully"}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"status": "error", "message": str(e)}), 500

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
    stores = request.form.getlist('stores[]')
    p.store = ",".join(stores) if stores else "toy"
    p.discount_percent = float(request.form.get('discount_percent', 0.0) or 0.0)
    
    use_custom_thumb_val = request.form.get('use_custom_thumbnail')
    p.use_custom_thumbnail = True if str(use_custom_thumb_val).lower() == 'true' else False
    
    thumb_file = request.files.get('thumbnail')
    if p.use_custom_thumbnail and thumb_file and thumb_file.filename != '':
        try:
            upload_res = optimize_and_upload(thumb_file)
            if upload_res and 'secure_url' in upload_res:
                p.image = upload_res['secure_url']
        except Exception as e:
            print(f"Error uploading thumbnail: {e}")

    v_ids = request.form.getlist('v_ids[]')
    v_images = request.form.getlist('v_images[]')
    v_names = request.form.getlist('v_names[]')
    v_prices = request.form.getlist('v_prices[]')
    v_stocks = request.form.getlist('v_stocks[]')
    v_cats = request.form.getlist('v_categories[]')
    v_discounts = request.form.getlist('v_discounts[]') 
    
    updated_variants = []
    total_stock = 0
    for i in range(len(v_ids)):
        stock = int(v_stocks[i])
        updated_variants.append({
            "id": int(v_ids[i]), "image": v_images[i], "name": v_names[i],
            "price": float(v_prices[i]), "stock": stock, 
            "category": v_cats[i] if i < len(v_cats) else p.category,
            "discount_percent": float(v_discounts[i]) if i < len(v_discounts) else 0.0 
        })
        total_stock += stock
        _sync_product_to_pool(p.id, int(v_ids[i]), stock)

    new_files = request.files.getlist('new_images')
    if new_files and new_files[0].filename != '':
        last_id = max([v['id'] for v in updated_variants]) if updated_variants else 0
        for f in new_files:
            if f and f.filename != '':
                try:
                    res = optimize_and_upload(f)
                    last_id += 1
                    updated_variants.append({
                        "id": last_id, "name": f"New Style {last_id}", "price": updated_variants[0]['price'] if updated_variants else 0, 
                        "stock": 1, "image": res['secure_url'], "category": p.category, "discount_percent": 0.0
                    })
                    total_stock += 1
                except Exception as e: 
                    print(f"Error adding new variant image: {e}")
    
    d_list = []
    try: 
        if getattr(p, 'detail_images', None): 
            d_list = json.loads(p.detail_images)
    except: pass

    new_detail_files = request.files.getlist('new_detail_images')
    if new_detail_files and new_detail_files[0].filename != '':
        for df in new_detail_files:
            if df and df.filename != '':
                try:
                    upload_result = optimize_and_upload(df)
                    if upload_result and 'secure_url' in upload_result:
                        d_list.append(upload_result['secure_url'])
                except Exception as e:
                    print(f"Error uploading detail image: {e}")
                    pass
    p.detail_images = json.dumps(d_list)

    p.variants = json.dumps(updated_variants)
    p.stock = total_stock
    if updated_variants:
        if not p.use_custom_thumbnail:
            p.image = updated_variants[0]['image']
        p.price = updated_variants[0]['price']
    db.session.commit()
    return redirect(url_for('admin_inventory'))

@app.route('/admin/product/add', methods=['POST'])
@login_required
def add_product():
    title = request.form.get('title')
    category = request.form.get('category')
    stores = request.form.getlist('stores[]')
    store_str = ",".join(stores) if stores else "toy"
    discount_percent = float(request.form.get('discount_percent', 0.0) or 0.0)
    
    use_custom_thumb = str(request.form.get('use_custom_thumbnail')).lower() == 'true'
    thumb_file = request.files.get('thumbnail')
    thumbnail_url = ""
    
    if use_custom_thumb and thumb_file and thumb_file.filename != '':
        try:
            res = optimize_and_upload(thumb_file)
            if res and 'secure_url' in res:
                thumbnail_url = res['secure_url']
        except Exception as e: 
            print(f"Upload error: {e}")
    
    v_names = request.form.getlist('variant_names[]')
    v_prices = request.form.getlist('variant_prices[]')
    v_stocks = request.form.getlist('variant_stocks[]')
    v_categories = request.form.getlist('variant_categories[]')
    v_discounts = request.form.getlist('variant_discounts[]')
    
    files = request.files.getlist('images')
    uploaded_urls = []
    for f in files:
        if f and f.filename != '': 
            try: 
                uploaded_urls.append(optimize_and_upload(f)['secure_url'])
            except: 
                pass
    
    detail_files = request.files.getlist('detail_images')
    detail_urls = []
    if detail_files and detail_files[0].filename != '':
        for df in detail_files:
            if df and df.filename != '': 
                try: 
                    detail_urls.append(optimize_and_upload(df)['secure_url'])
                except: 
                    pass

    if uploaded_urls:
        vars_json = []
        total_stock = 0
        for i, url in enumerate(uploaded_urls):
            price = float(v_prices[i]) if i < len(v_prices) else 0
            stock = int(v_stocks[i]) if i < len(v_stocks) else 0
            cat_str = v_categories[i] if i < len(v_categories) else category
            v_disc = float(v_discounts[i]) if i < len(v_discounts) else 0.0
            vars_json.append({
                "id": i, "name": v_names[i] if i < len(v_names) else f"Style {i+1}", 
                "price": price, "stock": stock, "image": url, "category": cat_str, "discount_percent": v_disc
            })
            total_stock += stock
            
        if not use_custom_thumb or not thumbnail_url:
            thumbnail_url = uploaded_urls[0]
            
        new_p = Product(
            title=title, price=vars_json[0]['price'], stock=total_stock, 
            image=thumbnail_url, category=category, store=store_str, 
            discount_percent=discount_percent, variants=json.dumps(vars_json), 
            sort_order=-1, is_visible=True,
            use_custom_thumbnail=use_custom_thumb,
            detail_images=json.dumps(detail_urls)
        )
        db.session.add(new_p)
        db.session.commit()
    return redirect(url_for('admin_inventory'))

@app.route('/api/products/<store_name>')
def get_api(store_name):
    try:
        all_prods = Product.query.filter_by(is_visible=True).order_by(Product.sort_order.asc(), Product.id.desc()).all()
        
        product_list = []
        for p in all_prods:
            if store_name not in (p.store or '').split(','):
                continue
            
            v_list = []
            try:
                if p.variants: 
                    v_list = json.loads(p.variants)
            except: pass
            
            d_list = []
            try:
                if getattr(p, 'detail_images', None): 
                    d_list = json.loads(p.detail_images)
            except: pass
            
            product_list.append({
                "id": p.id,
                "title": p.title,
                "price": p.price,
                "stock": p.stock,
                "category": p.category, 
                "thumbnail": p.image,
                "discount_percent": getattr(p, 'discount_percent', 0.0) or 0.0,
                "use_custom_thumbnail": getattr(p, 'use_custom_thumbnail', False) or False,
                "detail_images": d_list,
                "variants": v_list
            })
            
        categories = Category.query.order_by(Category.sort_order.asc()).all()
        return jsonify({
            "products": product_list,
            "categories": [{"name": c.name, "image": c.image} for c in categories]
        })
    except Exception as e: 
        print(f"CRITICAL API ERROR: {str(e)}")
        return jsonify({"products": [], "categories": [], "error": str(e)}), 200

@app.route('/admin/spin/update_rewards', methods=['POST'])
@login_required
def update_spin_rewards():
    data = { "0": float(request.form.get("pct_0", 50)), "500": float(request.form.get("pct_500", 20)), "1000": float(request.form.get("pct_1000", 15)), "2000": float(request.form.get("pct_2000", 10)), "5000": float(request.form.get("pct_5000", 3)), "10000": float(request.form.get("pct_10000", 1.5)), "50000": float(request.form.get("pct_50000", 0.5)) }
    save_reward_config(data)
    flash('5x Spin Probabilities updated!', 'success')
    return redirect(url_for('admin_spin'))

@app.route('/admin/spin/generate_codes', methods=['POST'])
@login_required
def generate_codes():
    quantity = int(request.form.get('quantity', 5))
    value = int(request.form.get('value', 1000))
    for _ in range(quantity): 
        db.session.add(RedeemCode(code=''.join(random.choice(string.ascii_uppercase + string.digits) for i in range(8)), value=value))
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
        if file and file.filename != '': 
            db.session.add(MinifigurePool(name=request.form.get('name', '').strip() or f"Mystery {rarity} Prize", rarity=rarity, stock=stock, image=optimize_and_upload(file)['secure_url']))
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
        item.rarity = request.json.get('rarity', item.rarity)
        item.sort_order = int(request.json.get('sort_order', item.sort_order))
        item.stock = int(request.json.get('stock', item.stock))
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
def request_entity_too_large(error): 
    return redirect(request.referrer)

# ==============================================================
# AUTO DATABASE MIGRATION FOR TELEGRAM COLUMNS
# ==============================================================
with app.app_context():
    db.create_all()
    queries = [
        'ALTER TABLE "order" ADD COLUMN promo_code_used VARCHAR(50)',
        'ALTER TABLE product ADD COLUMN discount_percent FLOAT DEFAULT 0.0',
        'ALTER TABLE product ADD COLUMN use_custom_thumbnail BOOLEAN DEFAULT FALSE',
        'ALTER TABLE product ADD COLUMN detail_images TEXT',
        'ALTER TABLE "order" ADD COLUMN delivery_fee FLOAT DEFAULT 0.0',
        
        # <-- NEW COLUMNS ADDED HERE -->
        'ALTER TABLE "order" ADD COLUMN telegram_id VARCHAR(100)',
        'ALTER TABLE "order" ADD COLUMN telegram_name VARCHAR(200)',
        'ALTER TABLE "order" ADD COLUMN telegram_user_payload TEXT'
    ]
    for q in queries:
        try:
            db.session.execute(text(q))
            db.session.commit()
        except:
            db.session.rollback()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))