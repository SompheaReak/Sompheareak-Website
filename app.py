import os
import requests
from flask import Flask, render_template, request, redirect, url_for, jsonify, session, abort
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.secret_key = 'somphea_reak_shop_secret_key_2024'

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

# --- DATABASE MODEL ---
class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name_kh = db.Column(db.String(200), nullable=False)
    name_en = db.Column(db.String(200))
    price = db.Column(db.Integer, nullable=False)
    image = db.Column(db.String(500), nullable=False)
    categories_str = db.Column(db.String(500), default="") 
    subcategory_str = db.Column(db.String(500), default="") 
    stock = db.Column(db.Integer, default=1)

# --- TELEGRAM NOTIFY ---
def notify_telegram(ip, user_agent, event_type="Visitor"):
    message = f"📦 *{event_type} Notification*\n*IP:* `{ip}`\n*Device:* `{user_agent}`"
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    try:
        requests.post(url, data={"chat_id": CHAT_ID, "text": message, "parse_mode": "Markdown"})
    except:
        pass

@app.before_request
def security_check():
    # Basic IP filter
    banned_ips = ['123.45.67.89', '45.119.135.70']
    ip = request.headers.get('X-Forwarded-For', request.remote_addr).split(',')[0].strip()
    if ip in banned_ips:
        abort(403)
    if not session.get('notified') and not request.path.startswith('/static'):
        notify_telegram(ip, request.headers.get('User-Agent'))
        session['notified'] = True

# --- STORE ROUTES ---

@app.route('/')
def home():
    return redirect(url_for('category', category_name='Hot Sale'))

@app.route('/category/<category_name>')
def category(category_name):
    # Handle specific redirect pages
    if category_name == 'Italy Bracelet': return redirect(url_for('custom_bracelet'))
    if category_name == 'Lucky Draw': return redirect(url_for('lucky_draw'))
    
    products = Product.query.filter(Product.categories_str.contains(category_name)).all()
    return render_template('home.html', products=products, current_category=category_name)

@app.route('/custom-bracelet')
def custom_bracelet():
    charms = Product.query.filter(Product.categories_str.contains('Italy Bracelet')).all()
    return render_template('custom_bracelet.html', charms=charms)

# --- ADMIN DASHBOARD ---

@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        if request.form['username'] == ADMIN_USERNAME and request.form['password'] == ADMIN_PASSWORD:
            session['admin'] = True
            return redirect(url_for('admin_panel'))
        return render_template('admin_login.html', error="Incorrect Admin Login")
    return render_template('admin_login.html')

@app.route('/admin/panel')
def admin_panel():
    if not session.get('admin'):
        return redirect(url_for('admin_login'))
    
    all_products = Product.query.all()
    
    # Calculate stats for the dashboard boxes
    stats = {
        "total_items": len(all_products),
        "out_of_stock": len([p for p in all_products if p.stock <= 0]),
        "low_stock": len([p for p in all_products if 0 < p.stock <= 5]),
        "total_value": sum([p.price * p.stock for p in all_products if p.stock > 0])
    }
    
    # Group items by subcategory string
    grouped_data = {}
    for p in all_products:
        cat = p.subcategory_str if p.subcategory_str else "Uncategorized"
        if cat not in grouped_data: grouped_data[cat] = []
        grouped_data[cat].append(p)
        
    return render_template('admin_panel.html', grouped=grouped_data, stats=stats)

@app.route('/admin/api/update-stock', methods=['POST'])
def update_stock():
    if not session.get('admin'): return jsonify({"success": False}), 403
    data = request.json
    product = Product.query.get(data.get('id'))
    if product:
        product.stock = int(data.get('amount'))
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
            categories_str=request.form.get('categories', ''),
            subcategory_str=request.form.get('subcategory', ''),
            stock=int(request.form.get('stock', 1))
        )
        db.session.add(new_p)
        db.session.commit()
        return redirect(url_for('admin_panel'))
    return render_template('add_product.html')

@app.route('/admin/logout')
def admin_logout():
    session.pop('admin', None)
    return redirect(url_for('admin_login'))

@app.errorhandler(403)
def forbidden(e):
    return "Access Denied: Your IP is blocked.", 403

# --- INIT ---
with app.app_context():
    db.create_all()

if __name__ == '__main__':
    app.run(debug=True, port=5000)

