import os
from flask import Flask, render_template, request, redirect, url_for, jsonify, session
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.secret_key = 'somphea_reak_ultimate_2025'

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
    # --- Charm
    {"id": 1, "name_kh": "Silver Charm", "price": 400, "image": "/static/images/c01.jpg", "categories": ["Charm"]},
   
    # --- F1 LOGOS ---
    {"id": 1100, "name_kh": "Classic F1 Logo", "price": 3000, "image": "/static/images/charm-f1–101.jpg", "categories": ["Class F1🏎️"]},
    {"id": 1191, "name_kh": "Classic F1", "price": 3000, "image": "/static/images/charm-chain-03.jpg", "categories": ["Class F1🏎️"]},
    {"id": 1192, "name_kh": "Classic F1 - Ferri", "price": 3000, "image": "/static/images/charm-f1-301.jpg", "categories": ["Class F1🏎️"]},
    {"id": 1193, "name_kh": "Classic F1 - Porsche", "price": 3000, "image": "/static/images/charm-f1-302.jpg", "categories": ["Class F1🏎️"]},
    {"id": 1194, "name_kh": "Classic F1 - BMW", "price": 3000, "image": "/static/images/charm-f1-303.jpg", "categories": ["Class F1🏎️"]},
    {"id": 1195, "name_kh": "Classic F1 - BMW", "price": 3000, "image": "/static/images/charm-f1-304.jpg", "categories": ["Class F1🏎️"]},
    {"id": 1101, "name_kh": "Classic F1 - Mercedes", "price": 3000, "image": "/static/images/cc15.jpg", "categories": ["Class F1🏎️"]},
    {"id": 1102, "name_kh": "Classic F1 - Ferrari", "price": 3000, "image": "/static/images/cc04.jpg", "categories": ["Class F1🏎️"]},
    {"id": 1103, "name_kh": "Classic F1 - Porsche", "price": 3000, "image": "/static/images/cc12.jpg", "categories": ["Class F1🏎️"]},
    {"id": 1104, "name_kh": "Classic F1 - BMW", "price": 3000, "image": "/static/images/cc06.jpg", "categories": ["Class F1🏎️"]},

    # --- Pink F1 ---
    {"id": 1200, "name_kh": "Pink F1 Logo", "price": 3000, "image": "/static/images/charm-f1-201.jpg", "categories": ["Pink F1🏎️"]},
    {"id": 1291, "name_kh": "Pink F1 - Mercedes", "price": 3000, "image": "/static/images/charm-chain-03.jpg", "categories": ["Pink F1🏎️"]},
    {"id": 1292, "name_kh": "Pink F1 - Ferri", "price": 3000, "image": "/static/images/charm-f1-301.jpg", "categories": ["Pink F1🏎️"]},
    {"id": 1293, "name_kh": "Pink F1 - Porsche", "price": 3000, "image": "/static/images/charm-f1-302.jpg", "categories": ["Pink F1🏎️"]},
    {"id": 1294, "name_kh": "Pink F1 - BMW", "price": 3000, "image": "/static/images/charm-f1-303.jpg", "categories": ["Pink F1🏎️"]},
    {"id": 1295, "name_kh": "Pink F1 - BMW", "price": 3000, "image": "/static/images/charm-f1-304.jpg", "categories": ["Pink F1🏎️"]},
    {"id": 1201, "name_kh": "Pink F1 - Mercedes", "price": 3000, "image": "/static/images/charm-f1-202.jpg", "categories": ["Pink F1🏎️"]},
    {"id": 1202, "name_kh": "Pink F1 - Ferrari", "price": 3000, "image": "/static/images/charm-f1-203.jpg", "categories": ["Pink F1🏎️"]},
    {"id": 1203, "name_kh": "Pink F1 - Porsche", "price": 3000, "image": "/static/images/charm-f1-204.jpg", "categories": ["Pink F1🏎️"]},
    {"id": 1204, "name_kh": "Pink F1 - BMW", "price": 3000, "image": "/static/images/charm-f1-205.jpg", "categories": ["Pink F1🏎️"]},

    # --- CAR LOGOS ---
    {"id": 1001, "name_kh": "Car Charm 01", "price": 3000, "image": "/static/images/cc01.jpg", "categories": ["Car Logo"]},
    {"id": 1002, "name_kh": "Car Charm 02", "price": 3000, "image": "/static/images/cc02.jpg", "categories": ["Car Logo"]},
    {"id": 1003, "name_kh": "Car Charm 03", "price": 3000, "image": "/static/images/cc03.jpg", "categories": ["Car Logo"]},
    {"id": 1004, "name_kh": "Car Charm 04", "price": 3000, "image": "/static/images/cc04.jpg", "categories": ["Car Logo"]},
    {"id": 1005, "name_kh": "Car Charm 05", "price": 3000, "image": "/static/images/cc05.jpg", "categories": ["Car Logo"]},
    {"id": 1006, "name_kh": "Car Charm 06", "price": 3000, "image": "/static/images/cc06.jpg", "categories": ["Car Logo"]},
    {"id": 1007, "name_kh": "Car Charm 07", "price": 3000, "image": "/static/images/cc07.jpg", "categories": ["Car Logo"]}, 
    {"id": 1008, "name_kh": "Car Charm 08", "price": 3000, "image": "/static/images/cc08.jpg", "categories": ["Car Logo"]},
    {"id": 1009, "name_kh": "Car Charm 09", "price": 3000, "image": "/static/images/cc09.jpg", "categories": ["Car Logo"]},
    {"id": 1010, "name_kh": "Car Charm 10", "price": 3000, "image": "/static/images/cc10.jpg", "categories": ["Car Logo"]},
    {"id": 1011, "name_kh": "Car Charm 11", "price": 3000, "image": "/static/images/cc11.jpg", "categories": ["Car Logo"]},
    {"id": 1012, "name_kh": "Car Charm 12", "price": 3000, "image": "/static/images/cc12.jpg", "categories": ["Car Logo"]},
    {"id": 1013, "name_kh": "Car Charm 13", "price": 3000, "image": "/static/images/cc13.jpg", "categories": ["Car Logo"]},
    {"id": 1014, "name_kh": "Car Charm 14", "price": 3000, "image": "/static/images/cc14.jpg", "categories": ["Car Logo"]},
    {"id": 1015, "name_kh": "Car Charm 15", "price": 3000, "image": "/static/images/cc15.jpg", "categories": ["Car Logo"]},

    # --- FLAGS ---
    *[{"id": 2000 + i, "name_kh": f"Flag Charm {i:02d}", "price": 3000, "image": f"/static/images/cf{i:02d}.jpg", "categories": ["Flag"], "subcategory": "Football"} for i in range(1, 20)],

    # --- GEMSTONES ---
    *[{"id": 3000 + i, "name_kh": f"Gemstone Charm {i:02d}", "price": 3500 if i < 21 else 5000, "image": f"/static/images/cg{i:02d}.jpg", "categories": ["Gemstone"]} for i in range(1, 25)],

    # --- CHAINS ---
    *[{"id": 4000 + i, "name_kh": f"Chain Charm {i:02d}", "price": 3000, "image": f"/static/images/charm-chain-{i:02d}.jpg", "categories": ["Chain"]} for i in range(1, 17)],

    # --- FOOTBALL CLUBS ---
    {"id": 5001, "name_kh": "Barcelona", "price": 3000, "image": "/static/images/charm-footballclub-01.jpg", "categories": ["Football Club Logo"]},
    {"id": 5002, "name_kh": "Real Madrid", "price": 3000, "image": "/static/images/charm-footballclub-02.jpg", "categories": ["Football Club Logo"]},
    # ... (Simplified range for space, can be expanded exactly like above)

    # --- THEMED LOVERS ---
    *[{"id": 6000 + i, "name_kh": f"Black Charm {i:02d}", "price": 3000, "image": f"/static/images/cb{i:02d}.jpg", "categories": ["Black Lover"]} for i in range(1, 8)],
    *[{"id": 7000 + i, "name_kh": f"Cat&Dog Charm {i:02d}", "price": 3000, "image": f"/static/images/charm-animal-{i:02d}.jpg", "categories": ["Dog&Cat Lover"]} for i in range(1, 8)],
    *[{"id": 7010 + i, "name_kh": f"Blue Sea Lover {i:02d}", "price": 3000, "image": f"/static/images/charm-bluesealover-{i:02d}.jpg", "categories": ["Blue Sea Lover🌊"]} for i in range(1, 16)],
    *[{"id": 8000 + i, "name_kh": f"Pink Charm {i:02d}", "price": 3000, "image": f"/static/images/cp{i:02d}.jpg", "categories": ["Pink Lover"]} for i in range(1, 10)],

    # --- LETTERS ---
    *[{"id": 9000 + i, "name_kh": f"Pink Letter {chr(64+i)}", "price": 1200, "image": f"/static/images/{chr(96+i)}p.jpg", "categories": ["Pink Letter"]} for i in range(1, 27)],
    *[{"id": 1100 + i, "name_kh": f"Letter {chr(64+i)}", "price": 1200, "image": f"/static/images/{chr(96+i)}.jpg", "categories": ["Letter"]} for i in range(1, 27)],

    # --- HOLIDAYS & OTHERS ---
    *[{"id": 2000 + i, "name_kh": f"Christmas 🎄 {i:02d}", "price": 3000, "image": f"/static/images/charm-christmas-{i:02d}.jpg", "categories": ["Christmas 🎄"]} for i in range(1, 30)],
    *[{"id": 2100 + i, "name_kh": f"Flower 🌹 {i:02d}", "price": 3000, "image": f"/static/images/charm-flower-{i:02d}.jpg", "categories": ["Flower 🌹"]} for i in range(1, 10)],
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
        inspector = db.inspect(db.engine)
        if not inspector.has_table("product"): db.create_all()
        for item in PRODUCT_CATALOG:
            existing = Product.query.get(item['id'])
            cat_str = ", ".join(item.get('categories', []))
            sub_str = str(item.get('subcategory', 'General'))
            if existing:
                existing.name_kh = item['name_kh']
                existing.price = item['price']
                existing.image = item['image']
                existing.categories_str = cat_str
                existing.subcategory_str = sub_str
            else:
                new_p = Product(id=item['id'], name_kh=item['name_kh'], price=item['price'], image=item['image'], categories_str=cat_str, subcategory_str=sub_str, stock=0)
                db.session.add(new_p)
        db.session.commit()
    except Exception as e:
        print(f"⚠️ DB Error: {e}")

