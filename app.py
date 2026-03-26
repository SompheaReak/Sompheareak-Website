import os
import json
from flask import Flask, render_template, request, redirect, url_for, jsonify, session, flash
from flask_sqlalchemy import SQLAlchemy
import cloudinary
import cloudinary.uploader

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'somphea_reak_pro_2025')

# --- 1. CLOUDINARY CONFIG ---
cloudinary.config( 
  cloud_name = "dwwearehy", 
  api_key = os.environ.get("CLOUDINARY_API_KEY"), 
  api_secret = os.environ.get("CLOUDINARY_API_SECRET"),
  secure = True
)

# --- 2. DATABASE CONFIG ---
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'sqlite:///fallback.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
ADMIN_PASS = 'Thesong_Admin@2022?!$'

class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    price = db.Column(db.Float, nullable=False) # Base price
    stock = db.Column(db.Integer, default=1) 
    image = db.Column(db.String(500), nullable=False) 
    category = db.Column(db.String(100), nullable=False)
    store = db.Column(db.String(50), nullable=False) 
    variants = db.Column(db.Text, nullable=True) 

# --- PUBLIC ROUTES ---
@app.route('/')
def index(): return render_template('index.html')

@app.route('/toy-universe')
def toy_universe(): return render_template('toy.html')

@app.route('/bracelet')
def shop(): return render_template('bracelet.html')

@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST' and request.form.get('password') == ADMIN_PASS:
        session['admin'] = True
        return redirect(url_for('admin_panel'))
    return render_template('admin_login.html')

@app.route('/admin/logout')
def logout():
    session.pop('admin', None)
    return redirect(url_for('admin_login'))

@app.route('/admin/panel')
def admin_panel():
    if not session.get('admin'): return redirect(url_for('admin_login'))
    products = Product.query.order_by(Product.id.desc()).all()
    unique_cats = db.session.query(Product.category).distinct().all()
    categories = [c[0] for c in unique_cats]
    return render_template('admin_panel.html', products=products, categories=categories)

@app.route('/admin/product/add', methods=['POST'])
def add_product():
    if not session.get('admin'): return redirect(url_for('admin_login'))
    
    title = request.form.get('title')
    stock = int(request.form.get('stock', 0))
    category = request.form.get('category')
    store = request.form.get('store')
    
    # These are lists from the form
    variant_names = request.form.getlist('variant_names[]')
    variant_prices = request.form.getlist('variant_prices[]')
    files = request.files.getlist('images')
    
    uploaded_urls = []
    for file in files:
        if file and file.filename != '':
            res = cloudinary.uploader.upload(file)
            uploaded_urls.append(res['secure_url'])
            
    if not uploaded_urls:
        flash('No images uploaded!', 'error')
        return redirect(url_for('admin_panel'))
        
    # Build the Taobao variant list
    variants_json = []
    base_price = float(variant_prices[0]) if variant_prices else 0
    
    for i, url in enumerate(uploaded_urls):
        name = variant_names[i] if i < len(variant_names) else f"Option {i+1}"
        price = float(variant_prices[i]) if i < len(variant_prices) else base_price
        variants_json.append({
            "id": i,
            "name": name,
            "price": price,
            "image": url
        })
        
    new_p = Product(
        title=title, 
        price=base_price, 
        stock=stock, 
        image=uploaded_urls[0], 
        category=category, 
        store=store, 
        variants=json.dumps(variants_json)
    )
    db.session.add(new_p)
    db.session.commit()
    return redirect(url_for('admin_panel'))

@app.route('/admin/product/delete/<int:id>', methods=['POST'])
def delete(id):
    if not session.get('admin'): return redirect(url_for('admin_login'))
    p = Product.query.get(id)
    if p:
        db.session.delete(p)
        db.session.commit()
    return redirect(url_for('admin_panel'))

@app.route('/api/products/<store_name>')
def api_store(store_name):
    products = Product.query.filter_by(store=store_name).order_by(Product.id.desc()).all()
    return jsonify([{
        "id": p.id, "title": p.title, "price": p.price, "stock": p.stock, 
        "category": p.category, "thumbnail": p.image, "variants": json.loads(p.variants)
    } for p in products])

with app.app_context():
    db.create_all()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))

