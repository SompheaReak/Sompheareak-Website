import os
import requests
from flask import Flask, render_template, request, redirect, url_for, jsonify, session
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.secret_key = 'somphea_reak_studio_pro_2025'

# --- 1. DATABASE SETUP (Safe Path for Production) ---
basedir = os.path.abspath(os.path.dirname(__file__))
# This ensures the database is created in the same folder as app.py
db_path = os.path.join(basedir, 'shop.db')
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + db_path
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# --- 2. CONFIGURATION ---
ADMIN_PASS = 'Thesong_Admin@2022?!$'
BOT_TOKEN = "7528700801:AAGTvXjk5qPBnq_qx69ZOW4RMLuGy40w5k8"
CHAT_ID = "-1002654437316"

class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200))
    price = db.Column(db.Integer)
    image = db.Column(db.String(500))
    category = db.Column(db.String(100))
    stock = db.Column(db.Integer, default=0)

def notify_telegram(msg):
    try: requests.post(f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage", data={"chat_id": CHAT_ID, "text": msg, "parse_mode": "Markdown"})
    except: pass

# --- 3. ROUTES ---

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
    return render_template('admin_panel.html', grouped=grouped)

@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        if request.form.get('password') == ADMIN_PASS:
            session['admin'] = True
            return redirect(url_for('admin_panel'))
    return render_template('admin_login.html')

# --- 4. API (SYNC & STOCK) ---

@app.route('/api/sync', methods=['POST'])
def sync_catalog():
    data = request.json
    items = data.get('items', [])
    for item in items:
        p = Product.query.get(item['id'])
        if not p:
            new_p = Product(id=item['id'], name=item['name_kh'], price=item['price'], image=item['image'], category=item['categories'][0], stock=0)
            db.session.add(new_p)
        else:
            p.name = item['name_kh']
            p.price = item['price']
            p.image = item['image']
    db.session.commit()
    return jsonify(success=True)

@app.route('/api/get-stock')
def get_stock():
    return jsonify({p.id: p.stock for p in Product.query.all()})

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

@app.route('/admin/api/process-receipt', methods=['POST'])
def process_receipt():
    if not session.get('admin'): return jsonify(success=False), 403
    data = request.json
    for item in data['items']:
        p = Product.query.get(item['id'])
        if p: p.stock = max(0, p.stock - int(item['qty']))
    db.session.commit()
    return jsonify(success=True)

# Important for Render/Heroku to create the DB on startup
with app.app_context():
    db.create_all()

if __name__ == "__main__":
    # This part is only for local testing
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))

