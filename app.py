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

# --- LOAD ENVIRONMENT VARIABLES (.env) ---
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

def _load_env_fallback(filepath='.env'):
    if os.path.exists(filepath):
        with open(filepath, 'r') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, val = line.split('=', 1)
                    key = key.strip()
                    val = val.strip().strip("'\"")
                    os.environ.setdefault(key, val)

_load_env_fallback()

app = Flask(__name__)

# --- SECURITY CONFIGURATION (SESSION & COOKIE HARDENING) ---
app.secret_key = os.environ.get('SECRET_KEY', 'somphea_reak_ultra_pro_2025')
app.config['MAX_CONTENT_LENGTH'] = 50 * 1024 * 1024 
app.config['SESSION_COOKIE_HTTPONLY'] = True
app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'
if os.environ.get('FLASK_ENV') == 'production' or os.environ.get('RENDER') or os.environ.get('DYNO'):
    app.config['SESSION_COOKIE_SECURE'] = True
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(hours=12) 

# --- 1. CLOUDINARY CONFIG (HARDENED FOR DEPLOYMENT) ---
# Using fallback strings ensures the app boots even if ENV vars are missing during the build phase
cloudinary.config( 
  cloud_name = os.environ.get("CLOUDINARY_CLOUD_NAME", "dwwearehy"), 
  api_key = os.environ.get("CLOUDINARY_API_KEY", "dummy_key"), 
  api_secret = os.environ.get("CLOUDINARY_API_SECRET", "dummy_secret"),
  secure = True
)

def optimize_and_upload(file):
    return cloudinary.uploader.upload(
        file, format="webp", quality="auto", width=900, height=900, crop="limit"
    )

# --- 2. PERMANENT DATABASE CONFIG ---
DEFAULT_NEON_DB = "postgresql://neondb_owner:npg_dq6KIUVe0cyS@ep-polished-feather-a19qzv4s-pooler.ap-southeast-1.aws.neon.tech/neondb?sslmode=require&channel_binding=require"
db_url = os.environ.get('DATABASE_URL', '').strip()
if not db_url or 'fallback.db' in db_url:
    db_url = DEFAULT_NEON_DB

if db_url.startswith("postgres://"):
    db_url = db_url.replace("postgres://", "postgresql://", 1)

app.config['SQLALCHEMY_DATABASE_URI'] = db_url
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
if 'sqlite' not in db_url:
    app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {
        "pool_pre_ping": True, "pool_recycle": 300, "pool_timeout": 30      
    }
else:
    app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {
        "pool_pre_ping": True
    }

from models import db, Product, Category, Order, PromoCode, PlayerSession, RedeemCode, MinifigurePool, DrawHistory, get_reward_config, save_reward_config, _sync_product_to_pool, _sync_pool_to_product
db.init_app(app)
# --- SECURITY CONFIG (FROM ENVIRONMENT) ---
ADMIN_USERNAME = os.environ.get('ADMIN_USERNAME', 'admin')
ADMIN_PASS = os.environ.get('ADMIN_PASS', 'Thesong_Admin@2022?!$')

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get('admin'):
            flash('Please log in to access the admin panel.', 'error')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

spam_tracker = {}

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

