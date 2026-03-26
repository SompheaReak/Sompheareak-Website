import os
import json
from flask import Flask, render_template, request, redirect, url_for, jsonify, session, flash
from flask_sqlalchemy import SQLAlchemy

# Import Cloudinary
import cloudinary
import cloudinary.uploader
import cloudinary.api

app = Flask(__name__)
app.secret_key = 'somphea_reak_studio_pro_2025'

# --- 1. CLOUDINARY CONFIGURATION ---
# Replace the API Key and Secret with your real ones!
cloudinary.config( 
  cloud_name = "dwwearehy", 
  api_key = "PASTE_YOUR_REAL_API_KEY_HERE", 
  api_secret = "PASTE_YOUR_REAL_API_SECRET_HERE",
  secure = True
)

# --- 2. DATABASE CONFIGURATION (NEON CLOUD) ---
# Your permanent database URL!
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://neondb_owner:npg_dq6KIUVe0cyS@ep-polished-feather-a19qzv4s-pooler.ap-southeast-1.aws.neon.tech/neondb?sslmode=require'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
ADMIN_PASS = 'Thesong_Admin@2022?!$'

# --- 3. MODELS ---
class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    price = db.Column(db.Float, nullable=False)
    stock = db.Column(db.Integer, default=1) 
    image = db.Column(db.String(500), nullable=False) # Cloudinary URL goes here
    category = db.Column(db.String(100), nullable=False)
    store = db.Column(db.String(50), nullable=False) 
    variants = db.Column(db.Text, nullable=True) # JSON of all Cloudinary URLs

# --- 4. PUBLIC ROUTES ---
@app.route('/')
def index(): return render_template('index.html')

@app.route('/custom-bracelet')
def custom_bracelet(): return render_template('custom_bracelet.html')

@app.route('/bracelet')
def shop(): return render_template('bracelet.html')

@app.route('/toy-universe')
def toy_universe(): return render_template('toy.html')

# --- 5. ADMIN SYSTEM ---
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
    
    files = request.files.getlist('images')
    if not files or files[0].filename == '':
        flash('No image uploaded', 'error')
        return redirect(url_for('admin_panel'))
        
    uploaded_urls = []
    
    # Upload images directly to Cloudinary Cloud!
    for file in files:
        if file and file.filename != '':
            try:
                upload_result = cloudinary.uploader.upload(file)
                # Get the permanent secure URL from Cloudinary
                uploaded_urls.append(upload_result['secure_url'])
            except Exception as e:
                print("Cloudinary Upload Error:", e)
            
    if not uploaded_urls:
        flash('Failed to upload images to the cloud.', 'error')
        return redirect(url_for('admin_panel'))
        
    main_thumbnail = uploaded_urls[0] 
    
    variants = []
    for i, url in enumerate(uploaded_urls):
        variants.append({
            "id": f"v{i+1}",
            "name": f"View {i+1}",
            "price": price,
            "image": url
        })
        
    new_product = Product(
        title=title, price=price, stock=stock, image=main_thumbnail, 
        category=category, store=store, variants=json.dumps(variants)
    )
    db.session.add(new_product)
    db.session.commit()
    flash(f'Successfully saved product and {len(uploaded_urls)} images to the Cloud!', 'success')
        
    return redirect(url_for('admin_panel'))

@app.route('/admin/product/delete/<int:id>', methods=['POST'])
def delete_product(id):
    if not session.get('admin'): return redirect(url_for('admin_login'))
    product = Product.query.get_or_404(id)
    db.session.delete(product)
    db.session.commit()
    flash('Product removed from database!', 'success')
    return redirect(url_for('admin_panel'))

# --- 6. APIs ---
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

# Initialize Database
with app.app_context():
    db.create_all()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))


