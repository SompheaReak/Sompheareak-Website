import os
import requests
from flask import Flask, render_template, request, redirect, url_for, jsonify, session, abort
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.secret_key = 'somphea_reak_fixed_key_2025'

# --- DATABASE SETUP ---
basedir = os.path.abspath(os.path.dirname(__file__))
db_path = os.path.join(basedir, 'shop.db')
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + db_path
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# --- CONFIG ---
ADMIN_USER = 'Admin'
ADMIN_PASS = '123' # Change this!
BOT_TOKEN = "7528700801:AAGTvXjk5qPBnq_qx69ZOW4RMLuGy40w5k8"
CHAT_ID = "-1002654437316"

# --- SECURITY ---
banned_ips = ['123.45.67.89']

def notify_telegram(ip, user_agent):
    try:
        msg = f"📦 *New Visitor*\n*IP:* `{ip}`"
        requests.post(f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage", 
                     data={"chat_id": CHAT_ID, "text": msg, "parse_mode": "Markdown"}, timeout=2)
    except:
        pass

@app.before_request
def security_check():
    ip = request.headers.get('X-Forwarded-For', request.remote_addr).split(',')[0].strip()
    if ip in banned_ips: abort(403)
    if not session.get('notified'):
        notify_telegram(ip, request.headers.get('User-Agent'))
        session['notified'] = True

# --- 1. PRODUCT CATALOG (DATA ADDED) ---
PRODUCT_CATALOG = [
    {"id": 1, "name": "Obsidian Anchor", "price": 12000, "image": "https://images.unsplash.com/photo-1611591437281-460bfbe1220a?w=400", "categories": ["Men Bracelet", "Italy Bracelet"]},
    {"id": 2, "name": "Lego Porsche 911", "price": 45000, "image": "https://images.unsplash.com/photo-1585366119957-e9730b6d0f60?w=400", "categories": ["LEGO"]},
    {"id": 3, "name": "Gold Charm", "price": 5000, "image": "https://images.unsplash.com/photo-1573408301185-9146fe634ad0?w=400", "categories": ["Italy Bracelet", "Custom"]},
    {"id": 4, "name": "Iron Man Minifig", "price": 8000, "image": "https://images.unsplash.com/photo-1532330393533-443990a51d10?w=400", "categories": ["Toy", "LEGO"]},
]

# --- DATABASE MODEL ---
class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False) # Renamed to match HTML
    price = db.Column(db.Integer, nullable=False)
    image = db.Column(db.String(500), nullable=False)
    categories_str = db.Column(db.String(500), default="") 
    stock = db.Column(db.Integer, default=10)

def sync_catalog():
    with app.app_context():
        db.create_all()
        if Product.query.count() == 0:
            print("🔄 Syncing Catalog...")
            for item in PRODUCT_CATALOG:
                new_p = Product(
                    id=item['id'], name=item['name'], price=item['price'],
                    image=item['image'], categories_str=", ".join(item['categories']), stock=10
                )
                db.session.add(new_p)
            db.session.commit()
            print("✅ Data Synced!")

# --- ROUTES ---
@app.route('/')
def home():
    # Shows the Main Menu (Index.html) we made earlier
    return render_template('index.html')

@app.route('/custom-bracelet')
def custom_bracelet():
    products = Product.query.filter(Product.categories_str.contains("Italy")).all()
    return render_template('custom_bracelet.html', products=products)

@app.route('/lego')
def lego_page():
    products = Product.query.filter(Product.categories_str.contains("LEGO")).all()
    return render_template('lego.html', products=products)

@app.route('/lucky-draw')
def lucky_draw():
    return render_template('luckydraw.html')

@app.route('/men-bracelet')
def men_bracelet():
    products = Product.query.filter(Product.categories_str.contains("Men")).all()
    return render_template('men_bracelet.html', products=products)

# --- ADMIN ROUTES ---
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
    products = Product.query.all()
    return render_template('admin_panel.html', products=products)

# --- STARTUP ---
if __name__ == '__main__':
    sync_catalog()
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)


