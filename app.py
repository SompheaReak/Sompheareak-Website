import os 
import requests
from flask import Flask, render_template, request, redirect, url_for, jsonify, session, abort
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.secret_key = 'somphea_reak_shop_secret_key'
app.debug = True

# --- DATABASE SETUP ---
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///shop.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# --- CONFIGURATION ---
ADMIN_USERNAME = 'AdminSompheaReakVitou'
ADMIN_PASSWORD = 'Thesong_Admin@2022?!$'
BOT_TOKEN = "7528700801:AAGTvXjk5qPBnq_qx69ZOW4RMLuGy40w5k8"
CHAT_ID = "-1002654437316"
BANNED_IPS = ['123.45.67.89','45.119.135.70']

# --- DATABASE MODEL ---
class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name_kh = db.Column(db.String(200), nullable=False)
    price = db.Column(db.Integer, nullable=False)
    image = db.Column(db.String(500), nullable=False)
    categories_str = db.Column(db.String(500), default="") # Stores "LEGO,Toy"
    subcategory_str = db.Column(db.String(500), default="") # Stores "Season 1,Season 2"
    stock = db.Column(db.Integer, default=1)

    @property
    def categories(self):
        return self.categories_str.split(',') if self.categories_str else []

    @property
    def subcategory(self):
        return self.subcategory_str.split(',') if self.subcategory_str else []

# --- INITIAL DATA (Runs once to fill database) ---
initial_products = [
    {"id": 101, "name_kh": "NINJAGO Season 1 - DX Suit", "price": 30000, "image": "https://raw.githubusercontent.com/TheSong-Store/static/main/images/njoss1dx.jpg", "categories": "LEGO Ninjago,Toy", "subcategory": "Lego Ninjago,Season 1", "stock": 1},
    {"id": 102, "name_kh": "NINJAGO Season 1 - KAI (DX)", "price": 5000, "image": "https://raw.githubusercontent.com/TheSong-Store/static/main/images/njoss1dxkai.jpg", "categories": "LEGO Ninjago,Toy", "subcategory": "Lego Ninjago,Season 1", "stock": 1},
    {"id": 103, "name_kh": "NINJAGO Season 1 - ZANE (DX)", "price": 5000, "image": "https://raw.githubusercontent.com/TheSong-Store/static/main/images/njoss1dxzane.jpg", "categories": "LEGO Ninjago,Toy", "subcategory": "Lego Ninjago,Season 1", "stock": 1},
]

# --- SUBCATEGORIES MAP ---
subcategories_map = {
    "Hot Sale": [],
    "LEGO Ninjago": ["Dragon Rising","Building Set","Season 1", "Season 2", "Season 3", "Season 4", "Season 5", "Season 6", "Season 7", "Season 8","Season 9","Season 10","Season 11","Season 12","Season 13", "Season 14","Season 15"],
    "LEGO Anime": ["One Piece","Demon Slayer"],
    "Accessories": ["Gym Bracelet", "Gem Stone Bracelet","Dragon Bracelet","Bracelet"],
    "Keychain": ["Gun Keychains"],
    "LEGO": ["Formula 1"],
    "Toy": ["Lego Ninjago", "One Piece","Lego WWII", "Lego ទាហាន"],
    "Italy Bracelet": ["All","Football","Gem","Flag","Chain"],
    "Lucky Draw": ["/lucky-draw"], 
}

