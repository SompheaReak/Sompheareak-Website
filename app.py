import os
from flask import Flask, render_template, request, redirect, url_for, jsonify, session
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.secret_key = 'somphea_reak_studio_pro_2025'

# --- DATABASE SETUP ---
basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'shop_v2.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# --- MODELS ---
class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200))
    price = db.Column(db.Integer)
    image = db.Column(db.String(500))
    category = db.Column(db.String(100))
    stock = db.Column(db.Integer, default=0)

# --- ROUTES ---

# 1. HOME PAGE (The Menu)
@app.route('/')
def home():
    return render_template('index.html')

# 2. MEN BRACELET PAGE
@app.route('/men-bracelet')
def men_bracelet():
    # Fetch only Men's Bracelets
    products = Product.query.filter(Product.category.contains("Men")).all()
    return render_template('men_bracelet.html', products=products)

# 3. LEGO PAGE
@app.route('/lego')
def lego():
    products = Product.query.filter(Product.category.contains("LEGO")).all()
    return render_template('lego.html', products=products)

# 4. CUSTOM BRACELET PAGE
@app.route('/custom-bracelet')
def custom_bracelet():
    # You might want to show beads or tools here
    products = Product.query.filter(Product.category.contains("Custom")).all()
    return render_template('custom_bracelet.html', products=products)

# 5. LUCKY DRAW PAGE
@app.route('/lucky-draw')
def lucky_draw():
    return render_template('luckydraw.html')

# 6. EXTRAS (Hot Sale / Toy) - Redirect to home or make new pages if needed
@app.route('/hot-sale')
def hot_sale():
    products = Product.query.filter(Product.category.contains("Hot")).all()
    return render_template('men_bracelet.html', products=products, title="Hot Sale") # Reusing template for simplicity

@app.route('/toy')
def toy():
    products = Product.query.filter(Product.category.contains("Toy")).all()
    return render_template('men_bracelet.html', products=products, title="Toy Collection")

# --- ADMIN ---
@app.route('/admin/login')
def admin_login():
    return render_template('admin_login.html')

# --- SEED DATA (Run once to fix empty DB) ---
def seed_data():
    if Product.query.count() == 0:
        items = [
            Product(name="Obsidian Anchor", price=12000, category="Men Bracelet", stock=10, image="https://images.unsplash.com/photo-1611591437281-460bfbe1220a?w=400"),
            Product(name="Titanium Cuff", price=15000, category="Men Bracelet", stock=5, image="https://images.unsplash.com/photo-1573408301185-9146fe634ad0?w=400"),
            Product(name="Porsche 911 LEGO", price=85000, category="LEGO", stock=2, image="https://images.unsplash.com/photo-1585366119957-e9730b6d0f60?w=400"),
            Product(name="Space Shuttle LEGO", price=120000, category="LEGO", stock=1, image="https://images.unsplash.com/photo-1532330393533-443990a51d10?w=400"),
            Product(name="Gold Bead Set", price=5000, category="Custom", stock=100, image="https://images.unsplash.com/photo-1605100804763-247f67b3557e?w=400"),
        ]
        db.session.add_all(items)
        db.session.commit()
        print("--- DATABASE SEEDED ---")

with app.app_context():
    db.create_all()
    seed_data()

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))


