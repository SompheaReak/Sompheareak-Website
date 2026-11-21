import os
import re
import json
import time
import random
import string
import uuid
from datetime import datetime, timedelta
from functools import wraps
from urllib.parse import urlparse, urljoin
from flask import Flask, render_template, request, redirect, url_for, jsonify, session, flash, render_template_string, Response
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import text
from sqlalchemy.exc import IntegrityError
from werkzeug.security import generate_password_hash, check_password_hash
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

# --- 1. UPLOAD HANDLING (CLOUDINARY WITH LOCAL STORAGE FALLBACK) ---
from uploader import optimize_and_upload

# --- 2. PERMANENT DATABASE CONFIG ---
DEFAULT_NEON_DB = "postgresql://neondb_owner:npg_dq6KIUVe0cyS@ep-polished-feather-a19qzv4s-pooler.ap-southeast-1.aws.neon.tech/neondb?sslmode=require"
db_url = os.environ.get('DATABASE_URL', '').strip()
if not db_url or 'fallback.db' in db_url:
    db_url = DEFAULT_NEON_DB

if db_url.startswith("postgres://"):
    db_url = db_url.replace("postgres://", "postgresql://", 1)

# Clean channel_binding parameter as it causes libpq/SCRAM failures in certain deployment environments
db_url = db_url.replace("&channel_binding=require", "").replace("?channel_binding=require&", "?").replace("?channel_binding=require", "")

app.config['SQLALCHEMY_DATABASE_URI'] = db_url
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 604800  # Cache static assets for 7 days
if 'sqlite' not in db_url:
    app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {
        "pool_pre_ping": True,
        "pool_recycle": 300,
        "pool_timeout": 15,
        "pool_size": 10,
        "max_overflow": 20
    }
else:
    app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {
        "pool_pre_ping": True
    }

from models import (
    db, Product, Category, Order, PromoCode, PlayerSession, RedeemCode,
    MinifigurePool, DrawHistory, CustomerUser, CreditTransaction, SystemSetting,
    get_reward_config, save_reward_config, _sync_product_to_pool, _sync_pool_to_product
)
db.init_app(app)

def customer_login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get('customer_id'):
            flash('Please log in to your account.', 'info')
            return redirect(url_for('customer_login', next=request.url))
        return f(*args, **kwargs)
    return decorated_function

spam_tracker = {}
rate_limit_trackers = {
    'forgot_password': {},
    'customer_login': {},
    'customer_register': {},
    'orders': {},
    'otp_verify': {}
}

# Constant-time dummy password hash to prevent timing attacks & account enumeration
DUMMY_PASSWORD_HASH = generate_password_hash("dummy_protection_hash_against_timing_attacks")

def is_safe_redirect_url(target):
    if not target or not isinstance(target, str):
        return False
    target = target.strip()
    if target.startswith('//') or target.startswith('\\\\'):
        return False
    ref_url = urlparse(request.host_url)
    test_url = urlparse(urljoin(request.host_url, target))
    return (
        test_url.scheme in ('http', 'https') and
        ref_url.netloc == test_url.netloc
    )

def get_client_ip():
    forwarded = request.headers.get('X-Forwarded-For')
    if forwarded:
        return forwarded.split(',')[0].strip()
    return request.remote_addr or '127.0.0.1'

def check_rate_limit(tracker_name, key, max_requests, window_seconds):
    tracker = rate_limit_trackers.setdefault(tracker_name, {})
    now = time.time()
    timestamps = [ts for ts in tracker.get(key, []) if now - ts < window_seconds]
    if len(timestamps) >= max_requests:
        tracker[key] = timestamps
        retry_after = max(1, int(window_seconds - (now - timestamps[0])))
        return False, retry_after
    timestamps.append(now)
    tracker[key] = timestamps
    return True, 0

@app.context_processor
def inject_global_data():
    data = {}
    cust_id = session.get('customer_id')
    if cust_id:
        try:
            data['current_customer'] = CustomerUser.query.get(cust_id)
        except Exception:
            data['current_customer'] = None
    else:
        data['current_customer'] = None
    return data

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

