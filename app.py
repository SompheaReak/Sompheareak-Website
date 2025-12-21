import os 
import requests
from flask import Flask, render_template, request, redirect, url_for, jsonify, session, abort

app = Flask(__name__)
app.secret_key = 'your_secret_key_change_in_production'
app.debug = True

# --- CONFIGURATION ---
ADMIN_USERNAME = 'AdminSompheaReakVitou'
ADMIN_PASSWORD = 'Thesong_Admin@2022?!$'
BOT_TOKEN = "7528700801:AAGTvXjk5qPBnq_qx69ZOW4RMLuGy40w5k8"
CHAT_ID = "-1002654437316"
BANNED_IPS = ['123.45.67.89','45.119.135.70']

# --- DATA (Restored from your previous input) ---
products = [
    {"id": 101, "name_kh": "NINJAGO Season 1 - DX Suit", "price": 30000, "image": "https://raw.githubusercontent.com/TheSong-Store/static/main/images/njoss1dx.jpg", "categories": ["LEGO Ninjago", "Toy"], "subcategory": ["Lego Ninjago", "Season 1"], "stock": 1},
    {"id": 102, "name_kh": "NINJAGO Season 1 - KAI (DX)", "price": 5000, "image": "https://raw.githubusercontent.com/TheSong-Store/static/main/images/njoss1dxkai.jpg", "categories": ["LEGO Ninjago", "Toy"], "subcategory": ["Lego Ninjago", "Season 1"], "stock": 1},
    {"id": 103, "name_kh": "NINJAGO Season 1 - ZANE (DX)", "price": 5000, "image": "https://raw.githubusercontent.com/TheSong-Store/static/main/images/njoss1dxzane.jpg", "categories": ["LEGO Ninjago", "Toy"], "subcategory": ["Lego Ninjago", "Season 1"], "stock": 1},
]

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
        message = f"📦 *New Visitor*\n*IP:* `{ip}`\n*Device:* `{user_agent}`"
        url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
        requests.post(url, data={"chat_id": CHAT_ID, "text": message, "parse_mode": "Markdown"})
    except:
        pass

@app.before_request
def block_banned_ips():
    if request.headers.getlist("X-Forwarded-For"):
        ip = request.headers.getlist("X-Forwarded-For")[0]
    else:
        ip = request.remote_addr
    
    user_agent = request.headers.get('User-Agent')

    if ip in BANNED_IPS: abort(403)
    if not session.get('notified'):
        notify_telegram(ip, user_agent)
        session['notified'] = True

# --- ROUTES ---
@app.route('/')
def home():
    language = request.args.get('lang', 'kh')
    cart = session.get('cart', [])
    return render_template('home.html', products=products, language=language, cart=cart, 
                         subcategories=[], current_category=None)

@app.route('/category/<category_name>')
def category(category_name):
    language = request.args.get('lang', 'kh')
    if category_name == 'Lucky Draw': return redirect(url_for('lucky_draw'))
    
    # Filter products
    filtered = [p for p in products if category_name in p.get('categories', [])]
    subs = subcategories_map.get(category_name, [])
    cart = session.get('cart', [])
    
    return render_template('home.html', products=filtered, language=language, cart=cart,
                         subcategories=subs, current_category=category_name)

@app.route('/subcategory/<subcategory_name>')
def subcategory(subcategory_name):
    language = request.args.get('lang', 'kh')
    filtered = [p for p in products if subcategory_name in p.get('subcategory', [])]
    cart = session.get('cart', [])

    if request.args.get('ajax') == 'true':
        html = ""
        for p in filtered:
            html += f'''
            <div class="product-card">
                <img src="{p['image']}" onclick="openImageModal(this.src)">
                <h3>{p['name_kh']}</h3>
                <div class="price-line"><span class="discounted">{p['price']:,}៛</span></div>
                <form class="add-to-cart-form">
                    <input type="hidden" name="product_id" value="{p['id']}">
                    <div class="quantity-selector">
                        <input type="number" name="quantity" value="1" min="1" style="width:40px;">
                    </div>
                    <button type="submit" class="add-cart-button">បន្ថែម</button>
                </form>
            </div>'''
        return html

    return render_template('home.html', products=filtered, language=language, cart=cart,
                         subcategories=[], current_subcategory=subcategory_name)

