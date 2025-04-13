from flask import Flask, render_template, request, redirect, url_for

app = Flask(__name__)

# Dummy products data
products = [
    {
        "id": 1,
        "name_en": "M416 - Gold Plate",
        "name_kh": "M416 - ប្រាក់មាស",
        "price": 6000,
        "image": "/static/images/m416-gold.jpg",
        "categories": ["Keychain"]
    },
    {
        "id": 2,
        "name_en": "M416 - Default",
        "name_kh": "M416 - ពណ៌ដើម",
        "price": 6000,
        "image": "/static/images/m416-default.jpg",
        "categories": ["Keychain"]
    },
    {
        "id": 3,
        "name_en": "AKM - Gold Plate",
        "name_kh": "AKM - ប្រាក់មាស",
        "price": 6000,
        "image": "/static/images/akm-gold.jpg",
        "categories": ["Keychain"]
    },
    {
        "id": 4,
        "name_en": "AKM - Default",
        "name_kh": "AKM - ពណ៌ដើម",
        "price": 6000,
        "image": "/static/images/akm-default.jpg",
        "categories": ["Keychain"]
    },
     {
        "id": 5,
        "name_en": "Scar L - Default",
        "name_kh": "Scar L - ពណ៌ដើម",
        "price": 6000,
        "image": "/static/images/scarl-default.jpg",
        "categories": ["Keychain"]
    },
     {
        "id": 6,
        "name_en": "Bracelet",
        "name_kh": "Scar L - ពណ៌ដើម",
        "price": 6000,
        "image": "/static/images/Bracelet.jpg",
        "categories": ["Hot Sale"]
    },
     {
        "id": 7,
        "name_en": "Bracelet",
        "name_kh": "Scar L - ពណ៌ដើម",
        "price": 6000,
        "image": "/static/images/Bracelet.jpg",
        "categories": ["Hot Sale"]
    }, 
    {
        "id": 8,
        "name_en": "Bracelet",
        "name_kh": "Scar L - ពណ៌ដើម",
        "price": 6000,
        "image": "/static/images/Bracelet.jpg",
        "categories": ["Hot Sale"]
    },
     {
        "id": 9,
        "name_en": "Bracelet",
        "name_kh": "Scar L - ពណ៌ដើម",
        "price": 6000,
        "image": "/static/images/Bracelet.jpg",
        "categories": ["Hot Sale"]
    }
]

# Simple in-memory orders (not real database yet)
orders = []

@app.route('/')
def home():
    language = request.args.get('lang', 'en')
    return render_template('home.html', products=products, language=language)
@app.route('/category/<category_name>')
def category(category_name):
    language = request.args.get('lang', 'en')
    filtered_products = [product for product in products if category_name in product['categories']]
    return render_template('home.html', products=filtered_products, language=language)
@app.route('/product/<int:product_id>')
def product_detail(product_id):
    language = request.args.get('lang', 'en')
    product = next((item for item in products if item["id"] == product_id), None)
    return render_template('product.html', product=product, language=language)

@app.route('/cart')
def cart():
    return render_template('cart.html')

@app.route('/checkout', methods=["GET", "POST"])
def checkout():
    if request.method == "POST":
        name = request.form['name']
        phone = request.form['phone']
        address = request.form['address']
        orders.append({"name": name, "phone": phone, "address": address})
        return redirect(url_for('home'))
    return render_template('checkout.html')

if __name__ == '__main__':
    import os
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
    