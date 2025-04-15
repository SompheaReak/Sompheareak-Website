from flask import Flask, render_template, request, redirect, url_for, jsonify, session
import requests

app = Flask(__name__)
app.secret_key = 'your_secret_key'
app.debug = True

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
    {"id": 11, "name_kh": "Lego Ninjago Season 1 - DX Suit", "name_en": "Lego Ninjago Season 1 - DX Suit", "price": 30000, "image": "/static/images/njoss1dx.jpg", "categories": ["LEGO Ninjago", "Toy"], "subcategory": ["Lego Ninjago","Season 1"]},
    {"id": 12, "name_kh": "Kai (DX)", "name_en": "Lego Ninjago Season 1 - Kai", "price": 5000, "image": "/static/images/njoss1dxkai.jpg", "categories": ["LEGO Ninjago", "Toy"], "subcategory": ["Lego Ninjago","Season 1"]},
    {"id": 13, "name_kh": "Zane (DX)", "name_en": "Lego Ninjago Season 1 - Zane", "price": 5000, "image": "/static/images/njoss1dxzane.jpg", "categories": ["LEGO Ninjago", "Toy"], "subcategory": ["Lego Ninjago","Season 1"]},
    {"id": 14, "name_kh": "Jay (DX)", "name_en": "Lego Ninjago Season 1 - Jay", "price": 5000, "image": "/static/images/njoss1dxjay.jpg", "categories": ["LEGO Ninjago", "Toy"], "subcategory": ["Lego Ninjago","Season 1"]},
    {"id": 15, "name_kh": "Cole (DX)", "name_en": "Lego Ninjago Season 1 - Cole", "price": 5000, "image": "/static/images/njoss1dxcole.jpg", "categories": ["LEGO Ninjago", "Toy"], "subcategory": ["Lego Ninjago","Season 1"]},
    {"id": 16, "name_kh": "Nya (DX)", "name_en": "Lego Ninjago Season 1 - Nya", "price": 5000, "image": "/static/images/njoss1dxnya.jpg", "categories": ["LEGO Ninjago", "Toy"], "subcategory": ["Lego Ninjago","Season 1"]},
    {"id": 17, "name_kh": "Lloyd (DX)", "name_en": "Lego Ninjago Season 1 - Lloyd", "price": 5000, "image": "/static/images/njoss1dxlloyd.jpg", "categories": ["LEGO Ninjago", "Toy"], "subcategory": ["Lego Ninjago","Season 1"]},
    {"id": 18, "name_kh": "Lego Ninjago Season 1 - Pilot Suit", "name_en": "Lego Ninjago Season 1 - Pilot Suit", "price": 25000, "image": "/static/images/njoss1pilot.jpg", "categories": ["LEGO Ninjago", "Toy"], "subcategory": ["Lego Ninjago","Season 1"]},
    {"id": 19, "name_kh": "Lego Ninjago Season 1 - Kai", "name_en": "Lego Ninjago Season 1 - Kai", "price": 5000, "image": "/static/images/njoss1pilotkai.jpg", "categories": ["LEGO Ninjago", "Toy"], "subcategory": ["Lego Ninjago","Season 1"]},
    {"id": 20, "name_kh": "Lego Ninjago Season 1 - Zane", "name_en": "Lego Ninjago Season 1 - Zane", "price": 5000, "image": "/static/images/njoss1pilotzane.jpg", "categories": ["LEGO Ninjago", "Toy"], "subcategory": ["Lego Ninjago","Season 1"]},
    {"id": 21, "name_kh": "Lego Ninjago Season 1 - Jay", "name_en": "Lego Ninjago Season 1 - Jay", "price": 5000, "image": "/static/images/njoss1pilotjay.jpg", "categories": ["LEGO Ninjago", "Toy"], "subcategory": ["Lego Ninjago","Season 1"]},
    {"id": 22, "name_kh": "Lego Ninjago Season 1 - Cole", "name_en": "Lego Ninjago Season 1 - Cole", "price": 5000, "image": "/static/images/njoss1pilotcole.jpg", "categories": ["LEGO Ninjago", "Toy"], "subcategory": ["Lego Ninjago","Season 1"]},
    {"id": 23, "name_kh": "Lego Ninjago Season 1 - Lloyd", "name_en": "Lego Ninjago Season 1 - Lloyd", "price": 5000, "image": "/static/images/njoss1pilotlloyd.jpg", "categories": ["LEGO Ninjago", "Toy"], "subcategory": ["Lego Ninjago","Season 1"]},
    {"id": 24, "name_kh": "ខ្សៃដៃថ្មធម្មជាតិ - ", "name_en": "Gem Stone Bracelet - ", "price": 5000, "image": "/static/images/bc-05.jpg", "categories": ["Accessories"], "subcategory": "Gem Stone Bracelets"},
    {"id": 25, "name_kh": "ខ្សៃដៃថ្មធម្មជាតិ - ", "name_en": "Gem Stone Bracelet - ", "price": 5000, "image": "/static/images/bc-06.jpg", "categories": ["Accessories"], "subcategory": "Gem Stone Bracelets"},
    {"id": 26, "name_kh": "ខ្សៃដៃថ្មធម្មជាតិ - ", "name_en": "Gem Stone Bracelet - ", "price": 5000, "image": "/static/images/bc-07.jpg", "categories": ["Accessories"], "subcategory": "Gem Stone Bracelets"},
    {"id": 27, "name_kh": "ខ្សៃដៃថ្មធម្មជាតិ - ", "name_en": "Gem Stone Bracelet - ", "price": 5000, "image": "/static/images/bc-08.jpg", "categories": ["Accessories"], "subcategory": "Gem Stone Bracelets"},
    {"id": 28, "name_kh": "ខ្សៃដៃថ្មធម្មជាតិ - ", "name_en": "Gem Stone Bracelet - ", "price": 5000, "image": "/static/images/bc-09.jpg", "categories": ["Accessories"], "subcategory": "Gem Stone Bracelets"},
    {"id": 29, "name_kh": "ខ្សៃដៃថ្មធម្មជាតិ - ", "name_en": "Gem Stone Bracelet - ", "price": 5000, "image": "/static/images/bc-10.jpg", "categories": ["Accessories"], "subcategory": "Gem Stone Bracelets"},
    {"id": 30, "name_kh": "ខ្សៃដៃ - ", "name_en": "Gym Bracelet - ", "price": 5000, "image": "/static/images/gymblack1.jpg", "categories": ["Accessories"], "subcategory": "Gym Bracelet"},
    {"id": 31, "name_kh": "ខ្សៃដៃ - ", "name_en": "Gym Bracelet - ", "price": 5000, "image": "/static/images/gymblack2.jpg", "categories": ["Accessories"], "subcategory": "Gym Bracelet"},
    {"id": 32, "name_kh": "ខ្សៃដៃ - ", "name_en": "Gym Bracelet - ", "price": 5000, "image": "/static/images/gymsilver1.jpg", "categories": ["Accessories"], "subcategory": "Gym Bracelet"},
    {"id": 33, "name_kh": "ខ្សៃដៃ - ", "name_en": "Gym Bracelet - ", "price": 5000, "image": "/static/images/gymsilver2.jpg", "categories": ["Accessories"], "subcategory": "Gym Bracelet"},
    {"id": 34, "name_kh": "ខ្សៃដៃ - ", "name_en": "Gym Bracelet - ", "price": 5000, "image": "/static/images/gymgold1.jpg", "categories": ["Accessories"], "subcategory": "Gym Bracelet"},
    {"id": 35, "name_kh": "ខ្សៃដៃ - ", "name_en": "Gym Bracelet - ", "price": 5000, "image": "/static/images/gymgold2.jpg", "categories": ["Accessories"], "subcategory": "Gym Bracelet"},
    {"id": 36, "name_kh": "WWII Germany 01", "name_en": "WWII Germany 01", "price": 1250, "image": "/static/images/wwii-01.jpg", "categories": ["toy"], "subcategory": "Lego WWII"},
    {"id": 37, "name_kh": "WWII Germany 02", "name_en": "WWII Germany 02", "price": 1250, "image": "/static/images/wwii-02.jpg", "categories": ["toy"], "subcategory": "Lego WWII"},
    {"id": 38, "name_kh": "WWII Germany 03", "name_en": "WWII Germany 03", "price": 1250, "image": "/static/images/wwii-03.jpg", "categories": ["toy"], "subcategory": "Lego WWII"},
    {"id": 39, "name_kh": "WWII Germany 04", "name_en": "WWII Germany 04", "price": 1250, "image": "/static/images/wwii-04.jpg", "categories": ["toy"], "subcategory": "Lego WWII"},
    {"id": 40, "name_kh": "WWII Germany 05", "name_en": "WWII Germany 05", "price": 1250, "image": "/static/images/wwii-05.jpg", "categories": ["toy"], "subcategory": "Lego WWII"},
    {"id": 41, "name_kh": "WWII Germany 06", "name_en": "WWII Germany 06", "price": 1250, "image": "/static/images/wwii-06.jpg", "categories": ["toy"], "subcategory": "Lego WWII"},
    {"id": 42, "name_kh": "WWII USA 01", "name_en": "WWII USA 01", "price": 1250, "image": "/static/images/wwii-07.jpg", "categories": ["toy"], "subcategory": "Lego WWII"},
    {"id": 43, "name_kh": "WWII USA 02", "name_en": "WWII USA 02", "price": 1250, "image": "/static/images/wwii-08.jpg", "categories": ["toy"], "subcategory": "Lego WWII"},
    {"id": 44, "name_kh": "WWII USA 03", "name_en": "WWII USA 03", "price": 1250, "image": "/static/images/wwii-09.jpg", "categories": ["toy"], "subcategory": "Lego WWII"},
    {"id": 45, "name_kh": "WWII USA 04", "name_en": "WWII USA 04", "price": 1250, "image": "/static/images/wwii-10.jpg", "categories": ["toy"], "subcategory": "Lego WWII"},
    {"id": 46, "name_kh": "WWII USA 05", "name_en": "WWII USA 05", "price": 1250, "image": "/static/images/wwii-11.jpg", "categories": ["toy"], "subcategory": "Lego WWII"},
    {"id": 47, "name_kh": "WWII SOVIET 01", "name_en": "WWII SOVIET 01", "price": 1250, "image": "/static/images/wwii-12.jpg", "categories": ["toy"], "subcategory": "Lego WWII"},
    {"id": 48, "name_kh": "WWII SOVIET 02", "name_en": "WWII SOVIET 02", "price": 1250, "image": "/static/images/wwii-13.jpg", "categories": ["toy"], "subcategory": "Lego WWII"},
    {"id": 49, "name_kh": "WWII SOVIET 03", "name_en": "WWII SOVIET 03", "price": 1250, "image": "/static/images/wwii-14.jpg", "categories": ["toy"], "subcategory": "Lego WWII"},
    {"id": 50, "name_kh": "WWII SOVIET 04", "name_en": "WWII SOVIET 04", "price": 1250, "image": "/static/images/wwii-15.jpg", "categories": ["toy"], "subcategory": "Lego WWII"},
    {"id": 51, "name_kh": "WWII SOVIET 05", "name_en": "WWII SOVIET 05", "price": 1250, "image": "/static/images/wwii-16.jpg", "categories": ["toy"], "subcategory": "Lego WWII"},
    {"id": 52, "name_kh": "WWII SOVIET 06", "name_en": "WWII SOVIET 06", "price": 1250, "image": "/static/images/wwii-17.jpg", "categories": ["toy"], "subcategory": "Lego WWII"},
    {"id": 53, "name_kh": "WWII SOVIET 07", "name_en": "WWII SOVIET 07", "price": 1250, "image": "/static/images/wwii-18.jpg", "categories": ["toy"], "subcategory": "Lego WWII"},
    {"id": 54, "name_kh": "WWII SOVIET 08", "name_en": "WWII SOVIET 08", "price": 1250, "image": "/static/images/wwii-19.jpg", "categories": ["toy"], "subcategory": "Lego WWII"},
    {"id": 55, "name_kh": "ខ្សែដៃ - ក្បាលនាគប្រាក់", "name_en": "Dragon Bracelet - ", "price": 6000, "image": "/static/images/dragon01.jpg", "categories": ["Accessories"], "subcategory": "Dragon Bracelet"},
    {"id": 56, "name_kh": "ខ្សែដៃ - ក្បាលនាគប្រាក់", "name_en": "Dragon Bracelet - ", "price": 6000, "image": "/static/images/dragon10.jpg", "categories": ["Accessories"], "subcategory": "Dragon Bracelet"},
    {"id": 57, "name_kh": "ខ្សែដៃ - ក្បាលនាគប្រាក់", "name_en": "Dragon Bracelet - ", "price": 6000, "image": "/static/images/dragon03.jpg", "categories": ["Accessories"], "subcategory": "Dragon Bracelet"},
    {"id": 58, "name_kh": "ខ្សែដៃ - ក្បាលនាគប្រាក់", "name_en": "Dragon Bracelet - ", "price": 6000, "image": "/static/images/dragon05.jpg", "categories": ["Accessories"], "subcategory": "Dragon Bracelet"},
    {"id": 59, "name_kh": "ខ្សែដៃ - ក្បាលនាគប្រាក់", "name_en": "Dragon Bracelet - ", "price": 6000, "image": "/static/images/dragon07.jpg", "categories": ["Accessories"], "subcategory": "Dragon Bracelet"},
    {"id": 60, "name_kh": "ខ្សែដៃ - ក្បាលនាគប្រាក់", "name_en": "Dragon Bracelet - ", "price": 6000, "image": "/static/images/dragon04.jpg", "categories": ["Accessories"], "subcategory": "Dragon Bracelet"},
    {"id": 61, "name_kh": "ខ្សែដៃ - ក្បាលនាគប្រាក់", "name_en": "Dragon Bracelet - ", "price": 6000, "image": "/static/images/dragon07.jpg", "categories": ["Accessories"], "subcategory": "Dragon Bracelet"},
    {"id": 62, "name_kh": "ខ្សែដៃ - ក្បាលនាគប្រាក់", "name_en": "Dragon Bracelet - ", "price": 6000, "image": "/static/images/dragon08.jpg", "categories": ["Accessories"], "subcategory": "Dragon Bracelet"},
    {"id": 63, "name_kh": "ខ្សែដៃ - ក្បាលនាគប្រាក់", "name_en": "Dragon Bracelet - ", "price": 6000, "image": "/static/images/dragon09.jpg", "categories": ["Accessories"], "subcategory": "Dragon Bracelet"},
    {"id": 64, "name_kh": "ខ្សែដៃ - ក្បាលនាគប្រាក់", "name_en": "Dragon Bracelet - ", "price": 6000, "image": "/static/images/dragon10.jpg", "categories": ["Accessories"], "subcategory": "Dragon Bracelet"},
]

