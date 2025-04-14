from flask import Flask, render_template, request, redirect, url_for, jsonify
import requests

app = Flask(__name__)
app.secret_key = 'your_secret_key'

# Products data
products = [
    {"id": 1, "name_kh": "M416 - ប្រាក់មាស", "name_en": "M416 - Gold Plate", "price": 6000, "image": "/static/images/m416-gold.jpg", "categories": ["Keychain"], "subcategory": "Gun Keychains"},
    {"id": 2, "name_kh": "M416 - ពណ៌ដើម", "name_en": "M416 - Default", "price": 6000, "image": "/static/images/m416-default.jpg", "categories": ["Keychain"], "subcategory": "Gun Keychains"},
    {"id": 3, "name_kh": "AKM - ប្រាក់មាស", "name_en": "AKM - Gold Plate", "price": 6000, "image": "/static/images/akm-gold.jpg", "categories": ["Keychain"], "subcategory": "Gun Keychains"},
    {"id": 4, "name_kh": "AKM - ពណ៌ដើម", "name_en": "AKM - Default", "price": 6000, "image": "/static/images/akm-default.jpg", "categories": ["Keychain"], "subcategory": "Gun Keychains"},
    {"id": 5, "name_kh": "Scar L - ពណ៌ដើម", "name_en": "Scar L - Default", "price": 6000, "image": "/static/images/scarl-default.jpg", "categories": ["Keychain"], "subcategory": "Gun Keychains"},
    {"id": 6, "name_kh": "Scar L - ពណ៌មាស", "name_en": "Scar L - Gold", "price": 6000, "image": "/static/images/scarl-gold.jpg", "categories": ["Keychain"], "subcategory": "Gun Keychains"},
    {"id": 7, "name_kh": "ក្រវិលស", "name_en": "White Chalcedony", "price": 6000, "image": "/static/images/bc-01.jpg", "categories": ["Accessories"], "subcategory": "Gem Stone Bracelets"},
    {"id": 8, "name_kh": "ក្រវិលពណ៌ផ្កាឈូក", "name_en": "Pink Opal", "price": 6000, "image": "/static/images/bc-02.jpg", "categories": ["Accessories"], "subcategory": "Gem Stone Bracelets"},
    {"id": 9, "name_kh": "គ្រីស្ទាល់ពណ៌ផ្កាឈូក", "name_en": "Pink Crystal", "price": 5500, "image": "/static/images/bc-03.jpg", "categories": ["Accessories"], "subcategory": "Gem Stone Bracelets"},
    {"id": 10, "name_kh": "គ្រីស្ទាល់ស្ករត្រសក់", "name_en": "Strawberry Crystal", "price": 9000, "image": "/static/images/bc-04.jpg", "categories": ["Accessories"], "subcategory": "Gem Stone Bracelets"},
    {"id": 11, "name_kh": "Lego Ninjago Season 1 - DX Suit", "name_en": "Lego Ninjago Season 1 - DX Suit", "price": 30000, "image": "/static/images/njoss1dx.jpg", "categories": ["Lego Ninjago", "Toy"], "subcategory": "Season 1"},
    {"id": 12, "name_kh": "Kai (DX)", "name_en": "Lego Ninjago Season 1 - Kai", "price": 5000, "image": "/static/images/njoss1dxkai.jpg", "categories": ["Lego Ninjago", "Toy"], "subcategory": "Season 1"},
    {"id": 13, "name_kh": "Zane (DX)", "name_en": "Lego Ninjago Season 1 - Zane", "price": 5000, "image": "/static/images/njoss1dxzane.jpg", "categories": ["Lego Ninjago", "Toy"], "subcategory": "Season 1"},
    {"id": 14, "name_kh": "Jay (DX)", "name_en": "Lego Ninjago Season 1 - Jay", "price": 5000, "image": "/static/images/njoss1dxjay.jpg", "categories": ["Lego Ninjago", "Toy"], "subcategory": "Season 1"},
    {"id": 15, "name_kh": "Cole (DX)", "name_en": "Lego Ninjago Season 1 - Cole", "price": 5000, "image": "/static/images/njoss1dxcole.jpg", "categories": ["Lego Ninjago", "Toy"], "subcategory": "Season 1"},
    {"id": 16, "name_kh": "Nya (DX)", "name_en": "Lego Ninjago Season 1 - Nya", "price": 5000, "image": "/static/images/njoss1dxnya.jpg", "categories": ["Lego Ninjago", "Toy"], "subcategory": "Season 1"},
    {"id": 17, "name_kh": "Lloyd (DX)", "name_en": "Lego Ninjago Season 1 - Lloyd", "price": 5000, "image": "/static/images/njoss1dxlloyd.jpg", "categories": ["Lego Ninjago", "Toy"], "subcategory": "Season 1"},
    {"id": 18, "name_kh": "Lego Ninjago Season 1 - Pilot Suit", "name_en": "Lego Ninjago Season 1 - Pilot Suit", "price": 25000, "image": "/static/images/njoss1pilot.jpg", "categories": ["Lego Ninjago", "Toy"], "subcategory": "Season 2"},
    {"id": 19, "name_kh": "Lego Ninjago Season 1 - Kai", "name_en": "Lego Ninjago Season 1 - Kai", "price": 5000, "image": "/static/images/njoss1pilotkai.jpg", "categories": ["Lego Ninjago", "Toy"], "subcategory": "Season 2"},
    {"id": 20, "name_kh": "Lego Ninjago Season 1 - Zane", "name_en": "Lego Ninjago Season 1 - Zane", "price": 5000, "image": "/static/images/njoss1pilotzane.jpg", "categories": ["Lego Ninjago", "Toy"], "subcategory": "Season 2"},
    {"id": 21, "name_kh": "Lego Ninjago Season 1 - Jay", "name_en": "Lego Ninjago Season 1 - Jay", "price": 5000, "image": "/static/images/njoss1pilotjay.jpg", "categories": ["Lego Ninjago", "Toy"], "subcategory": "Season 2"},
    {"id": 22, "name_kh": "Lego Ninjago Season 1 - Cole", "name_en": "Lego Ninjago Season 1 - Cole", "price": 5000, "image": "/static/images/njoss1pilotcole.jpg", "categories": ["Lego Ninjago", "Toy"], "subcategory": "Season 2"},
    {"id": 23, "name_kh": "Lego Ninjago Season 1 - Lloyd", "name_en": "Lego Ninjago Season 1 - Lloyd", "price": 5000, "image": "/static/images/njoss1pilotlloyd.jpg", "categories": ["Lego Ninjago", "Toy"], "subcategory": "Season 2"},
    {"id": 24, "name_kh": "ខ្សៃដៃថ្មធម្មជាតិ - ", "name_en": "Gem Stone Bracelet - ", "price": 5000, "image": "/static/images/bc-05.jpg", "categories": ["Accessories"], "subcategory": "Gem Stone Bracelets"},
    {"id": 24, "name_kh": "ខ្សៃដៃថ្មធម្មជាតិ - ", "name_en": "Gem Stone Bracelet - ", "price": 5000, "image": "/static/images/bc-06.jpg", "categories": ["Accessories"], "subcategory": "Gem Stone Bracelets"},
    {"id": 24, "name_kh": "ខ្សៃដៃថ្មធម្មជាតិ - ", "name_en": "Gem Stone Bracelet - ", "price": 5000, "image": "/static/images/bc-07.jpg", "categories": ["Accessories"], "subcategory": "Gem Stone Bracelets"},
    {"id": 24, "name_kh": "ខ្សៃដៃថ្មធម្មជាតិ - ", "name_en": "Gem Stone Bracelet - ", "price": 5000, "image": "/static/images/bc-08.jpg", "categories": ["Accessories"], "subcategory": "Gem Stone Bracelets"},
    {"id": 24, "name_kh": "ខ្សៃដៃថ្មធម្មជាតិ - ", "name_en": "Gem Stone Bracelet - ", "price": 5000, "image": "/static/images/bc-09.jpg", "categories": ["Accessories"], "subcategory": "Gem Stone Bracelets"},
    {"id": 24, "name_kh": "ខ្សៃដៃថ្មធម្មជាតិ - ", "name_en": "Gem Stone Bracelet - ", "price": 5000, "image": "/static/images/bc-10.jpg", "categories": ["Accessories"], "subcategory": "Gem Stone Bracelets"},
    
]

