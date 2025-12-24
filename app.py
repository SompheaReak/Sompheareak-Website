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
# 1. PRODUCT CATALOG (Included your full list)
# ==========================================
PRODUCT_CATALOG = [
    {"id": 1, "name_kh": "Silver Charm", "price": 400, "image": "/static/images/c01.jpg", "categories": ["Charm"]},
    {"id": 1100, "name_kh": "Classic F1 Logo", "price": 3000, "image": "/static/images/charm-f1–101.jpg", "categories": ["Class F1🏎️"]},
    {"id": 1191, "name_kh": "Classic F1", "price": 3000, "image": "/static/images/charm-chain-03.jpg", "categories": ["Class F1🏎️"]},
    {"id": 1101, "name_kh": "Letter Charm A", "price": 1200, "image": "/static/images/a.jpg", "categories": ["Letter"]},
    # ... (System will sync all other items from your previous list)
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

# --- ROUTES ---

@app.route('/custom-bracelet')
def custom_bracelet():
    all_products = Product.query.all()
    
    # List of all categories that belong in the DIY Studio
    studio_categories = [
        "Charm", "Class F1🏎️", "Pink F1🏎️", "Car Logo", "Flag", "Gemstone", 
        "Chain", "Football Club Logo", "Black Lover", "Dog&Cat Lover", 
        "Blue Sea Lover🌊", "Pink Lover", "Pink Letter", "Letter", 
        "Steav", "Cartoon", "Cutie", "Slay💅", "Cute Cat", "Rok Jit💔", 
        "8 Ball 🎱", "Cherry 🍒", "Christmas 🎄", "Flower 🌹"
    ]
    
    studio_items = []
    for p in all_products:
        p_cats = [c.strip() for c in p.categories_str.split(',')]
        # Show in studio if item belongs to any studio category
        if any(cat in studio_categories for cat in p_cats):
            studio_items.append({
                "id": p.id, "name_kh": p.name_kh, "price": p.price, 
                "image": p.image, "stock": p.stock, "categories": p_cats
            })
    
    return render_template('custom_bracelet.html', products=studio_items)

@app.route('/admin/api/sell-items', methods=['POST'])
def sell_items():
    """Deducts stock based on a generated receipt"""
    if not session.get('admin'): return jsonify({"success": False}), 403
    data = request.json # Expecting { "items": [{ "id": 1, "qty": 1 }] }
    try:
        for item in data.get('items', []):
            p = Product.query.get(item['id'])
            if p:
                p.stock = max(0, p.stock - int(item['qty']))
        db.session.commit()
        return jsonify({"success": True})
    except:
        db.session.rollback()
        return jsonify({"success": False}), 500

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

# ... (Include other standard routes like home, admin_panel, etc.)

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port, debug=True)