def normalize_phone(phone_str):
    if not phone_str:
        return ''
    cleaned = re.sub(r'[\s\-\(\)\.]+', '', str(phone_str).strip())
    if cleaned.startswith('+855'):
        cleaned = '0' + cleaned[4:]
    elif cleaned.startswith('855') and len(cleaned) >= 11:
        cleaned = '0' + cleaned[3:]
    return cleaned

# --- CUSTOMER ACCOUNT & AUTH ROUTES ---
@app.route('/customer/register', methods=['GET', 'POST'])
def customer_register():
    if request.method == 'POST':
        client_ip = get_client_ip()
        allowed, retry_after = check_rate_limit('customer_register', client_ip, max_requests=5, window_seconds=600)
        if not allowed:
            if request.is_json:
                return jsonify({'error': f'Too many registration attempts. Please wait {retry_after} seconds.'}), 429
            flash(f'Too many registration attempts. Please wait {retry_after} seconds.', 'error')
            return redirect(url_for('customer_register'))

        data = request.get_json(silent=True) or request.form
        full_name = (data.get('full_name') or '').strip()[:100]
        raw_phone = (data.get('phone') or '').strip()
        telegram = (data.get('telegram') or '').strip()[:100]
        phone = normalize_phone(raw_phone)
        password = (data.get('password') or '').strip()

        if not full_name:
            if request.is_json:
                return jsonify({'error': 'User name is required.'}), 400
            flash('User name is required.', 'error')
            return redirect(url_for('customer_register'))

        if not phone or not password:
            if request.is_json:
                return jsonify({'error': 'Phone number and password are required.'}), 400
            flash('Phone number and password are required.', 'error')
            return redirect(url_for('customer_register'))

        if not telegram:
            if request.is_json:
                return jsonify({'error': 'Telegram number or @username is required.'}), 400
            flash('Telegram number or @username is required.', 'error')
            return redirect(url_for('customer_register'))

        if len(phone) < 8 or len(phone) > 15 or not re.match(r'^\+?[0-9]+$', phone):
            if request.is_json:
                return jsonify({'error': 'Please enter a valid phone number (at least 8 digits).'}), 400
            flash('Please enter a valid phone number (at least 8 digits).', 'error')
            return redirect(url_for('customer_register'))

        if len(password) < 6:
            if request.is_json:
                return jsonify({'error': 'Password must be at least 6 characters long.'}), 400
            flash('Password must be at least 6 characters long.', 'error')
            return redirect(url_for('customer_register'))

        if len(password) > 100:
            if request.is_json:
                return jsonify({'error': 'Password is too long (maximum 100 characters).'}), 400
            flash('Password is too long (maximum 100 characters).', 'error')
            return redirect(url_for('customer_register'))

        existing = CustomerUser.query.filter(
            db.or_(
                CustomerUser.phone == phone,
                CustomerUser.phone == raw_phone
            )
        ).first()
        if existing:
            if request.is_json:
                return jsonify({'error': 'This phone number is already registered. Please login.'}), 409
            flash('This phone number is already registered. Please login.', 'error')
            return redirect(url_for('customer_login'))

        user = CustomerUser(phone=phone, full_name=full_name, telegram=telegram)
        user.set_password(password)
        try:
            db.session.add(user)
            db.session.commit()
        except IntegrityError:
            db.session.rollback()
            if request.is_json:
                return jsonify({'error': 'This phone number is already registered. Please login.'}), 409
            flash('This phone number is already registered. Please login.', 'error')
            return redirect(url_for('customer_login'))

        # Regenerate session on registration to prevent session fixation
        session.clear()
        session['customer_id'] = user.id
        session['customer_phone'] = user.phone
        if request.is_json:
            return jsonify({'success': True, 'customer': user.to_dict()})
        flash('Account created successfully! Welcome to Somphea Reak.', 'success')
        next_url = request.args.get('next')
        if not is_safe_redirect_url(next_url):
            next_url = url_for('customer_account')
        return redirect(next_url)

    return render_template('customer/login.html', mode='register')

