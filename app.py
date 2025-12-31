import os
import requests
from flask import Flask, render_template, request, redirect, url_for, jsonify, session
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.secret_key = 'somphea_reak_studio_pro_2025'

# --- 1. DATABASE SETUP ---
basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'shop_v2.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# --- 2. MODELS ---
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

# --- 3. CONFIG ---
ADMIN_PASS = 'Thesong_Admin@2022?!$'
BOT_TOKEN = "7528700801:AAGTvXjk5qPBnq_qx69ZOW4RMLuGy40w5k8"
CHAT_ID = "-1002654437316"

# --- 4. NAVIGATION ROUTES (The New Part) ---

@app.route('/')
def home():
    # Shows the Main Menu (index.html) instead of just the bracelet page
    return render_template('index.html')

@app.route('/custom-bracelet')
def custom_bracelet():
    # Fetches products so the loop {% for p in products %} works
    products = Product.query.filter(
        (Product.category.contains("Custom")) | 
        (Product.category.contains("Italy"))
    ).all()
    # Fallback: if no specific category, show everything so page isn't empty
    if not products: products = Product.query.all()
    return render_template('custom_bracelet.html', products=products)

@app.route('/lego')
def lego():
    products = Product.query.filter(Product.category.contains("LEGO")).all()
    return render_template('lego.html', products=products)

@app.route('/men-bracelet')
def men_bracelet():
    products = Product.query.filter(Product.category.contains("Men")).all()
    return render_template('men_bracelet.html', products=products)

@app.route('/lucky-draw')
def lucky_draw():
    return render_template('luckydraw.html')

@app.route('/hot-sale')
def hot_sale():
    products = Product.query.filter(Product.category.contains("Hot")).all()
    return render_template('men_bracelet.html', products=products, title="Hot Sale")

@app.route('/toy')
def toy():
    products = Product.query.filter(Product.category.contains("Toy")).all()
    return render_template('men_bracelet.html', products=products, title="Toy Collection")

# --- 5. ADMIN ROUTES (Your Original Logic) ---

@app.route('/admin/panel')
def admin_panel():
    if not session.get('admin'): return redirect(url_for('admin_login'))
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

@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        if request.form.get('password') == ADMIN_PASS:
            session['admin'] = True
            return redirect(url_for('admin_panel'))
    return render_template('admin_login.html')

# --- 6. API ROUTES (Stock & Sync) ---

@app.route('/api/get-data')
def get_data():
    try:
        override = Setting.query.get('stock_override')
        val = override.value if override else "off"
    except:
        val = "off"
    return jsonify({
        "stock": {p.id: p.stock for p in Product.query.all()},
        "override": val
    })

@app.route('/api/sync', methods=['POST'])
def sync_catalog():
    data = request.json
    items = data.get('items', [])
    for item in items:
        p = Product.query.get(item['id'])
        if not p:
            # Safe category extraction
            cat = item['categories'][0] if 'categories' in item and item['categories'] else "General"
            new_p = Product(id=item['id'], name=item.get('name_kh', 'Item'), price=item.get('price',0), image=item.get('image',''), category=cat, stock=0)
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
    if not sett: sett = Setting(key='stock_override', value=val)
    else: sett.value = val
    db.session.add(sett)
    db.session.commit()
    return jsonify(success=True)

@app.route('/admin/api/process-receipt', methods=['POST'])
def process_receipt():
    if not session.get('admin'): return jsonify(success=False), 403
    data = request.json
    for item in data['items']:
        p = Product.query.get(item['id'])
        if p: p.stock = max(0, p.stock - int(item['qty']))
    db.session.commit()
    return jsonify(success=True)

# --- 7. AUTO-SEEDER (Runs if DB is empty) ---
def seed_data():
    if Product.query.count() == 0:
        print("🌱 Seeding initial data...")
        items = [
            Product(name="Obsidian Anchor", price=12000, category="Men Bracelet", stock=10, image="https://images.unsplash.com/photo-1611591437281-460bfbe1220a?w=400"),
            Product(name="Lego Porsche 911", price=45000, category="LEGO", stock=5, image="https://images.unsplash.com/photo-1585366119957-e9730b6d0f60?w=400"),
            Product(name="Gold Bead", price=5000, category="Custom", stock=100, image="https://images.unsplash.com/photo-1605100804763-247f67b3557e?w=400"),
            Product(name="Robot Warrior", price=8000, category="Toy", stock=0, image="https://images.unsplash.com/photo-1532330393533-443990a51d10?w=400"),
        ]
        db.session.add_all(items)
        db.session.commit()

# --- 8. STARTUP ---
with app.app_context():
    db.create_all()
    seed_data()

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)


