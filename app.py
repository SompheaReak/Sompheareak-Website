import os
import json
from flask import Flask, render_template, request, redirect, url_for, jsonify, session, flash
from flask_sqlalchemy import SQLAlchemy
import cloudinary
import cloudinary.uploader

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'somphea_reak_enterprise_2025')

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

# --- 3. MODEL ---
class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    price = db.Column(db.Float, nullable=False) # Base display price
    stock = db.Column(db.Integer, default=0) # Total stock (sum of variants)
    image = db.Column(db.String(500), nullable=False) 
    category = db.Column(db.String(100), nullable=False)
    store = db.Column(db.String(50), nullable=False) 
    variants = db.Column(db.Text, nullable=True) # JSON: [{"name": "", "price": 0, "stock": 0, "image": ""}]

# --- 4. ROUTES ---
@app.route('/')
def index(): return render_template('index.html')

@app.route('/toy-universe')
def toy_universe(): return render_template('toy.html')

@app.route('/bracelet')
def shop(): return render_template('bracelet.html')

@app.route('/admin/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST' and request.form.get('password') == ADMIN_PASS:
        session['admin'] = True
        return redirect(url_for('admin_panel'))
    return render_template('admin_login.html')

@app.route('/admin/panel')
def admin_panel():
    if not session.get('admin'): return redirect(url_for('login'))
    products = Product.query.order_by(Product.id.desc()).all()
    for p in products:
        p.parsed_variants = json.loads(p.variants) if p.variants else []
    unique_cats = db.session.query(Product.category).distinct().all()
    categories = [c[0] for c in unique_cats]
    return render_template('admin_panel.html', products=products, categories=categories)

# --- 5. THE ENTERPRISE UPDATE ROUTE (Variants + New Images) ---
@app.route('/admin/product/update/<int:id>', methods=['POST'])
def update_product(id):
    if not session.get('admin'): return redirect(url_for('login'))
    p = Product.query.get_or_404(id)
    
    p.title = request.form.get('title')
    p.category = request.form.get('category')
    p.store = request.form.get('store')
    
    # Update existing variants
    v_names = request.form.getlist('v_names[]')
    v_prices = request.form.getlist('v_prices[]')
    v_stocks = request.form.getlist('v_stocks[]')
    
    old_variants = json.loads(p.variants)
    updated_variants = []
    total_stock = 0
    
    for i, old_v in enumerate(old_variants):
        name = v_names[i] if i < len(v_names) else old_v['name']
        price = float(v_prices[i]) if i < len(v_prices) else old_v['price']
        stock = int(v_stocks[i]) if i < len(v_stocks) else old_v.get('stock', 0)
        
        updated_variants.append({
            "id": old_v['id'],
            "image": old_v['image'],
            "name": name,
            "price": price,
            "stock": stock
        })
        total_stock += stock

    # HANDLE ADDING NEW IMAGES TO EXISTING PRODUCT
    new_files = request.files.getlist('new_images')
    if new_files and new_files[0].filename != '':
        last_id = updated_variants[-1]['id'] if updated_variants else 0
        for f in new_files:
            if f and f.filename != '':
                res = cloudinary.uploader.upload(f)
                last_id += 1
                new_v = {
                    "id": last_id,
                    "name": f"New Style {last_id}",
                    "price": updated_variants[0]['price'] if updated_variants else 0,
                    "stock": 1,
                    "image": res['secure_url']
                }
                updated_variants.append(new_v)
                total_stock += 1

    p.variants = json.dumps(updated_variants)
    p.stock = total_stock
    p.price = updated_variants[0]['price'] if updated_variants else 0
    
    db.session.commit()
    flash('Product & Inventory Updated!', 'success')
    return redirect(url_for('admin_panel'))

@app.route('/admin/product/add', methods=['POST'])
def add_product():
    if not session.get('admin'): return redirect(url_for('login'))
    title = request.form.get('title')
    category = request.form.get('category')
    store = request.form.get('store')
    
    v_names = request.form.getlist('variant_names[]')
    v_prices = request.form.getlist('variant_prices[]')
    v_stocks = request.form.getlist('variant_stocks[]')
    files = request.files.getlist('images')
    
    uploaded_urls = []
    for f in files:
        if f and f.filename != '':
            res = cloudinary.uploader.upload(f)
            uploaded_urls.append(res['secure_url'])
            
    if uploaded_urls:
        vars_json = []
        total_stock = 0
        for i, url in enumerate(uploaded_urls):
            price = float(v_prices[i]) if i < len(v_prices) else 0
            stock = int(v_stocks[i]) if i < len(v_stocks) else 0
            vars_json.append({
                "id": i, 
                "name": v_names[i] if i < len(v_names) else f"Style {i+1}", 
                "price": price, 
                "stock": stock,
                "image": url
            })
            total_stock += stock
        
        new_p = Product(title=title, price=vars_json[0]['price'], stock=total_stock, image=uploaded_urls[0], category=category, store=store, variants=json.dumps(vars_json))
        db.session.add(new_p)
        db.session.commit()
    return redirect(url_for('admin_panel'))

@app.route('/admin/product/delete/<int:id>', methods=['POST'])
def delete_product(id):
    if not session.get('admin'): return redirect(url_for('login'))
    p = Product.query.get(id)
    if p:
        db.session.delete(p)
        db.session.commit()
    return redirect(url_for('admin_panel'))

@app.route('/api/products/<store_name>')
def get_api(store_name):
    products = Product.query.filter_by(store=store_name).order_by(Product.id.desc()).all()
    return jsonify([{
        "id": p.id, "title": p.title, "price": p.price, "stock": p.stock, 
        "category": p.category, "thumbnail": p.image, "variants": json.loads(p.variants)
    } for p in products])

with app.app_context():
    db.create_all()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))

