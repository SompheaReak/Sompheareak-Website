import os
import requests
from flask import Flask, render_template, request, redirect, url_for, jsonify, session
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.secret_key = 'somphea_reak_studio_pro_2025'

# --- 1. DATABASE SETUP ---
basedir = os.path.abspath(os.path.dirname(__file__))
db_path = os.path.join(basedir, 'shop_v2.db')
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + db_path
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# --- 2. MODELS ---
class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200))
    price = db.Column(db.Integer)
    image = db.Column(db.String(500))
    category = db.Column(db.String(100))
    # Every product starts with 999 stock
    stock = db.Column(db.Integer, default=999)

class Setting(db.Model):
    key = db.Column(db.String(50), primary_key=True)
    value = db.Column(db.String(50))

# --- 3. CONFIG ---
ADMIN_PASS = 'Thesong_Admin@2022?!$'
BOT_TOKEN = "7528700801:AAGTvXjk5qPBnq_qx69ZOW4RMLuGy40w5k8"
CHAT_ID = "-1002654437316"

# --- 4. SHOP ROUTES ---

@app.route('/')
def home():
    all_p = Product.query.all()
    # Get unique categories for the sticky bar
    subs = db.session.query(Product.category).distinct().all()
    subcategories = [s[0] for s in subs if s[0]]
    cart = session.get('cart', [])
    return render_template('home.html', products=all_p, subcategories=subcategories, cart=cart, current_subcategory="All")

@app.route('/custom-bracelet')
def custom_bracelet():
    return render_template('custom_bracelet.html')

@app.route('/category/<cat_name>')
def category(cat_name):
    products = Product.query.filter_by(category=cat_name).all()
    subs = db.session.query(Product.category).distinct().all()
    subcategories = [s[0] for s in subs if s[0]]
    cart = session.get('cart', [])
    return render_template('home.html', products=products, subcategories=subcategories, cart=cart, current_subcategory=cat_name)

@app.route('/search')
def search():
    query = request.args.get('q', '')
    products = Product.query.filter(Product.name.contains(query)).all()
    cart = session.get('cart', [])
    return render_template('home.html', products=products, subcategories=[], cart=cart, current_subcategory="Search")

@app.route('/add-to-cart', methods=['POST'])
def add_to_cart():
    pid = request.form.get('product_id')
    qty = int(request.form.get('quantity', 1))
    cart = session.get('cart', [])
    cart.append({'id': pid, 'qty': qty})
    session['cart'] = cart
    return jsonify(success=True, cart_count=len(cart))

@app.route('/cart')
def view_cart():
    cart = session.get('cart', [])
    return f"<h1>Cart</h1><p>Items: {len(cart)}</p><a href='/'>Go Back</a>"

# --- 5. ADMIN ROUTES ---

@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        if request.form.get('password') == ADMIN_PASS:
            session['admin'] = True
            return redirect(url_for('admin_panel'))
    return render_template('admin_login.html')

@app.route('/admin/panel')
def admin_panel():
    if not session.get('admin'): return redirect(url_for('admin_login'))
    all_p = Product.query.all()
    grouped = {}
    for p in all_p:
        cat = p.category if p.category else "General"
        if cat not in grouped: grouped[cat] = []
        grouped[cat].append(p)
    
    override = db.session.get(Setting, 'stock_override')
    override_val = override.value if override else "off"
    return render_template('admin_panel.html', grouped=grouped, override=override_val)

# --- 6. API ---

@app.route('/api/get-data')
def get_data():
    override = db.session.get(Setting, 'stock_override')
    val = override.value if override else "off"
    return jsonify({
        "stock": {p.id: p.stock for p in Product.query.all()},
        "override": val
    })

@app.route('/api/sync', methods=['POST'])
def sync_catalog():
    data = request.json
    items = data.get('items', [])
    existing_ids = {p.id for p in Product.query.with_entities(Product.id).all()}
    
    for item in items:
        name_val = item.get('name_kh') or item.get('name') or "Item"
        if item['id'] not in existing_ids:
            new_p = Product(
                id=item['id'], name=name_val, price=item['price'], 
                image=item['image'], category=item['categories'][0], 
                stock=999 # FORCE 999
            )
            db.session.add(new_p)
    db.session.commit()
    return jsonify(success=True)

@app.route('/admin/api/update-stock', methods=['POST'])
def update_stock():
    if not session.get('admin'): return jsonify(success=False), 403
    data = request.json
    p = db.session.get(Product, data['id'])
    if p:
        p.stock = int(data['amount'])
        db.session.commit()
        return jsonify(success=True)
    return jsonify(success=False)

@app.route('/admin/api/toggle-override', methods=['POST'])
def toggle_override():
    if not session.get('admin'): return jsonify(success=False), 403
    val = request.json.get('value')
    sett = db.session.get(Setting, 'stock_override')
    if not sett:
        sett = Setting(key='stock_override', value=val)
        db.session.add(sett)
    else: sett.value = val
    db.session.commit()
    return jsonify(success=True)

@app.route('/admin/api/process-receipt', methods=['POST'])
def process_receipt():
    if not session.get('admin'): return jsonify(success=False), 403
    data = request.json
    items_list = []
    total_bill = 0
    for item in data.get('items', []):
        p = db.session.get(Product, item['id'])
        if p:
            p.stock = max(0, p.stock - int(item['qty']))
            items_list.append(f"• {p.name} x{item['qty']}")
            total_bill += (p.price * item['qty'])
    db.session.commit()
    
    try:
        msg = f"<b>🔔 NEW SALE</b>\n" + "\n".join(items_list) + f"\n<b>Total: {total_bill}៛</b>"
        requests.post(f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage", json={"chat_id": CHAT_ID, "text": msg, "parse_mode": "HTML"}, timeout=2)
    except: pass
    return jsonify(success=True)

with app.app_context():
    db.create_all()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))