@app.route('/product/<int:product_id>')
def product_detail(product_id):
    product = next((p for p in products if p['id'] == product_id), None)
    cart = session.get('cart', [])
    return render_template('product.html', product=product, language=request.args.get('lang', 'kh'), cart=cart)

@app.route('/add-to-cart', methods=['POST'])
def add_to_cart():
    try:
        p_id = int(request.form.get('product_id'))
        qty = int(request.form.get('quantity', 1))
        product = next((p for p in products if p['id'] == p_id), None)
        if not product: return jsonify({'success': False})
        
        cart = session.get('cart', [])
        cart.append({"product": product, "quantity": qty})
        session['cart'] = cart
        return jsonify({"success": True, "cart_count": len(cart)})
    except Exception as e:
        print(f"Error adding to cart: {e}")
        return jsonify({'success': False})

@app.route('/cart')
def cart_page():
    return render_template('cart.html', cart=session.get('cart', []), language=request.args.get('lang', 'kh'))

@app.route('/remove-from-cart/<int:index>', methods=["POST"])
def remove_from_cart(index):
    cart = session.get('cart', [])
    if 0 <= index < len(cart): cart.pop(index)
    session['cart'] = cart
    return redirect(url_for('cart_page'))

@app.route('/checkout', methods=["GET", "POST"])
def checkout():
    language = request.args.get('lang', 'kh')
    cart = session.get('cart', [])

    if request.method == "POST":
        ip = request.headers.get('X-Forwarded-For', request.remote_addr)
        user_agent = request.headers.get('User-Agent')
        name = request.form['name']
        phone = request.form['phone']
        address = request.form['address']
        
        message = f"🛒 *New Order*\n*Name:* {name}\n*Phone:* {phone}\n*Address:* {address}\n*IP:* `{ip}`"
        try:
            requests.post(f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage", 
                        data={"chat_id": CHAT_ID, "text": message, "parse_mode": "Markdown"})
        except: pass

        session['cart'] = []
        return redirect(url_for('thank_you'))

    return render_template('checkout.html', language=language, cart=cart)

@app.route('/thankyou')
def thank_you():
    return render_template('thankyou.html', language=request.args.get('lang', 'kh'))

@app.route('/lucky-draw')
def lucky_draw():
    return render_template('minifigure_game.html')

@app.route('/custom-bracelet')
def custom_bracelet():
    charms = [
        {"id": 1, "name_kh": "Car Logo","price": 3000, "image": "https://raw.githubusercontent.com/TheSong-Store/static/main/images/cc01.jpg"},
        {"id": 2, "name_kh": "Car Logo","price": 3000, "image": "https://raw.githubusercontent.com/TheSong-Store/static/main/images/cc02.jpg"},
    ]
    return render_template('custom_bracelet.html', charms=charms)

# --- ADMIN ROUTES ---
@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    error = None
    if request.method == 'POST':
        if request.form['username'] == ADMIN_USERNAME and request.form['password'] == ADMIN_PASSWORD:
            session['admin'] = True
            return redirect(url_for('admin_dashboard'))
        else:
            error = 'Invalid credentials.'
    return render_template('admin_login.html', error=error)

@app.route('/admin/dashboard')
def admin_dashboard():
    if not session.get('admin'): return redirect(url_for('admin_login'))
    return render_template('admin_dashboard.html')

@app.route('/admin/products')
def admin_products():
    if not session.get('admin'): return redirect(url_for('admin_login'))
    return render_template('admin_products.html', products=products)

@app.route('/admin/ban-ip', methods=['GET', 'POST'])
def ban_ip():
    if not session.get('admin'): return redirect(url_for('admin_login'))
    if request.method == 'POST':
        ip = request.form.get('ip')
        if ip and ip not in BANNED_IPS: BANNED_IPS.append(ip)
    return render_template('ban_ip.html', banned_ips=BANNED_IPS)

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)


