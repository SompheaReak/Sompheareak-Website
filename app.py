import os
import requests
from flask import Flask, render_template, request, redirect, url_for, jsonify, session, abort
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.secret_key = 'somphea_reak_studio_pro_2025'

# --- DATABASE SETUP ---
basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'shop.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# --- CONFIG ---
ADMIN_USER = 'AdminSompheaReakVitou'
ADMIN_PASS = 'Thesong_Admin@2022?!$'
BOT_TOKEN = "7528700801:AAGTvXjk5qPBnq_qx69ZOW4RMLuGy40w5k8"
CHAT_ID = "-1002654437316"

class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name_kh = db.Column(db.String(200))
    price = db.Column(db.Integer)
    image = db.Column(db.String(500))
    category = db.Column(db.String(100))
    stock = db.Column(db.Integer, default=0)

def notify_telegram(msg):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    try: requests.post(url, data={"chat_id": CHAT_ID, "text": msg, "parse_mode": "Markdown"})
    except: pass

# --- ROUTES ---

@app.route('/')
def home():
    notify_telegram("🌐 *New Visitor* on Studio")
    return render_template('custom_bracelet.html')

@app.route('/admin/panel')
def admin_panel():
    if not session.get('admin'): return redirect(url_for('admin_login'))
    all_p = Product.query.all()
    grouped = {}
    for p in all_p:
        if p.category not in grouped: grouped[p.category] = []
        grouped[p.category].append(p)
    return render_template('admin_panel.html', grouped=grouped)

@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        if request.form['username'] == ADMIN_USER and request.form['password'] == ADMIN_PASS:
            session['admin'] = True
            return redirect(url_for('admin_panel'))
    return render_template('admin_login.html')

# --- API FOR DATA SYNC ---

@app.route('/api/sync', methods=['POST'])
def sync_catalog():
    """Reads product list from HTML and updates Database"""
    data = request.json
    items = data.get('items', [])
    for item in items:
        p = Product.query.get(item['id'])
        if not p:
            new_p = Product(id=item['id'], name_kh=item['name_kh'], price=item['price'], 
                            image=item['image'], category=item['category'], stock=0)
            db.session.add(new_p)
        else:
            p.name_kh, p.price, p.image, p.category = item['name_kh'], item['price'], item['image'], item['category']
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

with app.app_context(): db.create_all()

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port, debug=True)

