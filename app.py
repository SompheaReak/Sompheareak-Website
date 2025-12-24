import os
import requests
from flask import Flask, render_template, request, redirect, url_for, jsonify, session
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.secret_key = 'somphea_reak_fixed_key_2025'

# --- DATABASE SETUP ---
basedir = os.path.abspath(os.path.dirname(__file__))
db_path = os.path.join(basedir, 'shop.db')
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + db_path
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# --- CONFIGURATION ---
ADMIN_USER = 'AdminSompheaReakVitou'
ADMIN_PASS = 'Thesong_Admin@2022?!$'

# ==========================================
# 1. PRODUCT CATALOG
# ==========================================
PRODUCT_CATALOG = [
    # --- Charm Base
    {"id": 1, "name_kh": "Silver Charm", "price": 400, "image": "/static/images/c01.jpg", "categories": ["Italy Bracelet", "Charm"], "subcategory": "General"},
   
    # --- F1 LOGOS (1100 - 1104, 1191 - 1195) ---
    {"id": 1100, "name_kh": "Classic F1 Logo", "price": 3000, "image": "/static/images/charm-f1–101.jpg", "categories": ["Italy Bracelet", "Class F1🏎️"], "subcategory": "F1 Logos"},
    {"id": 1191, "name_kh": "Classic F1", "price": 3000, "image": "/static/images/charm-chain-03.jpg", "categories": ["Italy Bracelet", "Class F1🏎️"], "subcategory": "F1 Logos"},
    {"id": 1192, "name_kh": "Classic F1 - Ferri", "price": 3000, "image": "/static/images/charm-f1-301.jpg", "categories": ["Italy Bracelet", "Class F1🏎️"], "subcategory": "F1 Logos"},
    {"id": 1193, "name_kh": "Classic F1 - Porsche", "price": 3000, "image": "/static/images/charm-f1-302.jpg", "categories": ["Italy Bracelet", "Class F1🏎️"], "subcategory": "F1 Logos"},
    {"id": 1194, "name_kh": "Classic F1 - BMW", "price": 3000, "image": "/static/images/charm-f1-303.jpg", "categories": ["Italy Bracelet", "Class F1🏎️"], "subcategory": "F1 Logos"},
    {"id": 1195, "name_kh": "Classic F1 - BMW", "price": 3000, "image": "/static/images/charm-f1-304.jpg", "categories": ["Italy Bracelet", "Class F1🏎️"], "subcategory": "F1 Logos"},
    
    {"id": 1101, "name_kh": "Classic F1 - Mercedes", "price": 3000, "image": "/static/images/cc15.jpg", "categories": ["Italy Bracelet", "Class F1🏎️"], "subcategory": "F1 Logos"},
    {"id": 1102, "name_kh": "Classic F1 - Ferrari", "price": 3000, "image": "/static/images/cc04.jpg", "categories": ["Italy Bracelet", "Class F1🏎️"], "subcategory": "F1 Logos"},
    {"id": 1103, "name_kh": "Classic F1 - Porsche", "price": 3000, "image": "/static/images/cc12.jpg", "categories": ["Italy Bracelet", "Class F1🏎️"], "subcategory": "F1 Logos"},
    {"id": 1104, "name_kh": "Classic F1 - BMW", "price": 3000, "image": "/static/images/cc06.jpg", "categories": ["Italy Bracelet", "Class F1🏎️"], "subcategory": "F1 Logos"},

    # --- Pink F1 
    {"id": 1200, "name_kh": "Pink F1 Logo", "price": 3000, "image": "/static/images/charm-f1-201.jpg", "categories": ["Italy Bracelet", "Pink F1🏎️"], "subcategory": "Pink Collection"},
    {"id": 1291, "name_kh": "Classic F1 - Mercedes", "price": 3000, "image": "/static/images/charm-chain-03.jpg", "categories": ["Italy Bracelet", "Pink F1🏎️"], "subcategory": "Pink Collection"},
    {"id": 1292, "name_kh": "Classic F1 - Ferri", "price": 3000, "image": "/static/images/charm-f1-301.jpg", "categories": ["Italy Bracelet", "Pink F1🏎️"], "subcategory": "Pink Collection"},
    {"id": 1293, "name_kh": "Classic F1 - Porsche", "price": 3000, "image": "/static/images/charm-f1-302.jpg", "categories": ["Italy Bracelet", "Pink F1🏎️"], "subcategory": "Pink Collection"},
    {"id": 1294, "name_kh": "Classic F1 - BMW", "price": 3000, "image": "/static/images/charm-f1-303.jpg", "categories": ["Italy Bracelet", "Pink F1🏎️"], "subcategory": "Pink Collection"},
    {"id": 1295, "name_kh": "Classic F1 - BMW", "price": 3000, "image": "/static/images/charm-f1-304.jpg", "categories": ["Italy Bracelet", "Pink F1🏎️"], "subcategory": "Pink Collection"},

    {"id": 1201, "name_kh": "Pink F1 - Mercedes", "price": 3000, "image": "/static/images/charm-f1-202.jpg", "categories": ["Italy Bracelet", "Pink F1🏎️"], "subcategory": "Pink Collection"},
    {"id": 1202, "name_kh": "Pink F1 - Ferrari", "price": 3000, "image": "/static/images/charm-f1-203.jpg", "categories": ["Italy Bracelet", "Pink F1🏎️"], "subcategory": "Pink Collection"},
    {"id": 1203, "name_kh": "Pink F1 - Porsche", "price": 3000, "image": "/static/images/charm-f1-204.jpg", "categories": ["Italy Bracelet", "Pink F1🏎️"], "subcategory": "Pink Collection"},
    {"id": 1204, "name_kh": "Pink F1 - BMW", "price": 3000, "image": "/static/images/charm-f1-205.jpg", "categories": ["Italy Bracelet", "Pink F1🏎️"], "subcategory": "Pink Collection"},

    # --- CAR LOGOS (1001 - 1015) ---
    {"id": 1001, "name_kh": "Car Charm 01", "price": 3000, "image": "/static/images/cc01.jpg", "categories": ["Italy Bracelet", "Car Logo"], "subcategory": "Car Brands"},
    {"id": 1002, "name_kh": "Car Charm 02", "price": 3000, "image": "/static/images/cc02.jpg", "categories": ["Italy Bracelet", "Car Logo"], "subcategory": "Car Brands"},
    {"id": 1003, "name_kh": "Car Charm 03", "price": 3000, "image": "/static/images/cc03.jpg", "categories": ["Italy Bracelet", "Car Logo"], "subcategory": "Car Brands"},
    {"id": 1004, "name_kh": "Car Charm 04", "price": 3000, "image": "/static/images/cc04.jpg", "categories": ["Italy Bracelet", "Car Logo"], "subcategory": "Car Brands"},
    {"id": 1005, "name_kh": "Car Charm 05", "price": 3000, "image": "/static/images/cc05.jpg", "categories": ["Italy Bracelet", "Car Logo"], "subcategory": "Car Brands"},
    {"id": 1006, "name_kh": "Car Charm 06", "price": 3000, "image": "/static/images/cc06.jpg", "categories": ["Italy Bracelet", "Car Logo"], "subcategory": "Car Brands"},
    {"id": 1007, "name_kh": "Car Charm 07", "price": 3000, "image": "/static/images/cc07.jpg", "categories": ["Italy Bracelet", "Car Logo"], "subcategory": "Car Brands"}, 
    {"id": 1008, "name_kh": "Car Charm 08", "price": 3000, "image": "/static/images/cc08.jpg", "categories": ["Italy Bracelet", "Car Logo"], "subcategory": "Car Brands"},
    {"id": 1009, "name_kh": "Car Charm 09", "price": 3000, "image": "/static/images/cc09.jpg", "categories": ["Italy Bracelet", "Car Logo"], "subcategory": "Car Brands"},
    {"id": 1010, "name_kh": "Car Charm 10", "price": 3000, "image": "/static/images/cc10.jpg", "categories": ["Italy Bracelet", "Car Logo"], "subcategory": "Car Brands"},
    {"id": 1011, "name_kh": "Car Charm 11", "price": 3000, "image": "/static/images/cc11.jpg", "categories": ["Italy Bracelet", "Car Logo"], "subcategory": "Car Brands"},
    {"id": 1012, "name_kh": "Car Charm 12", "price": 3000, "image": "/static/images/cc12.jpg", "categories": ["Italy Bracelet", "Car Logo"], "subcategory": "Car Brands"},
    {"id": 1013, "name_kh": "Car Charm 13", "price": 3000, "image": "/static/images/cc13.jpg", "categories": ["Italy Bracelet", "Car Logo"], "subcategory": "Car Brands"},
    {"id": 1014, "name_kh": "Car Charm 14", "price": 3000, "image": "/static/images/cc14.jpg", "categories": ["Italy Bracelet", "Car Logo"], "subcategory": "Car Brands"},
    {"id": 1015, "name_kh": "Car Charm 15", "price": 3000, "image": "/static/images/cc15.jpg", "categories": ["Italy Bracelet", "Car Logo"], "subcategory": "Car Brands"},

    # --- FLAGS (2001 - 2019) ---
    {"id": 2001, "name_kh": "Flag Charm 01", "price": 3000, "image": "/static/images/cf01.jpg", "categories": ["Italy Bracelet", "Flag"], "subcategory": "Football"},
    {"id": 2002, "name_kh": "Flag Charm 02", "price": 3000, "image": "/static/images/cf02.jpg", "categories": ["Italy Bracelet", "Flag"], "subcategory": "Football"},
    {"id": 2003, "name_kh": "Flag Charm 03", "price": 3000, "image": "/static/images/cf03.jpg", "categories": ["Italy Bracelet", "Flag"], "subcategory": "Football"},
    {"id": 2004, "name_kh": "Flag Charm 04", "price": 3000, "image": "/static/images/cf04.jpg", "categories": ["Italy Bracelet", "Flag"], "subcategory": "Football"},
    {"id": 2005, "name_kh": "Flag Charm 05", "price": 3000, "image": "/static/images/cf05.jpg", "categories": ["Italy Bracelet", "Flag"], "subcategory": "Football"},
    {"id": 2006, "name_kh": "Flag Charm 06", "price": 3000, "image": "/static/images/cf06.jpg", "categories": ["Italy Bracelet", "Flag"], "subcategory": "Football"},
    {"id": 2007, "name_kh": "Flag Charm 07", "price": 3000, "image": "/static/images/cf07.jpg", "categories": ["Italy Bracelet", "Flag"], "subcategory": "Football"},
    {"id": 2008, "name_kh": "Flag Charm 08", "price": 3000, "image": "/static/images/cf08.jpg", "categories": ["Italy Bracelet", "Flag"], "subcategory": "Football"},
    {"id": 2009, "name_kh": "Flag Charm 09", "price": 3000, "image": "/static/images/cf09.jpg", "categories": ["Italy Bracelet", "Flag"], "subcategory": "Football"},
    {"id": 2010, "name_kh": "Flag Charm 10", "price": 3000, "image": "/static/images/cf10.jpg", "categories": ["Italy Bracelet", "Flag"], "subcategory": "Football"},
    {"id": 2011, "name_kh": "Flag Charm 11", "price": 3000, "image": "/static/images/cf11.jpg", "categories": ["Italy Bracelet", "Flag"], "subcategory": "Football"},
    {"id": 2012, "name_kh": "Flag Charm 12", "price": 3000, "image": "/static/images/cf12.jpg", "categories": ["Italy Bracelet", "Flag"], "subcategory": "Football"},
    {"id": 2013, "name_kh": "Flag Charm 13", "price": 3000, "image": "/static/images/cf13.jpg", "categories": ["Italy Bracelet", "Flag"], "subcategory": "Football"},
    {"id": 2014, "name_kh": "Flag Charm 14", "price": 3000, "image": "/static/images/cf14.jpg", "categories": ["Italy Bracelet", "Flag"], "subcategory": "Football"},
    {"id": 2015, "name_kh": "Flag Charm 15", "price": 3000, "image": "/static/images/cf15.jpg", "categories": ["Italy Bracelet", "Flag"], "subcategory": "Football"},
    {"id": 2016, "name_kh": "Flag Charm 16", "price": 3000, "image": "/static/images/cf16.jpg", "categories": ["Italy Bracelet", "Flag"], "subcategory": "Football"},
    {"id": 2017, "name_kh": "Flag Charm 17", "price": 3000, "image": "/static/images/cf17.jpg", "categories": ["Italy Bracelet", "Flag"], "subcategory": "Football"},
    {"id": 2018, "name_kh": "Flag Charm 18", "price": 3000, "image": "/static/images/cf18.jpg", "categories": ["Italy Bracelet", "Flag"], "subcategory": "Football"},
    {"id": 2019, "name_kh": "Flag Charm 19", "price": 3000, "image": "/static/images/cf19.jpg", "categories": ["Italy Bracelet", "Flag"], "subcategory": "Football"},
]

