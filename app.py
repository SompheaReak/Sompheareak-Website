import os
import requests
from flask import Flask, render_template, request, redirect, url_for, jsonify, session
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.secret_key = 'somphea_reak_studio_pro_2025'

# --- 1. DATABASE SETUP (Using v2 to fix deployment) ---
basedir = os.path.abspath(os.path.dirname(__file__))
# We renamed this to 'shop_v2.db' to force a fresh database creation
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

# --- 4. ROUTES ---
@app.route('/')
def home():
    return render_template('custom_bracelet.html')

@app.route('/admin/panel')
def admin_panel():
    if not session.get('admin'): return redirect(url_for('admin_login'))
    all_p = Product.query.all()
    grouped = {}
    for p in all_p:
        cat = p.category if p.category else "General"
        if cat not in grouped: grouped[cat] = []
        grouped[cat].append(p)
    
    # Safe check for override
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

# --- 5. API ---
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
            new_p = Product(id=item['id'], name=item['name_kh'], price=item['price'], image=item['image'], category=item['categories'][0], stock=0)
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

# Ensure tables exist
with app.app_context():
    db.create_all()

# Port configuration for Render/Heroku
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))



