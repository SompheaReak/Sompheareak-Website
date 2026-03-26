import os
import json
from werkzeug.utils import secure_filename
from flask import Flask, render_template, request, redirect, url_for, jsonify, session, flash
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.secret_key = 'somphea_reak_studio_pro_2025'

# --- 1. CONFIGURATION ---
basedir = os.path.abspath(os.path.dirname(__file__))
# Changed to shop_v3.db so it creates a fresh, clean database for the new system
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'shop_v3.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Image Upload Settings
UPLOAD_FOLDER = os.path.join(basedir, 'static', 'uploads')
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

db = SQLAlchemy(app)

# --- 2. CONSTANTS ---
ADMIN_PASS = 'Thesong_Admin@2022?!$'

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# --- 3. MODELS ---
class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    price = db.Column(db.Float, nullable=False)
    image = db.Column(db.String(500), nullable=False)
    category = db.Column(db.String(100), nullable=False)
    store = db.Column(db.String(50), nullable=False) # 'toy' or 'bracelet'
    variants = db.Column(db.Text, nullable=True) # JSON string for advanced variants

# --- 4. PUBLIC ROUTES (Your Website) ---
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/custom-bracelet')
def custom_bracelet():
    return render_template('custom_bracelet.html')

@app.route('/bracelet')
def shop():
    return render_template('bracelet.html')

@app.route('/toy-universe')
def toy_universe():
    return render_template('toy.html')

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
    if not session.get('admin'): 
        return redirect(url_for('admin_login'))
    
    products = Product.query.order_by(Product.id.desc()).all()
    return render_template('admin_panel.html', products=products)

@app.route('/admin/product/add', methods=['POST'])
def add_product():
    if not session.get('admin'): return redirect(url_for('admin_login'))
    
    title = request.form.get('title')
    price = float(request.form.get('price', 0))
    category = request.form.get('category')
    store = request.form.get('store')
    
    # Handle Image Upload
    if 'image' not in request.files:
        flash('No image uploaded', 'error')
        return redirect(url_for('admin_panel'))
        
    file = request.files['image']
    if file.filename == '':
        flash('No selected file', 'error')
        return redirect(url_for('admin_panel'))
        
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        # Add a unique prefix so files with the same name don't overwrite
        import uuid
        unique_filename = f"{uuid.uuid4().hex[:8]}_{filename}"
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], unique_filename))
        image_url = f"static/uploads/{unique_filename}"
        
        # Create default variant matching the parent product
        default_variant = [{"id": f"v1", "name": "Standard", "price": price, "image": image_url}]
        
        new_product = Product(
            title=title, 
            price=price, 
            image=image_url, 
            category=category, 
            store=store,
            variants=json.dumps(default_variant)
        )
        db.session.add(new_product)
        db.session.commit()
        flash('Product added successfully!', 'success')
        
    return redirect(url_for('admin_panel'))

@app.route('/admin/product/delete/<int:id>', methods=['POST'])
def delete_product(id):
    if not session.get('admin'): return redirect(url_for('admin_login'))
    product = Product.query.get_or_404(id)
    
    # Try to delete the image file from server to save space
    try:
        os.remove(os.path.join(basedir, product.image))
    except:
        pass # If file doesn't exist, just ignore
        
    db.session.delete(product)
    db.session.commit()
    flash('Product deleted!', 'success')
    return redirect(url_for('admin_panel'))

# --- 6. API FOR YOUR HTML PAGES ---
@app.route('/api/products/<store_name>')
def get_store_products(store_name):
    """Your toy.html and bracelet.html will call this to get their items!"""
    products = Product.query.filter_by(store=store_name).all()
    output = []
    for p in products:
        output.append({
            "id": p.id,
            "title": p.title,
            "sold": "New",
            "category": p.category,
            "thumbnail": p.image,
            "variants": json.loads(p.variants) if p.variants else []
        })
    return jsonify(output)

# Initialize Database
with app.app_context():
    db.create_all()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))

