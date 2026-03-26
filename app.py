import os
import json
from flask import Flask, render_template, request, redirect, url_for, jsonify, session, flash
from flask_sqlalchemy import SQLAlchemy
import cloudinary
import cloudinary.uploader

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'somphea_reak_final_pro_2025')

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
    price = db.Column(db.Float, nullable=False)
    stock = db.Column(db.Integer, default=1) 
    image = db.Column(db.String(500), nullable=False) 
    category = db.Column(db.String(100), nullable=False)
    store = db.Column(db.String(50), nullable=False) 
    variants = db.Column(db.Text, nullable=True) 

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
    unique_cats = db.session.query(Product.category).distinct().all()
    categories = [c[0] for c in unique_cats]
    return render_template('admin_panel.html', products=products, categories=categories)

# --- 5. THE FULL UPDATE ROUTE ---
@app.route('/admin/product/update/<int:id>', methods=['POST'])
def update_product(id):
    if not session.get('admin'): return redirect(url_for('login'))
    p = Product.query.get_or_404(id)
    
    # Update main info
    p.title = request.form.get('title')
    p.price = float(request.form.get('price'))
    p.stock = int(request.form.get('stock'))
    p.category = request.form.get('category')
    p.store = request.form.get('store')
    
    # Update variants prices to match the new main price
    vars_list = json.loads(p.variants)
    for v in vars_list:
        v['price'] = p.price
    p.variants = json.dumps(vars_list)
    
    db.session.commit()
    flash('Product Updated Successfully!', 'success')
    return redirect(url_for('admin_panel'))

@app.route('/admin/product/add', methods=['POST'])
def add_product():
    if not session.get('admin'): return redirect(url_for('login'))
    
    title = request.form.get('title')
    stock = int(request.form.get('stock', 0))
    category = request.form.get('category')
    store = request.form.get('store')
    v_names = request.form.getlist('variant_names[]')
    v_prices = request.form.getlist('variant_prices[]')
    files = request.files.getlist('images')
    
    uploaded_urls = []
    for f in files:
        if f and f.filename != '':
            res = cloudinary.uploader.upload(f)
            uploaded_urls.append(res['secure_url'])
            
    if uploaded_urls:
        main_p = float(v_prices[0]) if v_prices else 0
        vars_json = [{"id": i, "name": v_names[i] if i < len(v_names) else f"Option {i+1}", "price": float(v_prices[i]) if i < len(v_prices) else main_p, "image": url} for i, url in enumerate(uploaded_urls)]
        
        new_p = Product(title=title, price=main_p, stock=stock, image=uploaded_urls[0], category=category, store=store, variants=json.dumps(vars_json))
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

