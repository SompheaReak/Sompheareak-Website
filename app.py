import os
from flask import Flask, render_template, request, redirect, url_for, jsonify, session
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.secret_key = 'somphea_reak_studio_pro_2025'

# --- 1. CONFIGURATION ---
basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'shop_v2.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# --- 2. CONSTANTS ---
ADMIN_PASS = 'Thesong_Admin@2022?!$'

# --- 3. MODELS ---
class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200))
    price = db.Column(db.Integer)
    image = db.Column(db.String(500))
    category = db.Column(db.String(100))
    stock = db.Column(db.Integer, default=0)

class Setting(db.Model):
    key = db.Column(db.String(50), primary_key=True)
    value = db.Column(db.String(50))

# --- 4. PUBLIC ROUTES ---

@app.route('/')
def index():
    """Main Landing Page"""
    return render_template('index.html')

@app.route('/custom-bracelet')
def custom_bracelet():
    """Custom Bracelet Studio"""
    return render_template('custom_bracelet.html')

@app.route('/lego')
def lego_shop():
    """The New React LEGO Shop"""
    return render_template('lego.html')

@app.route('/toy-universe')
def toy_universe():
    """The New TaoBao Style Toy Shop"""
    return render_template('toy.html')

@app.route('/lucky-draw')
def lucky_draw():
    """The Lucky Draw Game"""
    return render_template('lucky_draw.html')

@app.route('/hot-sale')
def hot_sale():
    return "<h1>Hot Sale Coming Soon</h1>"

# --- 5. ADMIN ROUTES ---

@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        if request.form.get('password') == ADMIN_PASS:
            session['admin'] = True
            return redirect(url_for('admin_panel'))
        else:
            return render_template('admin_login.html', error="Invalid Password")
    return render_template('admin_login.html')

@app.route('/admin/panel')
def admin_panel():
    if not session.get('admin'): 
        return redirect(url_for('admin_login'))
    
    all_p = Product.query.all()
    grouped = {}
    for p in all_p:
        cat = p.category if p.category else "General"
        if cat not in grouped: grouped[cat] = []
        grouped[cat].append(p)
    
    try:
        override = Setting.query.get('stock_override')
        override_val = override.value if override else "off"
    except:
        override_val = "off"
    
    return render_template('admin_panel.html', grouped=grouped, override=override_val)

# --- 6. APIs ---

@app.route('/api/products')
def get_products():
    """For Bracelet Studio"""
    products = Product.query.all()
    override = Setting.query.get('stock_override')
    val = override.value if override else "off"
    return jsonify([{
        "id": p.id, "name_kh": p.name, "price": p.price, 
        "image": p.image, "categories": [p.category], 
        "stock": p.stock, "master_switch": val
    } for p in products])

@app.route('/api/sync', methods=['POST'])
def sync_catalog():
    data = request.json
    items = data.get('items', [])
    for item in items:
        p = Product.query.get(item['id'])
        if not p:
            cat = item['categories'][0] if isinstance(item.get('categories'), list) else item.get('category', 'General')
            new_p = Product(id=item['id'], name=item['name_kh'], price=item['price'], image=item['image'], category=cat, stock=0)
            db.session.add(new_p)
    db.session.commit()
    return jsonify(success=True)

@app.route('/admin/api/update-stock', methods=['POST'])
def update_stock():
    if not session.get('admin'): return jsonify(success=False), 403
    data = request.json
    p = Product.query.get(data['id'])
    if p:
        p.stock = int(data['amount'])
        db.session.commit()
        return jsonify(success=True)
    return jsonify(success=False)

@app.route('/admin/api/toggle-override', methods=['POST'])
def toggle_override():
    if not session.get('admin'): return jsonify(success=False), 403
    val = request.json.get('value')
    sett = Setting.query.get('stock_override')
    if not sett: 
        sett = Setting(key='stock_override', value=val)
        db.session.add(sett)
    else: 
        sett.value = val
    db.session.commit()
    return jsonify(success=True)

# Ensure tables exist
with app.app_context():
    db.create_all()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))