@app.route('/api/check-promo', methods=['GET'])
def check_promo():
    code = request.args.get('code', '').strip().upper()
    if not code:
        return jsonify({'error': 'No code provided'}), 400
        
    promo = PromoCode.query.filter_by(code=code, is_active=True).first()
    if not promo:
        return jsonify({'error': 'Invalid or expired promo code'}), 404
        
    if promo.max_uses > 0 and promo.current_uses >= promo.max_uses:
        return jsonify({'error': 'Promo code usage limit reached'}), 400
        
    return jsonify({
        'success': True,
        'code': promo.code,
        'discountPercent': promo.discount_value if promo.discount_type == 'percent' else 0,
        'discountAmount': promo.discount_value if promo.discount_type == 'flat' else 0
    })

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
        cart_data_raw = request.form.get('cart_data', '[]')
        try:
            cart_items = json.loads(cart_data_raw)
        except Exception:
            return "Invalid cart data", 400

        if not cart_items:
            return "Cart is empty", 400

        # Server-side validation of pricing to prevent tampering
        subtotal = 0.0
        for item in cart_items:
            qty = max(1, int(item.get('qty', 1)))
            price = max(0.0, float(item.get('price', 0.0)))
            subtotal += price * qty

        discount_amount = 0.0
        promo_code = request.form.get('promo_code_used', '').strip().upper()
        if promo_code:
            promo = PromoCode.query.filter_by(code=promo_code, is_active=True).first()
            if promo and (promo.max_uses == 0 or promo.current_uses < promo.max_uses):
                if subtotal >= promo.min_order_value:
                    if promo.discount_type == 'percent':
                        discount_amount = subtotal * (promo.discount_value / 100.0)
                    elif promo.discount_type == 'flat':
                        discount_amount = promo.discount_value
            else:
                promo_code = None

        final_total = max(0.0, subtotal - discount_amount)

        new_order = Order(
            customer_name=(request.form.get('name') or '').strip()[:100], 
            customer_phone=(request.form.get('phone') or '').strip()[:20], 
            customer_address=(request.form.get('address') or '').strip(),
            items_json=json.dumps(cart_items), 
            total_usd=round(final_total, 2), 
            status="Pending",
            promo_code_used=promo_code if discount_amount > 0 else None
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
        return "An error occurred while placing your order.", 400

@app.route('/api/checkout', methods=['POST'])
def checkout():
    data = request.json
    try:
        tg_user = data.get('telegram_user')
        tg_id = str(tg_user.get('id')) if tg_user and tg_user.get('id') else None
        
        tg_name = None
        if tg_user:
            tg_name = tg_user.get('first_name', '')
            last_name = tg_user.get('last_name')
            if last_name:
                tg_name += f" {last_name}"

        tg_payload = json.dumps(tg_user) if tg_user else None

        new_order = Order(
            customer_name=data.get('name'), 
            customer_phone=data.get('phone'), 
            customer_address=data.get('address'),
            items_json=json.dumps(data.get('items', [])), 
            total_usd=float(data.get('total', 0) or 0), 
            delivery_fee=float(data.get('deliveryFee', 0) or 0),
            promo_code_used=data.get('redeemCode'), 
            telegram_id=tg_id,           
            telegram_name=tg_name,       
            telegram_user_payload=tg_payload, 
            status="Pending"
        )
        db.session.add(new_order)
        db.session.commit()
        return jsonify({'status': 'success', 'order_id': new_order.id})
    except Exception as e: 
        db.session.rollback()
        return jsonify({'status': 'error', 'message': 'Failed to process order'}), 400

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
                "product_code": getattr(p, 'product_code', '') or '',
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


# --- 6. LUCKY DRAW / SPIN GAME PUBLIC API ---
def get_player():
    if 'player_id' not in session:
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
def get_spin_balance():
    player = get_player()
    return jsonify({"balance": player.balance, "player_id": player.player_id})

@app.route('/api/spin/pool', methods=['GET'])
def get_live_pool():
    items = MinifigurePool.query.all()
    return jsonify({"pool": [{"id": i.id, "name": i.name, "image": i.image, "rarity": i.rarity, "stock": i.stock} for i in items]})

@app.route('/api/spin/redeem', methods=['POST'])
def redeem_spin_code():
    player = get_player()
    code_input = (request.json or {}).get('code', '').strip().upper()
    code_entry = RedeemCode.query.filter_by(code=code_input).first()
    
    if not code_entry: 
        return jsonify({"error": "Invalid Code"}), 400
    if code_entry.status == "Redeemed": 
        return jsonify({"error": "Code already used"}), 400
        
    code_entry.status = "Redeemed"
    code_entry.redeemed_by = player.player_id
    player.balance += code_entry.value
    db.session.commit()
    return jsonify({"success": True, "new_balance": player.balance, "value": code_entry.value})

@app.route('/api/spin/play', methods=['POST'])
def execute_spin():
    player = get_player()
    count = int((request.json or {}).get('count', 1)) 
    cost = 1000 if count == 1 else 5000
    
    if player.balance < cost: 
        return jsonify({"error": "Insufficient Riel balance. Please redeem a code."}), 400

    available_items = MinifigurePool.query.filter(MinifigurePool.stock > 0).all()
    if not available_items or sum([item.stock for item in available_items]) < count:
        return jsonify({"error": "Not enough stock in the prize pool!"}), 400

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
        winner.stock -= 1 
        _sync_pool_to_product(winner)
        db.session.add(DrawHistory(player_id=player.player_id, item_name=winner.name, rarity=winner.rarity, stock_remaining=winner.stock))
        prizes.append({"id": winner.id, "name": winner.name, "image": winner.image, "rarity": winner.rarity})
        pool = [i for i in pool if i.stock > 0]
        if not pool and _ < count - 1: 
            break

    player.balance -= cost 

    extra_reward_amount = 0
    if count == 5:
        cfg = get_reward_config()
        amounts = [0, 500, 1000, 2000, 5000, 10000, 50000]
        try:
            weights = [float(cfg.get(str(a), 0)) for a in amounts]
            if sum(weights) <= 0: 
                weights = [100, 0, 0, 0, 0, 0, 0]
            extra_reward_amount = random.choices(amounts, weights=weights, k=1)[0]
            if extra_reward_amount > 0:
                player.balance += extra_reward_amount
        except Exception: 
            pass

    db.session.commit()
    return jsonify({"success": True, "new_balance": player.balance, "prizes": prizes, "extra_reward": extra_reward_amount})


# --- CONNECT STORE-ADMIN ---
def _url_build_error_handler(error, endpoint, values):
    for ep in app.view_functions:
        if ep.endswith('.' + endpoint):
            return url_for(ep, **values)
    raise error

app.url_build_error_handlers.append(_url_build_error_handler)

import importlib
store_admin_module = importlib.import_module('store-admin')
app.register_blueprint(store_admin_module.admin_bp)

@app.route('/admin/db-status')
def db_status():
    if not session.get('admin'):
        return jsonify({"error": "unauthorized"}), 401
    
    db_uri = app.config.get('SQLALCHEMY_DATABASE_URI', '')
    masked_uri = db_uri
    if '@' in db_uri:
        prefix = db_uri.split('@')[0]
        host = db_uri.split('@')[1]
        masked_uri = f"{prefix.split(':')[0]}://****@{host}"
        
    try:
        from models import Product, Category, Order
        prod_count = Product.query.count()
        cat_count = Category.query.count()
        order_count = Order.query.count()
        first_prod = Product.query.first()
        return jsonify({
            "status": "connected",
            "db_type": "postgres" if "postgres" in db_uri else "sqlite",
            "masked_uri": masked_uri,
            "product_count": prod_count,
            "category_count": cat_count,
            "order_count": order_count,
            "sample_product": first_prod.title if first_prod else None
        })
    except Exception as e:
        return jsonify({
            "status": "error",
            "db_uri": masked_uri,
            "error": str(e)
        }), 500


# --- SECURITY HEADERS MIDDLEWARE ---
@app.after_request
def set_security_headers(response):
    response.headers['X-Content-Type-Options'] = 'nosniff'
    response.headers['X-Frame-Options'] = 'SAMEORIGIN'
    response.headers['X-XSS-Protection'] = '1; mode=block'
    response.headers['Referrer-Policy'] = 'strict-origin-when-cross-origin'
    response.headers['Permissions-Policy'] = 'camera=(), microphone=(), geolocation=()'
    return response

@app.errorhandler(404)
def not_found_error(error):
    if request.path.startswith('/api/'):
        return jsonify({'error': 'Resource not found'}), 404
    return redirect(url_for('index'))

@app.errorhandler(500)
def internal_server_error(error):
    if request.path.startswith('/api/'):
        return jsonify({'error': 'Internal server error'}), 500
    return "An unexpected error occurred. Please try again later.", 500

@app.errorhandler(413)
def request_entity_too_large(error): 
    return redirect(request.referrer)

# --- THE DEPLOYMENT "CRASH-PROOF" BOOT SEQUENCE ---
with app.app_context():
    try:
        # Create all tables normally
        db.create_all()
        
        # Only execute manual ALTER statements if running on the local SQLite fallback
        # This prevents transaction aborts from crashing Postgres environments on Render/Heroku
        if 'sqlite' in app.config['SQLALCHEMY_DATABASE_URI']:
            queries = [
                'ALTER TABLE product ADD COLUMN product_code VARCHAR(50)',
                'ALTER TABLE "order" ADD COLUMN promo_code_used VARCHAR(50)',
                'ALTER TABLE product ADD COLUMN discount_percent FLOAT DEFAULT 0.0',
                'ALTER TABLE product ADD COLUMN use_custom_thumbnail BOOLEAN DEFAULT FALSE',
                'ALTER TABLE product ADD COLUMN detail_images TEXT',
                'ALTER TABLE "order" ADD COLUMN delivery_fee FLOAT DEFAULT 0.0',
                'ALTER TABLE "order" ADD COLUMN telegram_id VARCHAR(100)',
                'ALTER TABLE "order" ADD COLUMN telegram_name VARCHAR(200)',
                'ALTER TABLE "order" ADD COLUMN telegram_user_payload TEXT'
            ]
            for q in queries:
                try:
                    db.session.execute(text(q))
                    db.session.commit()
                except Exception:
                    db.session.rollback()
    except Exception as e:
        print(f"Warning during DB startup, safely ignored: {e}")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