@app.route('/customer/login', methods=['GET', 'POST'])
def customer_login():
    if request.method == 'POST':
        client_ip = get_client_ip()
        login_fails = rate_limit_trackers.setdefault('customer_login', {})
        now = time.time()
        fail_times = [ts for ts in login_fails.get(client_ip, []) if now - ts < 600]
        if len(fail_times) >= 10:
            wait_sec = max(1, int(600 - (now - fail_times[0])))
            if request.is_json:
                return jsonify({'error': f'Too many failed login attempts. Please try again in {wait_sec} seconds.'}), 429
            flash('Too many failed login attempts. Please try again in 10 minutes.', 'error')
            return redirect(url_for('customer_login'))

        data = request.get_json(silent=True) or request.form
        login_id = (data.get('phone') or data.get('login_id') or '').strip()
        phone = normalize_phone(login_id)
        password = (data.get('password') or '').strip()

        user = CustomerUser.query.filter(
            db.or_(
                CustomerUser.phone == phone,
                CustomerUser.phone == login_id,
                CustomerUser.telegram == login_id,
                CustomerUser.full_name == login_id
            )
        ).first()

        # Constant-time password check: Always run check_password to eliminate timing attacks & account enumeration
        password_correct = user.check_password(password) if user else check_password_hash(DUMMY_PASSWORD_HASH, password)

        if not user or not password_correct:
            fail_times.append(now)
            login_fails[client_ip] = fail_times
            if request.is_json:
                return jsonify({'error': 'Invalid login credentials or password.'}), 401
            flash('Invalid login credentials or password.', 'error')
            return redirect(url_for('customer_login'))

        # Reset failed attempts on success
        login_fails.pop(client_ip, None)

        # Regenerate session on authentication to prevent session fixation
        session.clear()
        session['customer_id'] = user.id
        session['customer_phone'] = user.phone
        if request.is_json:
            return jsonify({'success': True, 'customer': user.to_dict()})
        flash(f'Welcome back, {user.full_name or user.phone}!', 'success')
        next_url = request.args.get('next')
        if not is_safe_redirect_url(next_url):
            next_url = url_for('customer_account')
        return redirect(next_url)

    return render_template('customer/login.html', mode='login')

@app.route('/customer/logout')
def customer_logout():
    session.clear()
    flash('You have been logged out.', 'info')
    return redirect(url_for('index'))

# --- PASSWORD RECOVERY VIA ADMIN TELEGRAM ALERT ---
@app.route('/customer/forgot-password', methods=['GET', 'POST'])
def customer_forgot_password():
    if request.method == 'POST':
        client_ip = get_client_ip()
        allowed, retry_after = check_rate_limit('forgot_password', client_ip, max_requests=5, window_seconds=300)
        if not allowed:
            if request.is_json:
                return jsonify({'error': f'Too many recovery requests. Please try again in {retry_after} seconds.'}), 429
            flash('Too many password recovery requests. Please try again in 5 minutes.', 'error')
            return redirect(url_for('customer_forgot_password'))

        data = request.get_json(silent=True) or request.form
        raw_phone = (data.get('phone') or '').strip()
        note = (data.get('note') or '').strip()[:200]
        phone = normalize_phone(raw_phone)

        if not phone:
            if request.is_json:
                return jsonify({'error': 'Please enter your registered phone number.'}), 400
            flash('Please enter your registered phone number.', 'error')
            return redirect(url_for('customer_forgot_password'))

        user = CustomerUser.query.filter(
            db.or_(CustomerUser.phone == phone, CustomerUser.phone == raw_phone)
        ).first()

        # Mask phone to prevent PII exposure (e.g. 012***78)
        masked_phone = (phone[:3] + '***' + phone[-2:]) if len(phone) >= 5 else phone

        if user:
            # Dispatch real-time alert to Admin Telegram Bot
            try:
                from telegram_notifier import send_telegram_recovery_alert
                send_telegram_recovery_alert(user, note=note)
            except Exception as e:
                print(f"Warning sending telegram recovery alert: {e}")

        # Uniform response to completely eliminate user enumeration (CWE-204)
        if request.is_json:
            return jsonify({
                'success': True,
                'message': 'If an account exists for this phone number, a recovery request has been sent to admin.',
                'phone': masked_phone
            })

        flash(f'If an account exists for {masked_phone}, an alert was sent to Admin. Admin will verify and assist you.', 'success')
        return render_template('customer/forgot_password.html', submitted=True, masked_phone=masked_phone)

    return render_template('customer/forgot_password.html', submitted=False)