# Subcategories map
subcategories_map = {
    "Accessories": ["Gem Stone Bracelets", "Gym Bracelet"],
    "Lego Ninjago": ["Season 1", "Season 2", "Season 3", "Season 4", "Season 5", "Season 6", "Season 7", "Season 8"],
    "Keychain": ["Gun Keychains"],
    "Hot Sale": [],
    "Toy": ["Lego Ninjago", "Lego WWII", "Lego ទាហាន"]
}

# In-memory cart
cart = []

# Home
@app.route('/')
def home():
    language = request.args.get('lang', 'kh')  # Khmer is default
    return render_template('home.html', products=products, language=language, cart=cart, current_category=None, subcategories=[])

# Category
@app.route('/category/<category_name>')
def category(category_name):
    language = request.args.get('lang', 'kh')
    filtered_products = [p for p in products if category_name in p['categories']]
    subs = subcategories_map.get(category_name, [])
    return render_template('home.html', products=filtered_products, language=language, cart=cart, current_category=category_name, subcategories=subs)

# Subcategory
@app.route('/subcategory/<subcategory_name>')
def subcategory(subcategory_name):
    language = request.args.get('lang', 'kh')
    filtered_products = [p for p in products if p.get('subcategory') == subcategory_name]
    return render_template('home.html', products=filtered_products, language=language, cart=cart, current_category=subcategory_name, subcategories=[])

