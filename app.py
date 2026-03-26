import os
import json
from flask import Flask, render_template, request, redirect, url_for, jsonify, session, flash
from flask_sqlalchemy import SQLAlchemy
import cloudinary
import cloudinary.uploader
import cloudinary.api

app = Flask(__name__)
# Secure secret key from environment or default
app.secret_key = os.environ.get('SECRET_KEY', 'somphea_reak_studio_pro_2025')

# --- 1. SECURE CLOUDINARY CONFIGURATION ---
# Fetches keys securely from your Render Environment Variables
cloudinary.config( 
  cloud_name = "dwwearehy", 
  api_key = os.environ.get("CLOUDINARY_API_KEY"), 
  api_secret = os.environ.get("CLOUDINARY_API_SECRET"),
  secure = True
)

# --- 2. SECURE DATABASE CONFIGURATION (NEON CLOUD) ---
# Fetches the Database URL securely from Render
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'sqlite:///fallback.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
# Your Admin Password
ADMIN_PASS = 'Thesong_Admin@2022?!$'

# --- 3. DATABASE MODEL ---
class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    price = db.Column(db.Float, nullable=False)
    stock = db.Column(db.Integer, default=1) 
    image = db.Column(db.String(500), nullable=False) # Main Thumbnail URL
    category = db.Column(db.String(100), nullable=False)
    store = db.Column(db.String(50), nullable=False) 
    variants = db.Column(db.Text, nullable=True) # Stores all 10 images as JSON

# --- 4. ROUTES ---
@app.route('/')
def index(): return render_template('index.html')

@app.route('/custom-bracelet')
def custom_bracelet(): return render_template('custom_bracelet.html')

@app.route('/bracelet')
def shop(): return render_template('bracelet.html')

@app.route('/toy-universe')
def toy_universe(): return render_template('toy.html')

# --- 5. ADMIN DASHBOARD LOGIC ---
@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        if request.form.get('password') == ADMIN_PASS:
            session['admin'] = True
            return redirect(url_for('admin_panel'))
        else:
            flash("Invalid Password", "error")
    return render_template('admin_login.html')

@app.route('/admin/logout')
def admin_logout():
    session.pop('admin', None)
    return redirect(url_for('admin_login'))

@app.route('/admin/panel')
def admin_panel():
    if not session.get('admin'): return redirect(url_for('admin_login'))
    products = Product.query.order_by(Product.id.desc()).all()
    return render_template('admin_panel.html', products=products)

@app.route('/admin/product/add', methods=['POST'])
def add_product():
    if not session.get('admin'): return redirect(url_for('admin_login'))
    
    title = request.form.get('title')
    price = float(request.form.get('price', 0))
    stock = int(request.form.get('stock', 1)) 
    category = request.form.get('category')
    store = request.form.get('store')
    
    # Receive up to 10 images
    files = request.files.getlist('images')
    if not files or files[0].filename == '':
        flash('No image selected', 'error')
        return redirect(url_for('admin_panel'))
        
    uploaded_urls = []
    
    # Upload each file to Cloudinary
    for file in files:
        if file and file.filename != '':
            try:
                upload_result = cloudinary.uploader.upload(file)
                uploaded_urls.append(upload_result['secure_url'])
            except Exception as e:
                print("Upload Error:", e)
            
    if not uploaded_urls:
        flash('Upload failed. Check your Cloudinary keys in Render.', 'error')
        return redirect(url_for('admin_panel'))
        
    main_thumbnail = uploaded_urls[0] 
    
    # Prepare the gallery JSON
    variants_list = []
    for i, url in enumerate(uploaded_urls):
        variants_list.append({
            "id": f"v{i+1}",
            "name": f"View {i+1}",
            "price": price,
            "image": url
        })
        
    new_product = Product(
        title=title, price=price, stock=stock, image=main_thumbnail, 
        category=category, store=store, variants=json.dumps(variants_list)
    )
    db.session.add(new_product)
    db.session.commit()
    flash(f'Product added with {len(uploaded_urls)} images!', 'success')
        
    return redirect(url_for('admin_panel'))

@app.route('/admin/product/delete/<int:id>', methods=['POST'])
def delete_product(id):
    if not session.get('admin'): return redirect(url_for('admin_login'))
    product = Product.query.get_or_404(id)
    db.session.delete(product)
    db.session.commit()
    flash('Product deleted!', 'success')
    return redirect(url_for('admin_panel'))

# --- 6. API FOR THE WEBSITE ---
@app.route('/api/products/<store_name>')
def get_store_products(store_name):
    products = Product.query.filter_by(store=store_name).order_by(Product.id.desc()).all()
    output = []
    for p in products:
        output.append({
            "id": p.id, "title": p.title, "sold": f"{p.stock} left", 
            "category": p.category, "thumbnail": p.image, 
            "variants": json.loads(p.variants) if p.variants else []
        })
    return jsonify(output)

# Create tables in Neon if they don't exist
with app.app_context():
    db.create_all()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))

