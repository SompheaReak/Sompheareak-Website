import os
import requests
from flask import Flask, render_template, request, redirect, url_for, jsonify, session, abort
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import inspect  # <--- IMPORT ADDED

app = Flask(__name__)
app.secret_key = 'somphea_reak_fixed_key_2025'

# --- DATABASE SETUP ---
basedir = os.path.abspath(os.path.dirname(__file__))
db_path = os.path.join(basedir, 'shop.db')
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + db_path
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# --- CONFIG ---
ADMIN_USER = 'AdminSompheaReakVitou'
ADMIN_PASS = 'Thesong_Admin@2022?!$'
BOT_TOKEN = "7528700801:AAGTvXjk5qPBnq_qx69ZOW4RMLuGy40w5k8"
CHAT_ID = "-1002654437316"
banned_ips = ['123.45.67.89']

# --- 1. POPULATED CATALOG (Fixed Empty Shop) ---
PRODUCT_CATALOG = [
    {"id": 1, "name_kh": "Obsidian Anchor", "price": 12000, "image": "https://images.unsplash.com/photo-1611591437281-460bfbe1220a?w=400", "categories": ["Men Bracelet", "Italy Bracelet"], "subcategory": "General"},
    {"id": 2, "name_kh": "Lego Porsche", "price": 45000, "image": "https://images.unsplash.com/photo-1585366119957-e9730b6d0f60?w=400", "categories": ["LEGO"], "subcategory": "Building Set"},
    {"id": 3, "name_kh": "Golden Charm", "price": 5000, "image": "https://images.unsplash.com/photo-1573408301185-9146fe634ad0?w=400", "categories": ["Italy Bracelet", "Custom"], "subcategory": "Charm"},
    {"id": 4, "name_kh": "Iron Man Minifig", "price": 8000, "image": "https://images.unsplash.com/photo-1532330393533-443990a51d10?w=400", "categories": ["Toy", "LEGO"], "subcategory": "Minifigures"},
]

# --- MODEL ---
class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name_kh = db.Column(db.String(200), nullable=False)
    price = db.Column(db.Integer, nullable=False)
    image = db.Column(db.String(500), nullable=False)
    categories_str = db.Column(db.String(500), default="") 
    subcategory_str = db.Column(db.String(500), default="") 
    stock = db.Column(db.Integer, default=10)

# --- ROUTES ---
@app.route('/')
def home():
    # Redirect to the main menu (index.html) instead of just custom bracelet
    return render_template('index.html')

@app.route('/custom-bracelet')
def custom_bracelet():
    all_products = Product.query.all()
    # Fixed safety check for None types
    studio_items = [
        p for p in all_products 
        if p.categories_str and ("Italy Bracelet" in p.categories_str or "Charm" in p.categories_str)
    ]
    
    # JSON format for the customization JS
    products_json = [{
        "id": p.id, "name_kh": p.name_kh, "price": p.price, 
        "image": p.image, "stock": p.stock, 
        "categories": p.categories_str.split(', ') if p.categories_str else []
    } for p in studio_items]
    
    return render_template('custom_bracelet.html', products=products_json)

# [Keep your other routes like /lego, /men-bracelet, /admin here...]
@app.route('/men-bracelet')
def men_bracelet():
    products = Product.query.filter(Product.categories_str.contains("Men")).all()
    return render_template('men_bracelet.html', products=products)

@app.route('/lego')
def lego_page():
    products = Product.query.filter(Product.categories_str.contains("LEGO")).all()
    return render_template('lego.html', products=products)

@app.route('/lucky-draw')
def lucky_draw():
    return render_template('luckydraw.html')

# --- SYNC ENGINE (Fixed) ---
def sync_catalog():
    try:
        # FIX 1: Use proper SQLAlchemy inspector
        inspector = inspect(db.engine)
        if not inspector.has_table("product"):
            db.create_all()
            print("📦 Database Created.")
            
        # FIX 2: Only sync if DB is empty to prevent overwriting edits
        if Product.query.count() == 0:
            print("🔄 Syncing Catalog...")
            for item in PRODUCT_CATALOG:
                cat_str = ", ".join(item.get('categories', []))
                sub_str = item.get('subcategory', 'General')
                new_p = Product(
                    id=item['id'], name_kh=item['name_kh'], price=item['price'],
                    image=item['image'], categories_str=cat_str, subcategory_str=sub_str, stock=10
                )
                db.session.add(new_p)
            db.session.commit()
            print("✅ Sync Complete!")
            
    except Exception as e:
        print(f"⚠️ Database Error: {e}")

if __name__ == '__main__':
    with app.app_context():
        sync_catalog()
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port, debug=True)