# --- Subcategories Map ---
subcategories_map = {
    "Accessories": ["Gym Bracelet", "Gem Stone Bracelet","Dragon Bracelet"],
    "LEGO Ninjago": ["Season 1", "Season 2", "Season 3", "Season 4", "Season 5", "Season 6", "Season 7", "Season 8"],
    "Keychain": ["Gun Keychains"],
    "Hot Sale": [],
    "Toy": ["Lego Ninjago", "Lego WWII", "Lego ទាហាន"]
}

# --- Routes ---

@app.route('/')
def home():
    language = request.args.get('lang', 'kh')
    cart = session.get('cart', [])
    return render_template('home.html', products=products, language=language, cart=cart, current_category=None, current_subcategory=None, subcategories=[])

@app.route('/category/<category_name>')
def category(category_name):
    language = request.args.get('lang', 'kh')
    filtered_products = [
        p for p in products
        if category_name in p.get('categories', [])
    ]
    subs = subcategories_map.get(category_name, [])
    cart = session.get('cart', [])
    return render_template(
        'home.html',
        products=filtered_products,
        language=language,
        cart=cart,
        current_category=category_name,
        current_subcategory=None,
        subcategories=subs
    )

@app.route('/subcategory/<subcategory_name>')
def subcategory(subcategory_name):
    language = request.args.get('lang', 'kh')
    filtered_products = [
        p for p in products
        if subcategory_name in p.get('subcategory', [])
    ]
    cart = session.get('cart', [])

    # Find main category
    main_category = None
    for category, subs in subcategories_map.items():
        if subcategory_name in subs:
            main_category = category
            break

    subs = subcategories_map.get(main_category, []) if main_category else []

    return render_template(
        'home.html',
        products=filtered_products,
        language=language,
        cart=cart,
        current_category=main_category,
        current_subcategory=subcategory_name,
        subcategories=subs
    )
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

@app.route('/add-to-cart', methods=["POST"])
def add_to_cart():
    product_id = int(request.form['product_id'])
    quantity = int(request.form['quantity'])
    product = next((p for p in products if p["id"] == product_id), None)

    if product:
        cart = session.get('cart', [])
        cart.append({"product": product, "quantity": quantity})
        session['cart'] = cart

    return jsonify({"success": True, "cart_count": len(session.get('cart', []))})

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

        # Telegram Bot
        bot_token = '7981426501:AAE7CInWMNE2_sz5DaCMuAcKmH8yji1YBqk'
        chat_id = 1098161879
        url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
        payload = {"chat_id": chat_id, "text": message, "parse_mode": "Markdown"}
        response = requests.post(url, data=payload)

        if response.status_code != 200:
            print("Telegram error:", response.text)

        session['cart'] = []
        return redirect(url_for('thank_you'))

    return render_template('checkout.html', language=language, cart=cart)

@app.route('/thankyou')
def thank_you():
    language = request.args.get('lang', 'kh')
    return render_template('thankyou.html', language=language)

if __name__ == '__main__':
    import os
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)