@app.route('/customer/reset-password', methods=['GET', 'POST'])
def customer_reset_password():
    prefill_phone = session.get('reset_phone', '')
    if request.method == 'POST':
        client_ip = get_client_ip()
        allowed, retry_after = check_rate_limit('otp_verify', client_ip, max_requests=5, window_seconds=300)
        if not allowed:
            if request.is_json:
                return jsonify({'error': f'Too many verification attempts. Please wait {retry_after} seconds.'}), 429
            flash(f'Too many verification attempts. Please try again in 5 minutes.', 'error')
            return render_template('customer/reset_password.html', phone=prefill_phone)

        data = request.get_json(silent=True) or request.form
        raw_phone = (data.get('phone') or prefill_phone or '').strip()
        phone = normalize_phone(raw_phone)
        otp = (data.get('otp') or '').strip()
        new_password = (data.get('new_password') or '').strip()
        confirm_password = (data.get('confirm_password') or '').strip()

        if not phone or not otp or not new_password:
            if request.is_json:
                return jsonify({'error': 'Phone, OTP code, and new password are required.'}), 400
            flash('Phone, OTP code, and new password are required.', 'error')
            return render_template('customer/reset_password.html', phone=phone)

        if new_password != confirm_password:
            if request.is_json:
                return jsonify({'error': 'Passwords do not match.'}), 400
            flash('Passwords do not match.', 'error')
            return render_template('customer/reset_password.html', phone=phone)

        if len(new_password) < 6:
            if request.is_json:
                return jsonify({'error': 'Password must be at least 6 characters long.'}), 400
            flash('Password must be at least 6 characters long.', 'error')
            return render_template('customer/reset_password.html', phone=phone)

        user = CustomerUser.query.filter(
            db.or_(CustomerUser.phone == phone, CustomerUser.phone == raw_phone)
        ).first()

        if not user or not user.reset_otp:
            if request.is_json:
                return jsonify({'error': 'Invalid request or no active reset code found.'}), 400
            flash('Invalid request or no active reset code found. Please request a new code.', 'error')
            return redirect(url_for('customer_forgot_password'))

        # Check expiration
        now_utc = datetime.utcnow()
        if not user.reset_otp_expires_at or user.reset_otp_expires_at < now_utc:
            if request.is_json:
                return jsonify({'error': 'Recovery code has expired. Please request a new one.'}), 400
            flash('Recovery code has expired. Please request a new code.', 'error')
            return redirect(url_for('customer_forgot_password'))

        # Check OTP match
        if str(user.reset_otp).strip() != otp:
            if request.is_json:
                return jsonify({'error': 'Incorrect verification code. Please try again.'}), 400
            flash('Incorrect verification code. Please check your SMS and try again.', 'error')
            return render_template('customer/reset_password.html', phone=phone)

        # Success - update password and clear OTP
        user.set_password(new_password)
        user.reset_otp = None
        user.reset_otp_expires_at = None
        db.session.commit()

        session.clear()

        if request.is_json:
            return jsonify({'success': True, 'message': 'Password reset successful!'})

        flash('Your password has been reset successfully! Please sign in with your new password.', 'success')
        return redirect(url_for('customer_login'))

    return render_template('customer/reset_password.html', phone=prefill_phone)