# --- ROUTES ---

@app.route('/admin/panel')
def admin_panel():
    if not session.get('admin'): return redirect(url_for('admin_login'))
    all_products = Product.query.all()
    stats = {"total": len(all_products), "out": len([p for p in all_products if p.stock <= 0]), "low": len([p for p in all_products if 0 < p.stock <= 5])}
    grouped = {}
    for p in all_products:
        cat = p.categories_str.split(', ')[0] if p.categories_str else "Uncategorized"
        if cat not in grouped: grouped[cat] = []
        grouped[cat].append(p)
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

@app.route('/admin/api/process-receipt', methods=['POST'])
def process_receipt():
    """Finalizes receipt and automatically decreases stock levels"""
    if not session.get('admin'): return jsonify({"success": False}), 403
    data = request.json # Expecting { "items": [{ "id": 1100, "qty": 1 }, ...] }
    try:
        for item in data.get('items', []):
            p = Product.query.get(item['id'])
            if p:
                p.stock = max(0, p.stock - int(item['qty']))
        db.session.commit()
        return jsonify({"success": True})
    except Exception as e:
        db.session.rollback()
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        if request.form['username'] == ADMIN_USER and request.form['password'] == ADMIN_PASS:
            session['admin'] = True
            return redirect(url_for('admin_panel'))
    return render_template('admin_login.html')

with app.app_context():
    sync_catalog()

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port, debug=True)

