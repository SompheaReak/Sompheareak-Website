import os
import requests
from flask import Flask, render_template, request, redirect, url_for, jsonify, session, abort
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.secret_key = 'somphea_reak_shop_ultra_secret_2024'

# --- DATABASE SETUP ---
# This creates shop.db in the same folder as app.py
basedir = os.path.abspath(os.path.dirname(__file__))
db_path = os.path.join(basedir, 'shop.db')
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + db_path
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
    stock = db.Column(db.Integer, default=1) # THIS IS THE STOCK CONTROL FIELD

# --- TELEGRAM NOTIFICATIONS ---
def notify_telegram(ip, user_agent, event_type="Visitor"):
    message = f"📦 *{event_type} Notification*\n*IP:* `{ip}`\n*Device:* `{user_agent}`"
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    try: requests.post(url, data={"chat_id": CHAT_ID, "text": message, "parse_mode": "Markdown"})
    except: pass

@app.before_request
def security_check():
    if not session.get('notified') and not request.path.startswith('/static'):
        ip = request.headers.get('X-Forwarded-For', request.remote_addr).split(',')[0].strip()
        notify_telegram(ip, request.headers.get('User-Agent'))
        session['notified'] = True

# --- STOREFRONT ROUTES ---
@app.route('/')
def home():
    return redirect(url_for('category', category_name='Hot Sale'))

@app.route('/category/<category_name>')
def category(category_name):
    if category_name == 'Italy Bracelet': return redirect(url_for('custom_bracelet'))
    products = Product.query.filter(Product.categories_str.contains(category_name)).all()
    return render_template('home.html', products=products, current_category=category_name)

@app.route('/custom-bracelet')
def custom_bracelet():
    charms = Product.query.filter(Product.categories_str.contains('Italy Bracelet')).all()
    return render_template('custom_bracelet.html', charms=charms)

# --- ADMIN COMMAND CENTER ---
@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        if request.form['username'] == ADMIN_USERNAME and request.form['password'] == ADMIN_PASSWORD:
            session['admin'] = True
            return redirect(url_for('admin_panel'))
        return render_template('admin_login.html', error="Invalid Login")
    return render_template('admin_login.html')

@app.route('/admin/panel')
def admin_panel():
    if not session.get('admin'): return redirect(url_for('admin_login'))
    
    # FETCH ALL PRODUCTS
    all_products = Product.query.all()
    
    # GENERATE DASHBOARD STATS
    stats = {
        "total_items": len(all_products),
        "out_of_stock": len([p for p in all_products if p.stock <= 0]),
        "low_stock": len([p for p in all_products if 0 < p.stock <= 5]),
        "total_value": sum([p.price * p.stock for p in all_products if p.stock > 0])
    }
    
    # GROUP PRODUCTS BY SUBCATEGORY
    grouped = {}
    for p in all_products:
        sub = p.subcategory_str if p.subcategory_str else "General Inventory"
        if sub not in grouped: grouped[sub] = []
        grouped[sub].append(p)
        
    return render_template('admin_panel.html', grouped=grouped, stats=stats)

# THIS IS THE REQUEST THAT SETS THE STOCK AMOUNT
@app.route('/admin/api/update-stock', methods=['POST'])
def update_stock():
    if not session.get('admin'): return jsonify({"success": False}), 403
    data = request.json
    p = Product.query.get(data.get('id'))
    if p:
        p.stock = int(data.get('amount')) # Updates the stock field
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

# --- DB REPAIR & STARTUP ---
with app.app_context():
    db.create_all()
    print(f"✅ Database check complete at: {db_path}")

if __name__ == '__main__':
    app.run(debug=True, port=5000)