# --- DATABASE MODEL ---
class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name_kh = db.Column(db.String(200), nullable=False)
    price = db.Column(db.Integer, nullable=False)
    image = db.Column(db.String(500), nullable=False)
    categories_str = db.Column(db.String(500), default="") 
    subcategory_str = db.Column(db.String(500), default="") 
    stock = db.Column(db.Integer, default=0)

# --- SYNC ENGINE ---
def sync_catalog():
    try:
        # Check if table exists to avoid crash
        inspector = db.inspect(db.engine)
        if not inspector.has_table("product"):
            db.create_all()
            
        print("🔄 Syncing Catalog...")
        for item in PRODUCT_CATALOG:
            existing = Product.query.get(item['id'])
            cat_str = ", ".join(item.get('categories', []))
            sub_str = item.get('subcategory', 'General')
            
            if existing:
                existing.name_kh = item['name_kh']
                existing.price = item['price']
                existing.image = item['image']
                existing.categories_str = cat_str
                existing.subcategory_str = sub_str
            else:
                new_p = Product(
                    id=item['id'],
                    name_kh=item['name_kh'],
                    price=item['price'],
                    image=item['image'],
                    categories_str=cat_str,
                    subcategory_str=sub_str,
                    stock=0
                )
                db.session.add(new_p)
        db.session.commit()
        print("✅ Sync Complete!")
    except Exception as e:
        print(f"⚠️ Database Error (Ignored to keep app alive): {e}")