@app.route('/customer/account')
@customer_login_required
def customer_account():
    user = CustomerUser.query.get(session['customer_id'])
    if not user:
        session.clear()
        return redirect(url_for('customer_login'))

    credit_rules = SystemSetting.get_val('credit_rules', {
        "points_per_usd": 10,
        "points_per_voucher_dollar": 20,
        "min_redeem_points": 100
    })

    # Scope vouchers strictly to the logged-in customer's own redeemed voucher codes (IDOR protection)
    user_txs = CreditTransaction.query.filter_by(user_id=user.id).all()
    user_voucher_codes = []
    for tx in user_txs:
        if tx.description and 'Code: CRD-' in tx.description:
            match = re.search(r'Code:\s*(CRD-[A-Z0-9]+)', tx.description)
            if match:
                user_voucher_codes.append(match.group(1))

    vouchers = []
    if user_voucher_codes:
        vouchers = PromoCode.query.filter(
            PromoCode.code.in_(user_voucher_codes),
            PromoCode.is_active == True,
            (PromoCode.max_uses == 0) | (PromoCode.current_uses < PromoCode.max_uses)
        ).order_by(PromoCode.timestamp.desc()).all()

    return render_template('customer/account.html', user=user, credit_rules=credit_rules, vouchers=vouchers)

@app.route('/customer/redeem-voucher', methods=['POST'])
@customer_login_required
def customer_redeem_voucher():
    user = CustomerUser.query.get(session['customer_id'])
    if not user:
        return redirect(url_for('customer_login'))

    try:
        points = int(request.form.get('points', 0))
    except (ValueError, TypeError):
        points = 0

    credit_rules = SystemSetting.get_val('credit_rules', {
        "points_per_usd": 10,
        "points_per_voucher_dollar": 20,
        "min_redeem_points": 100
    })

    min_points = credit_rules.get('min_redeem_points', 100)
    pts_per_dollar = max(1, credit_rules.get('points_per_voucher_dollar', 20))

    if points < min_points:
        flash(f'Minimum {min_points} credit points required to redeem a voucher.', 'error')
        return redirect(url_for('customer_account'))

    if user.credit_balance < points:
        flash('You do not have enough credit points.', 'error')
        return redirect(url_for('customer_account'))

    voucher_value = round(points / pts_per_dollar, 2)
    voucher_code = f"CRD-{uuid.uuid4().hex[:6].upper()}"

    new_promo = PromoCode(
        code=voucher_code,
        discount_type='flat',
        discount_value=voucher_value,
        min_order_value=0.0,
        max_uses=1,
        current_uses=0,
        is_active=True
    )
    user.credit_balance -= points
    tx = CreditTransaction(
        user_id=user.id,
        amount=-points,
        description=f"Redeemed for ${voucher_value:.2f} Voucher (Code: {voucher_code})"
    )
    db.session.add(new_promo)
    db.session.add(tx)
    db.session.commit()

    flash(f'Voucher created! Code: {voucher_code} for ${voucher_value:.2f} discount.', 'success')
    return redirect(url_for('customer_account'))

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

