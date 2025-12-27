import os
import requests
from flask import Flask, render_template, request, redirect, url_for, jsonify, session
from flask_sqlalchemy import SQLAlchemy

# --- FLASK APP INITIALIZATION ---
app = Flask(__name__)
app.secret_key = 'somphea_reak_studio_pro_2025'

# --- 1. DATABASE CONFIGURATION ---
# We use an absolute path to ensure the SQLite file is accessible on any server
basedir = os.path.abspath(os.path.dirname(__file__))
db_path = os.path.join(basedir, 'shop_v2.db')

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + db_path
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# --- 2. DATA MODELS ---
class Product(db.Model):
    """Main Product Catalog for the Italy Bracelet Studio"""
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200))
    price = db.Column(db.Integer)
    image = db.Column(db.String(500))
    category = db.Column(db.String(100))
    # Default stock set to 999 to ensure availability by default
    stock = db.Column(db.Integer, default=999)

class Setting(db.Model):
    """Global Settings like the Master Stock Switch (Safety Lock)"""
    key = db.Column(db.String(50), primary_key=True)
    value = db.Column(db.String(50))

# --- 3. SYSTEM CONFIGURATION ---
ADMIN_PASS = 'Thesong_Admin@2022?!$'
BOT_TOKEN = "7528700801:AAGTvXjk5qPBnq_qx69ZOW4RMLuGy40w5k8"
CHAT_ID = "-1002654437316"

# --- 4. CUSTOMER-FACING ROUTES ---

@app.route('/')
def home():
    """Main Landing Page showing all products and categories"""
    all_products = Product.query.all()
    # Extract unique categories for the navigation bar
    categories_query = db.session.query(Product.category).distinct().all()
    subcategories = [cat[0] for cat in categories_query if cat[0]]
    cart = session.get('cart', [])
    return render_template('home.html', products=all_products, subcategories=subcategories, cart=cart, current_subcategory="All")

@app.route('/custom-bracelet')
def custom_bracelet():
    """The Interactive Bracelet Designer Studio"""
    return render_template('custom_bracelet.html')

@app.route('/category/<cat_name>')
def category(cat_name):
    """Filter products by specific category"""
    products = Product.query.filter_by(category=cat_name).all()
    categories_query = db.session.query(Product.category).distinct().all()
    subcategories = [cat[0] for cat in categories_query if cat[0]]
    cart = session.get('cart', [])
    return render_template('home.html', products=products, subcategories=subcategories, cart=cart, current_subcategory=cat_name)

@app.route('/search')
def search():
    """Live search for the product catalog"""
    query = request.args.get('q', '')
    products = Product.query.filter(Product.name.contains(query)).all()
    cart = session.get('cart', [])
    return render_template('home.html', products=products, subcategories=[], cart=cart, current_subcategory="Search Result")

@app.route('/add-to-cart', methods=['POST'])
def add_to_cart():
    """Saves items to the session-based cart"""
    pid = request.form.get('product_id')
    qty = int(request.form.get('quantity', 1))
    cart = session.get('cart', [])
    cart.append({'id': pid, 'qty': qty})
    session['cart'] = cart
    return jsonify(success=True, cart_count=len(cart))

@app.route('/cart')
def view_cart():
    """Displays items currently in the cart"""
    cart = session.get('cart', [])
    return f"<h1>Your Cart</h1><p>Items in cart: {len(cart)}</p><a href='/'>Return to Studio</a>"

# --- 5. SECURE ADMIN ROUTES ---

@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    """Secure login portal for the Admin Panel"""
    if request.method == 'POST':
        if request.form.get('password') == ADMIN_PASS:
            session['admin'] = True
            return redirect(url_for('admin_panel'))
    return render_template('admin_login.html')

@app.route('/admin/panel')
def admin_panel():
    """The Master Control Center for the Studio"""
    if not session.get('admin'):
        return redirect(url_for('admin_login'))
    
    all_p = Product.query.all()
    grouped_data = {}
    for p in all_p:
        cat = p.category if p.category else "General"
        if cat not in grouped_data: grouped_data[cat] = []
        grouped_data[cat].append(p)
    
    # Check the Master Safety Lock status
    override_setting = db.session.get(Setting, 'stock_override')
    override_val = override_setting.value if override_setting else "off"
    
    return render_template('admin_panel.html', grouped=grouped_data, override=override_val)

# --- 6. CORE API ENDPOINTS ---

@app.route('/api/get-data')
def get_data():
    """Provides live stock data and switch status to the Frontend Studio"""
    override_setting = db.session.get(Setting, 'stock_override')
    val = override_setting.value if override_setting else "off"
    
    return jsonify({
        "stock": {p.id: p.stock for p in Product.query.all()},
        "override": val
    })

@app.route('/api/sync', methods=['POST'])
def sync_catalog():
    """Imports new items from the frontend JS list into the Database"""
    data = request.json
    items = data.get('items', [])
    existing_ids = {p.id for p in Product.query.with_entities(Product.id).all()}
    
    for item in items:
        # Prioritize Khmer name if available
        display_name = item.get('name_kh') or item.get('name') or "Studio Item"
        
        if item['id'] not in existing_ids:
            new_p = Product(
                id=item['id'], 
                name=display_name, 
                price=item['price'], 
                image=item['image'], 
                category=item['categories'][0], 
                stock=999 # New items start with full stock
            )
            db.session.add(new_p)
    
    db.session.commit()
    return jsonify(success=True)

@app.route('/admin/api/reset-all', methods=['POST'])
def reset_all_stock():
    """Emergency reset: Sets all 500+ items back to 999 stock instantly"""
    if not session.get('admin'): return jsonify(success=False), 403
    Product.query.update({Product.stock: 999})
    db.session.commit()
    return jsonify(success=True)

@app.route('/admin/api/update-stock', methods=['POST'])
def update_stock():
    """Updates quantity for a specific item manually"""
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
    """Toggles the Master Safety Lock (Opposite Mode)"""
    if not session.get('admin'): return jsonify(success=False), 403
    val = request.json.get('value')
    sett = db.session.get(Setting, 'stock_override')
    
    if not sett:
        sett = Setting(key='stock_override', value=val)
        db.session.add(sett)
    else:
        sett.value = val
    
    db.session.commit()
    return jsonify(success=True)

@app.route('/admin/api/process-receipt', methods=['POST'])
def process_receipt():
    """Generates an Invoice and DEDUCTS quantities from the Database"""
    if not session.get('admin'): return jsonify(success=False), 403
    data = request.json
    items_list = []
    total_bill = 0
    
    for item in data.get('items', []):
        p = db.session.get(Product, item['id'])
        if p:
            # Deduce amount in stock
            p.stock = max(0, p.stock - int(item['qty']))
            items_list.append(f"• {p.name} x{item['qty']}")
            total_bill += (p.price * item['qty'])
    
    db.session.commit()
    
    # Send Notification to Telegram with Error Handling
    try:
        msg = f"<b>🔔 INVOICE CONFIRMED</b>\n" + "\n".join(items_list) + f"\n<b>Total: {total_bill}៛</b>"
        requests.post(f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage", 
                     json={"chat_id": CHAT_ID, "text": msg, "parse_mode": "HTML"}, 
                     timeout=5)
    except Exception as e:
        print(f"Telegram Error: {e}")
    
    return jsonify(success=True)

# --- INIT DATABASE ---
with app.app_context():
    db.create_all()

if __name__ == "__main__":
    # Ensure port is pulled from environment for Render/PythonAnywhere deployment
    server_port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=server_port)

