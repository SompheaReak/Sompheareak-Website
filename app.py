import os
import requests
from flask import Flask, render_template, request, redirect, url_for, jsonify, session, abort

app = Flask(__name__)
app.secret_key = 'your_secret_key'
app.debug = True

# Admin credentials
ADMIN_USERNAME = 'AdminSompheaReakVitou'
ADMIN_PASSWORD = 'Thesong_Admin@2022?!$'

# Banned IPs
banned_ips = ['123.45.67.89']

# Notify visitor once
def notify_telegram(ip, user_agent):
    if session.get('notified'):
        return  # Prevent repeat notification

    bot_token = "7663680888:AAHhInaDKP8QNxw8l87dQaNPsRTZFQXy1J4"
    chat_id = "-1002660809745"
    message = f"🌐 *New Visitor Alert!*\n\n*IP:* `{ip}`\n*Device:* `{user_agent}`"
    url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
    payload = {'chat_id': chat_id, 'text': message, 'parse_mode': 'Markdown'}

    try:
        requests.post(url, data=payload)
        session['notified'] = True
    except Exception as e:
        print("Telegram error:", e)

# Order notifier
def send_order_to_telegram(name, phone, address, delivery_method, delivery_fee, ip_list, cart, total):
    bot_token = "7663680888:AAHhInaDKP8QNxw8l87dQaNPsRTZFQXy1J4"
    chat_id = "-1002660809745"
    media = []

    for item in cart:
        media.append({
            "type": "photo",
            "media": item["product"]["image"],
            "caption": f"{item['product']['name_kh']} x {item['quantity']} = {item['quantity'] * item['product']['price']:,}៛",
            "parse_mode": "HTML"
        })

    if media:
        requests.post(f"https://api.telegram.org/bot{bot_token}/sendMediaGroup",
                      json={"chat_id": chat_id, "media": media[:10]})

    order_lines = "\n".join(
        f"{item['product']['name_kh']} x {item['quantity']} = {item['quantity'] * item['product']['price']:,}៛"
        for item in cart
    )

    summary = f"""🛒 បញ្ជាទិញថ្មី!

ឈ្មោះ: {name}
ទូរស័ព្ទ: {phone}
អាសយដ្ឋាន: {address}
ដឹកជញ្ជូន: {delivery_method} ({delivery_fee:,}៛)
IP: {ip_list}

ព័ត៌មានការកម្មង់:
{order_lines}

សរុបជាមួយដឹកជញ្ជូន: {total:,}៛
"""

    requests.post(f"https://api.telegram.org/bot{bot_token}/sendMessage",
                  json={"chat_id": chat_id, "text": summary, "parse_mode": "HTML"})

# Before each request
@app.before_request
def block_banned_ips():
    ip = request.headers.get('X-Forwarded-For', request.remote_addr).split(',')[0].strip()
    user_agent = request.headers.get('User-Agent')

    if ip in banned_ips:
        abort(403)

    notify_telegram(ip, user_agent)

# Dummy product list
products = []  # You will fill this

subcategories_map = {
    "Accessories": ["Gym Bracelet", "Gem Stone Bracelet","Dragon Bracelet","Bracelet"],
    "LEGO Ninjago": ["New","Building Set","Season 1", "Season 2", "Season 3", "Season 4", "Season 5", "Season 6", "Season 7", "Season 8"],
    "Keychain": ["Gun Keychains"],
    "Hot Sale": [],
    "Toy": ["Lego Ninjago", "Lego WWII", "Lego ទាហាន"]
}

@app.route('/')
def home():
    return redirect(url_for('category', category_name='Hot Sale'))

@app.route('/category/<category_name>')
def category(category_name):
    language = request.args.get('lang', 'kh')
    subs = subcategories_map.get(category_name, [])
    if subs:
        return redirect(url_for('subcategory', subcategory_name=subs[0]))

    filtered_products = [p for p in products if category_name in p.get('categories', [])]
    cart = session.get('cart', [])
    return render_template('home.html', products=filtered_products, language=language, cart=cart, current_category=category_name, current_subcategory=None, subcategories=[])

@app.route('/subcategory/<subcategory_name>')
def subcategory(subcategory_name):
    language = request.args.get('lang', 'kh')
    filtered_products = [p for p in products if subcategory_name in p.get('subcategory', [])]
    cart = session.get('cart', [])
    main_category = next((cat for cat, subs in subcategories_map.items() if subcategory_name in subs), None)
    subs = subcategories_map.get(main_category, []) if main_category else []

    if request.args.get('ajax') == 'true':
        return render_template('product_cards.html', products=filtered_products, language=language)

    return render_template('home.html', products=filtered_products, language=language, cart=cart, current_category=main_category, current_subcategory=subcategory_name, subcategories=subs)

@app.route('/product/<int:product_id>')
def product_detail(product_id):
    language = request.args.get('lang', 'kh')
    product = next((p for p in products if p['id'] == product_id), None)
    cart = session.get('cart', [])
    return render_template('product.html', product=product, language=language, cart=cart)