# --- HELPER FUNCTIONS ---
def notify_telegram(ip, user_agent):
    try:
        msg = f"📦 *New Visitor*\n*IP:* `{ip}`\n*Device:* `{user_agent}`"
        requests.post(f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage", data={"chat_id": CHAT_ID, "text": msg, "parse_mode": "Markdown"})
    except: pass

@app.before_request
def block_and_notify():
    if request.headers.getlist("X-Forwarded-For"): ip = request.headers.getlist("X-Forwarded-For")[0]
    else: ip = request.remote_addr
    if ip in BANNED_IPS: abort(403)
    if not session.get('notified'):
        notify_telegram(ip, request.headers.get('User-Agent'))
        session['notified'] = True

# --- ROUTES ---
@app.route('/')
def home():
    products = Product.query.all()
    return render_template('home.html', products=products, subcategories=[], current_category=None, cart=session.get('cart', []))

@app.route('/category/<category_name>')
def category(category_name):
    if category_name == 'Lucky Draw': return redirect(url_for('lucky_draw'))
    # Search DB for category string
    products = Product.query.filter(Product.categories_str.contains(category_name)).all()
    return render_template('home.html', products=products, subcategories=subcategories_map.get(category_name, []), current_category=category_name, cart=session.get('cart', []))

@app.route('/subcategory/<subcategory_name>')
def subcategory(subcategory_name):
    products = Product.query.filter(Product.subcategory_str.contains(subcategory_name)).all()
    # AJAX support for infinite scroll/dynamic loading if your frontend requests it
    if request.args.get('ajax') == 'true':
        html = ""
        for p in products:
            html += f'<div class="product-card"><img src="{p.image}" onclick="openImageModal(this.src)"><h3>{p.name_kh}</h3><div class="price-line">{ "{:,}".format(p.price) }៛</div><form class="add-to-cart-form"><input type="hidden" name="product_id" value="{p.id}"><button type="submit" class="add-cart-button">🛒 Add</button></form></div>'
        return html
    return render_template('home.html', products=products, subcategories=[], current_subcategory=subcategory_name, cart=session.get('cart', []))

@app.route('/product/<int:product_id>')
def product_detail(product_id):
    product = Product.query.get(product_id)
    return render_template('product.html', product=product, cart=session.get('cart', []))

@app.route('/search')
def search():
    query = request.args.get('q', '')
    if query:
        products = Product.query.filter(Product.name_kh.contains(query)).all()
    else:
        products = []
    return render_template('home.html', products=products, subcategories=[], current_category=f"Search: {query}", cart=session.get('cart', []))

# --- CART LOGIC ---
@app.route('/add-to-cart', methods=['POST'])
def add_to_cart():
    try:
        p_id = int(request.form.get('product_id'))
        qty = int(request.form.get('quantity', 1))
        p = Product.query.get(p_id)
        if not p: return jsonify({'success': False})
        
        cart = session.get('cart', [])
        # Save as dict for session
        p_dict = {"id": p.id, "name_kh": p.name_kh, "price": p.price, "image": p.image}
        cart.append({"product": p_dict, "quantity": qty})
        session['cart'] = cart
        return jsonify({"success": True, "cart_count": len(cart)})
    except: return jsonify({'success': False})

@app.route('/cart')
def cart_page(): return render_template('cart.html', cart=session.get('cart', []))

@app.route('/remove-from-cart/<int:index>', methods=["POST"])
def remove_from_cart(index):
    cart = session.get('cart', [])
    if 0 <= index < len(cart): cart.pop(index)
    session['cart'] = cart
    return redirect(url_for('cart_page'))

@app.route('/checkout', methods=["GET", "POST"])
def checkout():
    cart = session.get('cart', [])
    if request.method == "POST":
        name = request.form['name']
        phone = request.form['phone']
        msg = f"🛒 *Order from {name}*\nPhone: {phone}\nItems: {len(cart)}"
        try: requests.post(f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage", data={"chat_id": CHAT_ID, "text": msg, "parse_mode": "Markdown"})
        except: pass
        session['cart'] = []
        return redirect(url_for('thank_you'))
    return render_template('checkout.html', cart=cart)

@app.route('/thankyou')
def thank_you(): return render_template('thankyou.html')
@app.route('/lucky-draw')
def lucky_draw(): return render_template('minifigure_game.html')
@app.route('/custom-bracelet')
def custom_bracelet(): return render_template('custom_bracelet.html')

# --- ADMIN PANEL ---
@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        if request.form['username'] == ADMIN_USERNAME and request.form['password'] == ADMIN_PASSWORD:
            session['admin'] = True
            return redirect(url_for('admin_products'))
    return render_template('admin_login.html')

@app.route('/admin/products')
def admin_products():
    if not session.get('admin'): return redirect(url_for('admin_login'))
    return render_template('admin_products.html', products=Product.query.all())

@app.route('/admin/add-product', methods=['GET', 'POST'])
def add_product():
    if not session.get('admin'): return redirect(url_for('admin_login'))
    if request.method == 'POST':
        new_p = Product(
            name_kh=request.form['name_kh'],
            price=int(request.form['price']),
            image=request.form['image'],
            categories_str=request.form.get('categories', ''),
            subcategory_str=request.form.get('subcategory', ''),
            stock=int(request.form.get('stock', 1))
        )
        db.session.add(new_p)
        db.session.commit()
        return redirect(url_for('admin_products'))
    return render_template('add_product.html')

@app.route('/admin/delete-product/<int:product_id>', methods=['POST'])
def delete_product(product_id):
    if not session.get('admin'): return redirect(url_for('admin_login'))
    p = Product.query.get(product_id)
    if p:
        db.session.delete(p)
        db.session.commit()
    return redirect(url_for('admin_products'))

# --- STARTUP ---
if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        # Create initial data if DB is empty
        if not Product.query.first():
            print("Creating database...")
            for p_data in initial_products:
                db.session.add(Product(id=p_data['id'], name_kh=p_data['name_kh'], price=p_data['price'], image=p_data['image'], categories_str=p_data['categories'], subcategory_str=p_data['subcategory'], stock=p_data['stock']))
            db.session.commit()
    
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)