# Product Detail
@app.route('/product/<int:product_id>')
def product_detail(product_id):
    language = request.args.get('lang', 'kh')
    product = next((p for p in products if p['id'] == product_id), None)
    return render_template('product.html', product=product, language=language)

# Cart Page
@app.route('/cart')
def cart_page():
    language = request.args.get('lang', 'kh')
    return render_template('cart.html', cart=cart, language=language)

# Add to Cart
@app.route('/add-to-cart', methods=["POST"])
def add_to_cart():
    product_id = int(request.form['product_id'])
    quantity = int(request.form['quantity'])
    product = next((p for p in products if p["id"] == product_id), None)
    if product:
        cart.append({"product": product, "quantity": quantity})
    return jsonify({"success": True, "cart_count": len(cart)})

# Remove from Cart
@app.route('/remove-from-cart/<int:index>', methods=["POST"])
def remove_from_cart(index):
    if 0 <= index < len(cart):
        cart.pop(index)
    return redirect(url_for('cart_page'))

# Checkout
@app.route('/checkout', methods=["GET", "POST"])
def checkout():
    language = request.args.get('lang', 'kh')
    if request.method == "POST":
        name = request.form['name']
        phone = request.form['phone']
        address = request.form['address']

        message = f"🛒 *New Order Received!*\n\n"
        message += f"*Name:* {name}\n*Phone:* {phone}\n*Address:* {address}\n\n*Order Details:*\n"

        total = 0
        for item in cart:
            p = item['product']
            subtotal = p['price'] * item['quantity']
            total += subtotal
            message += f"- {p['name_en']} x {item['quantity']} = {subtotal}៛\n"

        message += f"\n*Total:* {total}៛"

        bot_token = 'YOUR_TELEGRAM_BOT_TOKEN'
        chat_id = YOUR_CHAT_ID
        url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
        payload = {"chat_id": chat_id, "text": message, "parse_mode": "Markdown"}
        response = requests.post(url, data=payload)

        if response.status_code != 200:
            print("Telegram error:", response.text)

        cart.clear()
        return redirect(url_for('thank_you'))

    return render_template('checkout.html', language=language)

# Thank you
@app.route('/thankyou')
def thank_you():
    language = request.args.get('lang', 'kh')
    return render_template('thankyou.html', language=language)

if __name__ == '__main__':
    import os
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)