@app.route('/cart')
def cart_page():
    language = request.args.get('lang', 'kh')
    cart = session.get('cart', [])
    return render_template('cart.html', cart=cart, language=language)

@app.route('/add-to-cart', methods=['POST'])
def add_to_cart():
    product_id = int(request.form.get('product_id'))
    quantity = int(request.form.get('quantity', 1))
    product = next((p for p in products if p['id'] == product_id), None)
    if not product:
        return jsonify({'success': False})

    cart = session.get('cart', [])
    cart.append({"product": product, "quantity": quantity})
    session['cart'] = cart
    return jsonify({"success": True, "cart_count": len(cart)})

@app.route('/remove-from-cart/<int:index>', methods=["POST"])
def remove_from_cart(index):
    cart = session.get('cart', [])
    if 0 <= index < len(cart):
        cart.pop(index)
    session['cart'] = cart
    return redirect(url_for('cart_page'))

@app.route('/checkout', methods=["GET", "POST"])
def checkout():
    language = request.args.get('lang', 'kh')
    cart = session.get('cart', [])

    if request.method == "POST":
        ip = request.headers.get('X-Forwarded-For', request.remote_addr)
        name = request.form['name']
        phone = request.form['phone']
        address = request.form['address']
        delivery_method = request.form['delivery']

        delivery_text = {"door": "ទំនិញដល់ដៃទូទាត់ប្រាក់", "vet": "វីរៈប៊ុនថាំ (VET)", "jnt": "J&T"}.get(delivery_method, "")
        delivery_fee = {"door": 7000, "vet": 5000, "jnt": 7000}.get(delivery_method, 0)

        total = sum(item['product']['price'] * item['quantity'] for item in cart)
        total += delivery_fee

        send_order_to_telegram(name, phone, address, delivery_text, delivery_fee, ip, cart, total)
        session['cart'] = []
        return redirect(url_for('thank_you'))

    return render_template('checkout.html', language=language, cart=cart)

@app.route('/thank-you')
def thank_you():
    language = request.args.get('lang', 'kh')
    return render_template('thankyou.html', language=language)

@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    error = None
    if request.method == 'POST':
        if request.form['username'] == ADMIN_USERNAME and request.form['password'] == ADMIN_PASSWORD:
            session['admin'] = True
            return redirect(url_for('admin_dashboard'))
        error = 'Invalid credentials.'
    return render_template('admin_login.html', error=error)

@app.route('/admin/dashboard')
def admin_dashboard():
    if not session.get('admin'):
        return redirect(url_for('admin_login'))
    return render_template('admin_dashboard.html')

@app.route('/admin/products')
def admin_products():
    if not session.get('admin'):
        return redirect(url_for('admin_login'))
    return render_template('admin_products.html', products=products)

@app.route('/admin/add-product', methods=['GET', 'POST'])
def add_product():
    if not session.get('admin'):
        return redirect(url_for('admin_login'))

    if request.method == 'POST':
        new_id = max([p['id'] for p in products]) + 1 if products else 1
        new_product = {
            'id': new_id,
            'name_kh': request.form['name_kh'],
            'name_en': request.form['name_en'],
            'price': int(request.form['price']),
            'image': request.form['image'],
            'categories': [request.form['category']],
            'subcategory': request.form['subcategory']
        }
        products.append(new_product)
        return redirect(url_for('admin_products'))

    return render_template('add_product.html')

@app.route('/admin/edit-product/<int:product_id>', methods=['GET', 'POST'])
def edit_product(product_id):
    if not session.get('admin'):
        return redirect(url_for('admin_login'))

    product = next((p for p in products if p['id'] == product_id), None)
    if not product:
        return "Product not found", 404

    if request.method == 'POST':
        product.update({
            'name_kh': request.form['name_kh'],
            'name_en': request.form['name_en'],
            'price': int(request.form['price']),
            'image': request.form['image']
        })
        return redirect(url_for('admin_products'))

    return render_template('edit_product.html', product=product)

@app.route('/admin/delete-product/<int:product_id>', methods=['POST'])
def delete_product(product_id):
    if not session.get('admin'):
        return redirect(url_for('admin_login'))

    global products
    products = [p for p in products if p['id'] != product_id]
    return redirect(url_for('admin_products'))

@app.route('/admin/ban-ip', methods=['GET', 'POST'])
def ban_ip():
    if not session.get('admin'):
        return redirect(url_for('admin_login'))

    message = ""
    if request.method == 'POST':
        ip = request.form.get('ip')
        if ip and ip not in banned_ips:
            banned_ips.append(ip)
            message = f"IP {ip} has been banned."

    return render_template('ban_ip.html', banned_ips=banned_ips, message=message)

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('home'))

@app.errorhandler(403)
def forbidden(e):
    return "Access Denied: Your IP is blocked.", 403

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)