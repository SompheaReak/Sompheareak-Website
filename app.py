import os
import requests
from flask import Flask, render_template, request, redirect, url_for, jsonify, session
from flask_sqlalchemy import SQLAlchemy

# --- INITIALIZATION ---
app = Flask(__name__)
app.secret_key = 'somphea_reak_studio_pro_2025'

# --- DATABASE SETUP ---
basedir = os.path.abspath(os.path.dirname(__file__))
db_path = os.path.join(basedir, 'shop_v2.db')
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + db_path
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# --- MODELS ---
class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200))
    price = db.Column(db.Integer)
    image = db.Column(db.String(500))
    category = db.Column(db.String(100))
    stock = db.Column(db.Integer, default=999)

class Setting(db.Model):
    key = db.Column(db.String(50), primary_key=True)
    value = db.Column(db.String(50))

# --- CONFIG ---
ADMIN_PASS = 'Thesong_Admin@2022?!$'
BOT_TOKEN = "7528700801:AAGTvXjk5qPBnq_qx69ZOW4RMLuGy40w5k8"
CHAT_ID = "-1002654437316"

# --- ROUTES ---

@app.route('/')
def home():
    all_p = Product.query.all()
    categories_query = db.session.query(Product.category).distinct().all()
    subcategories = [cat[0] for cat in categories_query if cat[0]]
    return render_template('home.html', products=all_p, subcategories=subcategories)

@app.route('/custom-bracelet')
def custom_bracelet():
    return render_template('custom_bracelet.html')

@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        if request.form.get('password') == ADMIN_PASS:
            session['admin'] = True
            return redirect(url_for('admin_panel'))
    return render_template('admin_login.html')

@app.route('/admin/logout')
def admin_logout():
    session.pop('admin', None)
    return redirect(url_for('home'))

@app.route('/admin/panel')
def admin_panel():
    if not session.get('admin'):
        return redirect(url_for('admin_login'))
    all_p = Product.query.order_by(Product.name.asc()).all()
    grouped = {}
    for p in all_p:
        cat = p.category or "General"
        if cat not in grouped: grouped[cat] = []
        grouped[cat].append(p)
    override = db.session.get(Setting, 'stock_override')
    return render_template('admin_panel.html', grouped=grouped, override=override.value if override else "off")

# --- API ENDPOINTS ---

@app.route('/api/get-data')
def get_data():
    override = db.session.get(Setting, 'stock_override')
    return jsonify({
        "stock": {p.id: p.stock for p in Product.query.all()},
        "override": override.value if override else "off"
    })

@app.route('/admin/api/update-stock', methods=['POST'])
def update_stock():
    if not session.get('admin'): return jsonify(success=False), 403
    data = request.json
    p = db.session.get(Product, data['id'])
    if p:
        p.stock = int(data['amount'])
        db.session.commit()
    return jsonify(success=True)

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

@app.route('/api/sync', methods=['POST'])
def sync_catalog():
    """Syncs product list: Adds new items and updates details of existing ones"""
    data = request.json
    items = data.get('items', [])
    
    for item in items:
        # Check if product exists in DB
        p = db.session.get(Product, item['id'])
        
        name = item.get('name_kh') or item['name']
        cat = item['categories'][0] if (item.get('categories') and len(item['categories']) > 0) else "General"
        
        if p:
            # Update existing product (Prices/Names might have changed in code)
            p.name = name
            p.price = item['price']
            p.image = item['image']
            p.category = cat
        else:
            # Add new product to DB
            new_p = Product(
                id=item['id'], 
                name=name, 
                price=item['price'], 
                image=item['image'], 
                category=cat,
                stock=999
            )
            db.session.add(new_p)
            
    db.session.commit()
    return jsonify(success=True)

@app.route('/admin/api/process-receipt', methods=['POST'])
def process_receipt():
    if not session.get('admin'): return jsonify(success=False), 403
    data = request.json
    for item in data.get('items', []):
        p = db.session.get(Product, item['id'])
        if p:
            p.stock = max(0, p.stock - int(item['qty']))
    db.session.commit()
    return jsonify(success=True)

@app.route('/admin/api/reset-all', methods=['POST'])
def reset_all():
    if not session.get('admin'): return jsonify(success=False), 403
    Product.query.update({Product.stock: 999})
    db.session.commit()
    return jsonify(success=True)

# --- BOOTSTRAP ---
with app.app_context():
    db.create_all()

if __name__ == "__main__":
    # Render uses the PORT environment variable
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)