def _handle_order_post_processing(order):
    """
    1. Awards credit points ONLY if customer is logged in to their account.
       Strict rule: No logged-in account = No credit (guests cannot earn credit).
    2. Sends real-time Telegram order alert.
    """
    try:
        cust_id = session.get('customer_id')
        user = CustomerUser.query.get(cust_id) if cust_id else None

        # STRICT RULE: No logged-in account = No credit. Guests cannot earn credit points.
        if user:
            credit_rules = SystemSetting.get_val('credit_rules', {"points_per_usd": 10})
            pts_per_usd = max(0, int(credit_rules.get('points_per_usd', 10)))
            earned = int(float(order.total_usd or 0.0) * pts_per_usd)
            if earned > 0:
                user.credit_balance = (user.credit_balance or 0) + earned
                tx = CreditTransaction(
                    user_id=user.id,
                    amount=earned,
                    description=f"Earned from Order #{order.id} (${order.total_usd:.2f})"
                )
                db.session.add(tx)
                db.session.commit()
    except Exception as e:
        print(f"Credit award error: {e}")

    try:
        from telegram_notifier import send_telegram_order_alert
        send_telegram_order_alert(order)
    except Exception as e:
        print(f"Telegram alert error: {e}")

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

        # Server-side validation of pricing from database to prevent price tampering
        subtotal = 0.0
        for item in cart_items:
            qty = max(1, int(item.get('qty', 1)))
            raw_id = str(item.get('id') or item.get('variantId') or item.get('cartId') or '').strip()
            p_id = None
            v_id = -1
            if '-' in raw_id:
                parts = raw_id.split('-')
                if parts[0].isdigit():
                    p_id = int(parts[0])
                if len(parts) >= 2 and parts[1].isdigit():
                    v_id = int(parts[1])
            elif raw_id.isdigit():
                p_id = int(raw_id)
            
            p = None
            if p_id:
                item['id'] = p_id
                p = Product.query.get(p_id)
            elif item.get('title'):
                raw_title = str(item.get('title')).split(' - ')[0].strip().lower()
                p = Product.query.filter(Product.title.ilike(raw_title)).first()
                if p:
                    item['id'] = p.id
            
            item_price = 0.0
            if p:
                item_price = float(p.price or 0.0)
                if p.variants and v_id != -1:
                    try:
                        variants = json.loads(p.variants)
                        for v in variants:
                            if v.get('id') == v_id and 'price' in v and v.get('price') is not None:
                                item_price = float(v.get('price'))
                                break
                    except Exception:
                        pass
                if getattr(p, 'cost_price', None) is not None:
                    item['cost_price'] = float(p.cost_price or 0.0)
            else:
                item_price = max(0.0, float(item.get('price', 0.0)))

            item['price'] = item_price
            subtotal += item_price * qty

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
                    promo.current_uses += 1
                else:
                    promo_code = None
            else:
                promo_code = None
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

        # Handle post-order credit rewards & Telegram alert
        _handle_order_post_processing(new_order)
        
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
    client_ip = get_client_ip()
    allowed, retry_after = check_rate_limit('orders', client_ip, max_requests=10, window_seconds=60)
    if not allowed:
        return jsonify({'status': 'error', 'message': f'Too many orders placed from this IP. Please wait {retry_after} seconds.'}), 429

    data = request.json or {}
    try:
        raw_name = (data.get('name') or '').strip()
        raw_phone = (data.get('phone') or '').strip()
        raw_telegram = (data.get('telegram') or '').strip()
        raw_address = (data.get('address') or '').strip()
        phone_digits = re.sub(r'[^0-9]', '', raw_phone)

        if not raw_name:
            return jsonify({'status': 'error', 'message': 'Customer name is required.'}), 400
        if not raw_phone or len(phone_digits) < 8:
            return jsonify({'status': 'error', 'message': 'Valid phone number with at least 8 digits is required.'}), 400
        if not raw_telegram:
            return jsonify({'status': 'error', 'message': 'Telegram contact (@username or phone) is required.'}), 400
        if not raw_address:
            return jsonify({'status': 'error', 'message': 'Delivery address is required.'}), 400

        tg_user = data.get('telegram_user')
        tg_id = str(tg_user.get('id')) if tg_user and tg_user.get('id') else None
        
        tg_name = None
        if tg_user:
            tg_name = tg_user.get('first_name', '')
            last_name = tg_user.get('last_name')
            if last_name:
                tg_name += f" {last_name}"
        if not tg_name and raw_telegram:
            tg_name = raw_telegram

        tg_payload = json.dumps(tg_user) if tg_user else None

        items = data.get('items', [])
        if not items:
            return jsonify({'status': 'error', 'message': 'Cart is empty'}), 400

        subtotal = 0.0
        for item in items:
            qty = max(1, int(item.get('qty', 1)))
            raw_id = str(item.get('id') or item.get('variantId') or item.get('cartId') or '').strip()
            p_id = None
            v_id = -1
            if '-' in raw_id:
                parts = raw_id.split('-')
                if parts[0].isdigit():
                    p_id = int(parts[0])
                if len(parts) >= 2 and parts[1].isdigit():
                    v_id = int(parts[1])
            elif raw_id.isdigit():
                p_id = int(raw_id)
            
            p = None
            if p_id:
                item['id'] = p_id
                p = Product.query.get(p_id)
            elif item.get('title'):
                raw_title = str(item.get('title')).split(' - ')[0].strip().lower()
                p = Product.query.filter(Product.title.ilike(raw_title)).first()
                if p:
                    item['id'] = p.id

            item_price = 0.0
            if p:
                item_price = float(p.price or 0.0)
                if p.variants and v_id != -1:
                    try:
                        variants = json.loads(p.variants)
                        for v in variants:
                            if v.get('id') == v_id and 'price' in v and v.get('price') is not None:
                                item_price = float(v.get('price'))
                                break
                    except Exception:
                        pass
                if getattr(p, 'cost_price', None) is not None:
                    item['cost_price'] = float(p.cost_price or 0.0)
            else:
                item_price = max(0.0, float(item.get('price', 0.0)))

            item['price'] = item_price
            subtotal += item_price * qty

        discount_amount = 0.0
        promo_code = (data.get('redeemCode') or '').strip().upper()
        if promo_code:
            promo = PromoCode.query.filter_by(code=promo_code, is_active=True).first()
            if promo and (promo.max_uses == 0 or promo.current_uses < promo.max_uses):
                if subtotal >= promo.min_order_value:
                    if promo.discount_type == 'percent':
                        discount_amount = subtotal * (promo.discount_value / 100.0)
                    elif promo.discount_type == 'flat':
                        discount_amount = promo.discount_value
                    promo.current_uses += 1
                else:
                    promo_code = None
            else:
                promo_code = None
        else:
            promo_code = None

        delivery_fee = max(0.0, float(data.get('deliveryFee', 0) or 0))
        computed_total = round(max(0.0, subtotal - discount_amount) + delivery_fee, 2)

        new_order = Order(
            customer_name=raw_name[:100], 
            customer_phone=raw_phone[:20], 
            customer_address=raw_address,
            items_json=json.dumps(items), 
            total_usd=computed_total, 
            delivery_fee=delivery_fee,
            promo_code_used=promo_code if discount_amount > 0 else None, 
            telegram_id=tg_id,           
            telegram_name=tg_name[:200] if tg_name else None,       
            telegram_user_payload=tg_payload, 
            status="Pending"
        )
        db.session.add(new_order)
        db.session.commit()
        _handle_order_post_processing(new_order)
        _catalog_cache.clear()
        return jsonify({'status': 'success', 'order_id': new_order.id, 'total': computed_total})
    except Exception as e: 
        db.session.rollback()
        return jsonify({'status': 'error', 'message': 'Failed to process order'}), 400

