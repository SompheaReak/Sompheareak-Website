import os
import requests
from flask import Flask, render_template, request, redirect, url_for, jsonify, session
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.secret_key = 'somphea_reak_studio_pro_2025'

# --- 1. DATABASE SETUP (Permanent Storage) ---
basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'shop.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# --- 2. CONFIGURATION ---
ADMIN_PASS = 'Thesong_Admin@2022?!$'
# Telegram settings
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
    # For now, we go straight to the bracelet studio
    notify_telegram("💎 *Visitor* entered Bracelet Studio")
    return render_template('custom_bracelet.html')

@app.route('/admin/panel')
def admin_panel():
    if not session.get('admin'): return redirect(url_for('admin_login'))
    
    # Group products by category for the Admin display
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
    return '''
    <body style="background:#f1f5f9;height:100vh;display:flex;align-items:center;justify-content:center;font-family:sans-serif;">
        <form method="post" style="background:white;padding:30px;border-radius:20px;box-shadow:0 10px 30px rgba(0,0,0,0.1);text-align:center;">
            <h2 style="margin:0 0 20px 0;font-weight:900;">ADMIN LOGIN</h2>
            <input type="password" name="password" placeholder="Password" style="padding:10px;border:1px solid #ddd;border-radius:10px;width:100%;margin-bottom:15px;">
            <button style="width:100%;padding:10px;background:#ea580c;color:white;border:none;border-radius:10px;font-weight:bold;">ENTER</button>
        </form>
    </body>
    '''

# --- 4. API (The Magic Sync) ---

@app.route('/api/sync', methods=['POST'])
def sync_catalog():
    """Reads the list from HTML and saves it to Database"""
    data = request.json
    items = data.get('items', [])
    
    for item in items:
        p = Product.query.get(item['id'])
        # If product is new, add it. Stock starts at 0.
        if not p:
            new_p = Product(
                id=item['id'], 
                name=item['name_kh'], 
                price=item['price'], 
                image=item['image'], 
                category=item['categories'][0], 
                stock=0
            )
            db.session.add(new_p)
        else:
            # If product exists, just update details (NOT STOCK)
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

# Create database tables if they don't exist
with app.app_context():
    db.create_all()


