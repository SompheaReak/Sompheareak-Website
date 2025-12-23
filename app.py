import os
from flask import Flask, render_template, request, redirect, url_for, jsonify, session
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.secret_key = 'somphea_reak_studio_key'

# --- DATABASE SETUP ---
basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'shop.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name_kh = db.Column(db.String(200), nullable=False)
    price = db.Column(db.Integer, nullable=False)
    image = db.Column(db.String(500), nullable=False)
    categories_str = db.Column(db.String(500), default="") 
    subcategory_str = db.Column(db.String(500), default="") 
    stock = db.Column(db.Integer, default=10) # Manage this from Admin

# --- DATA IMPORT LOGIC ---
def seed_database():
    """Import your list from the file into the database"""
    if Product.query.first(): return # Stop if already imported
    
    # PASTE YOUR ENTIRE LIST OF CHARMS HERE
    catalog = [
        {"id": 1101, "name_kh": "Letter Charm A", "price": 1200, "image": "/static/images/a.jpg", "categories": ["Letter", "Italy Bracelet"], "subcategory": "Silver/Gold Letters"},
        {"id": 1102, "name_kh": "Letter Charm B", "price": 1200, "image": "/static/images/b.jpg", "categories": ["Letter", "Italy Bracelet"], "subcategory": "Silver/Gold Letters"},
        # ... Add the rest of your hundreds of lines here ...
    ]

    for item in catalog:
        # Check if Italy Bracelet is in categories to ensure it shows in studio
        cats = ", ".join(item['categories'])
        sub = item.get('subcategory', 'General')
        
        new_product = Product(
            id=item['id'],
            name_kh=item['name_kh'],
            price=item['price'],
            image=item['image'],
            categories_str=cats,
            subcategory_str=sub,
            stock=10 # Initial stock value
        )
        db.session.add(new_product)
    
    db.session.commit()
    print("✅ All charms imported to Database!")

# --- ROUTES ---

@app.route('/custom-bracelet')
def custom_bracelet():
    # Fetch charms and pass to Studio
    charms_db = Product.query.filter(Product.categories_str.contains('Italy Bracelet')).all()
    charms_list = []
    for c in charms_db:
        charms_list.append({
            "id": c.id, "name_kh": c.name_kh, "price": c.price, 
            "image": c.image, "stock": c.stock,
            "categories": [cat.strip() for cat in c.categories_str.split(',')]
        })
    return render_template('custom_bracelet.html', charms_json=charms_list)

@app.route('/admin/products')
def admin_products():
    # Group products by subcategory for easy scrolling
    all_p = Product.query.all()
    grouped = {}
    for p in all_p:
        sub = p.subcategory_str if p.subcategory_str else "General"
        if sub not in grouped: grouped[sub] = []
        grouped[sub].append(p)
    return render_template('admin_products.html', grouped=grouped)

@app.route('/admin/update-stock', methods=['POST'])
def update_stock():
    data = request.json
    p = Product.query.get(data.get('id'))
    if p:
        p.stock = int(data.get('amount'))
        db.session.commit()
        return jsonify({"success": True})
    return jsonify({"success": False})

@app.route('/api/deduct-stock', methods=['POST'])
def deduct_stock():
    """Call this from JS when design is saved"""
    data = request.json
    for pid in data.get('ids', []):
        p = Product.query.get(pid)
        if p and p.stock > 0: p.stock -= 1
    db.session.commit()
    return jsonify({"success": True})

with app.app_context():
    db.create_all()
    seed_database()

if __name__ == '__main__':
    app.run(debug=True)