_catalog_cache = {}
CATALOG_CACHE_TTL = 30  # seconds

@app.route('/api/products/<store_name>')
def get_api(store_name):
    now = time.time()
    include_charms = request.args.get('include_charms', '0') == '1'
    cache_key = f"{store_name}_{int(include_charms)}"
    cached = _catalog_cache.get(cache_key)
    if cached and (now - cached['time'] < CATALOG_CACHE_TTL):
        resp = jsonify(cached['data'])
        resp.headers['Cache-Control'] = 'public, max-age=15, stale-while-revalidate=60'
        return resp

    try:
        if store_name == 'all':
            query = Product.query.filter(Product.is_visible == True)
            if not include_charms:
                query = query.filter(
                    ~Product.store.ilike('%custom_bracelet%'),
                    ~Product.category.ilike('%charm%'),
                    ~Product.title.ilike('charm %')
                )
            matching_prods = query.order_by(Product.sort_order.asc(), Product.id.desc()).all()
        else:
            # Filter matching store directly in database for fast response
            matching_prods = Product.query.filter(
                Product.is_visible == True,
                Product.store.ilike(f"%{store_name}%")
            ).order_by(Product.sort_order.asc(), Product.id.desc()).all()
        
        product_list = []
        for p in matching_prods:
            if store_name != 'all':
                stores = [s.strip() for s in (p.store or '').split(',') if s.strip()]
                if store_name not in stores:
                    continue
            
            v_list = []
            try:
                if p.variants: 
                    v_list = json.loads(p.variants)
            except Exception:
                pass
            
            d_list = []
            try:
                if getattr(p, 'detail_images', None): 
                    d_list = json.loads(p.detail_images)
            except Exception:
                pass
            
            product_list.append({
                "id": p.id,
                "product_code": getattr(p, 'product_code', '') or '',
                "title": p.title,
                "price": p.price,
                "stock": p.stock,
                "category": p.category, 
                "store": p.store or '',
                "thumbnail": p.image,
                "discount_percent": getattr(p, 'discount_percent', 0.0) or 0.0,
                "use_custom_thumbnail": getattr(p, 'use_custom_thumbnail', False) or False,
                "detail_images": d_list,
                "variants": v_list
            })
            
        categories = Category.query.order_by(Category.sort_order.asc()).all()
        res_data = {
            "products": product_list,
            "categories": [{"name": c.name, "image": c.image} for c in categories]
        }
        _catalog_cache[cache_key] = {'time': now, 'data': res_data}
        resp = jsonify(res_data)
        resp.headers['Cache-Control'] = 'public, max-age=15, stale-while-revalidate=60'
        return resp
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