# --- ROUTES ---
@app.route('/')
def home():
    return redirect(url_for('custom_bracelet'))

@app.route('/custom-bracelet')
def custom_bracelet():
    try:
        all_products = Product.query.all()
        products_json = [{
            "id": p.id, "name_kh": p.name_kh, "price": p.price, 
            "image": p.image, "stock": p.stock, 
            "categories": p.categories_str.split(', ')
        } for p in all_products]
    except:
        products_json = [] # Fallback if DB fails
    
    is_admin = session.get('admin', False)
    return render_template('custom_bracelet.html', products=products_json, is_admin=is_admin)

@app.route('/admin/panel')
def admin_panel():
    if not session.get('admin'): return redirect(url_for('admin_login'))
    
    all_products = Product.query.all()
    stats = {
        "total": len(all_products),
        "out": len([p for p in all_products if p.stock <= 0]),
        "low": len([p for p in all_products if 0 < p.stock <= 5])
    }
    
    grouped = {}
    for p in all_products:
        sub = p.subcategory_str if p.subcategory_str else "General"
        if sub not in grouped: grouped[sub] = []
        grouped[sub].append(p)
        
    return render_template('admin_panel.html', grouped=grouped, stats=stats)

@app.route('/admin/api/update-stock', methods=['POST'])
def update_stock():
    if not session.get('admin'): return jsonify({"success": False}), 403
    data = request.json
    p = Product.query.get(data['id'])
    if p:
        p.stock = int(data['amount'])
        db.session.commit()
        return jsonify({"success": True})
    return jsonify({"success": False})

@app.route('/admin/api/sell-items', methods=['POST'])
def sell_items():
    if not session.get('admin'): return jsonify({"success": False, "msg": "Unauthorized"}), 403
    data = request.json
    ids = data.get('ids', [])
    for pid in ids:
        p = Product.query.get(pid)
        if p and p.stock > 0:
            p.stock -= 1
    db.session.commit()
    return jsonify({"success": True})

@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        if request.form['username'] == ADMIN_USER and request.form['password'] == ADMIN_PASS:
            session['admin'] = True
            return redirect(url_for('admin_panel'))
    return render_template('admin_login.html')

@app.route('/admin/logout')
def logout():
    session.pop('admin', None)
    return redirect(url_for('admin_login'))

# --- INIT & RUN ---
with app.app_context():
    try:
        db.create_all()
        sync_catalog()
    except:
        pass

if __name__ == '__main__':
    # CRITICAL FIX FOR RENDER: Bind to 0.0.0.0 and use PORT env var
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port, debug=True)