# --- ADMIN REDIRECT ROUTE ---
@app.route('/admin')
@app.route('/admin/<path:subpath>')
def admin_redirect(subpath=''):
    admin_base = os.environ.get('ADMIN_PANEL_URL', 'https://store-admin-5uew.onrender.com').rstrip('/')
    target = f"{admin_base}/admin/{subpath}".rstrip('/') if subpath else f"{admin_base}/admin/login"
    return redirect(target)


# --- SEO & CRAWLER DIRECTIVES ---
@app.route('/robots.txt')
def robots_txt():
    content = "User-agent: *\nAllow: /\nDisallow: /customer/\nDisallow: /api/\n"
    return Response(content, mimetype="text/plain")

# --- SECURITY HEADERS MIDDLEWARE ---
@app.after_request
def set_security_headers(response):
    response.headers['X-Content-Type-Options'] = 'nosniff'
    response.headers['X-Frame-Options'] = 'SAMEORIGIN'
    response.headers['X-XSS-Protection'] = '1; mode=block'
    response.headers['Referrer-Policy'] = 'strict-origin-when-cross-origin'
    response.headers['Permissions-Policy'] = 'camera=(), microphone=(), geolocation=()'
    response.headers['Strict-Transport-Security'] = 'max-age=31536000; includeSubDomains'
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
                'ALTER TABLE product ADD COLUMN cost_price FLOAT DEFAULT 0.0',
                'ALTER TABLE product ADD COLUMN detail_images TEXT',
                'ALTER TABLE "order" ADD COLUMN delivery_fee FLOAT DEFAULT 0.0',
                'ALTER TABLE "order" ADD COLUMN telegram_id VARCHAR(100)',
                'ALTER TABLE "order" ADD COLUMN telegram_name VARCHAR(200)',
                'ALTER TABLE "order" ADD COLUMN telegram_user_payload TEXT',
                'ALTER TABLE customer_user ADD COLUMN reset_otp VARCHAR(10)',
                'ALTER TABLE customer_user ADD COLUMN reset_otp_expires_at DATETIME'
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
    port = int(os.environ.get("PORT", 5001))
    print(f"🚀 Starting Somphea Reak Test Store on http://127.0.0.1:{port}")
    app.run(host="0.0.0.0", port=port, debug=True)

