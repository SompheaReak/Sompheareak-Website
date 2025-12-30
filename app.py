import os
import time
import json
import re
import logging
from flask import Flask, request, redirect, url_for, jsonify, session, render_template_string
from flask_sqlalchemy import SQLAlchemy

# --- CONFIGURATION ---
# Set up logging to catch "Internal Server Errors" details
logging.basicConfig(level=logging.DEBUG)

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'dev_key_123')
ADMIN_PASS = os.environ.get('ADMIN_PASS', 'admin')

# --- DATABASE SETUP ---
basedir = os.path.abspath(os.path.dirname(__file__))
db_path = os.path.join(basedir, 'shop_v2.db')
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + db_path
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# --- MODELS ---
class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200))
    price = db.Column(db.Integer)
    image = db.Column(db.String(500))
    category = db.Column(db.String(100))
    subcategory = db.Column(db.String(200)) 
    stock = db.Column(db.Integer, default=999)

class Setting(db.Model):
    key = db.Column(db.String(50), primary_key=True)
    value = db.Column(db.String(50))

# --- TEMPLATES ---
# We use string replacement instead of Jinja blocks to avoid inheritance complexity in a single file
HTML_LAYOUT = """
<!DOCTYPE html>
<html>
<head>
    <title>LEGO Shop</title>
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <script src="https://cdn.tailwindcss.com"></script>
</head>
<body class="bg-gray-50 text-gray-900">
    <nav class="bg-white border-b p-4">
        <div class="max-w-7xl mx-auto flex justify-between">
            <h1 class="text-xl font-bold text-red-600">LEGO Market</h1>
            <div>
                <a href="/" class="mr-4 hover:underline">Home</a>
                <a href="/lego" class="mr-4 hover:underline">Themes</a>
                <a href="/admin/login" class="hover:underline">Admin</a>
            </div>
        </div>
    </nav>
    <div class="max-w-7xl mx-auto p-4">
        <!-- CONTENT_PLACEHOLDER -->
    </div>
</body>
</html>
"""

HOME_TEMPLATE = HTML_LAYOUT.replace("<!-- CONTENT_PLACEHOLDER -->", """
    <h2 class="text-2xl font-bold mb-6">All Products</h2>
    <div class="grid grid-cols-2 md:grid-cols-4 gap-4">
        {% for p in products %}
        <div class="bg-white p-4 rounded shadow">
            <img src="{{ p.image }}" class="w-full h-40 object-contain mb-2" onerror="this.src='https://placehold.co/200?text=No+Image'">
            <h3 class="font-bold">{{ p.name }}</h3>
            <p class="text-red-600 font-bold">${{ p.price }}</p>
            <span class="text-xs bg-gray-200 px-2 py-1 rounded">{{ p.category }}</span>
        </div>
        {% endfor %}
    </div>
""")

LEGO_TEMPLATE = HTML_LAYOUT.replace("<!-- CONTENT_PLACEHOLDER -->", """
    <h2 class="text-3xl font-bold mb-8 text-center uppercase tracking-widest">Collections</h2>

    {# Ninjago Section #}
    {% if data.ninjago_sorted %}
    <div class="mb-12">
        <h3 class="text-2xl font-bold mb-4 border-l-4 border-red-500 pl-3">NINJAGO</h3>
        {% for season, items in data.ninjago_sorted %}
            <div class="mb-6">
                <h4 class="text-lg font-semibold mb-2 text-gray-700">{{ season }}</h4>
                <div class="flex overflow-x-auto gap-4 pb-4">
                    {% for p in items %}
                    <div class="min-w-[200px] w-[200px] bg-white p-3 rounded border">
                        <img src="{{ p.image }}" class="w-full h-32 object-contain" onerror="this.src='https://placehold.co/200?text=Lego'">
                        <div class="mt-2">
                            <h5 class="text-sm font-bold truncate">{{ p.name }}</h5>
                            <p class="text-red-600 font-bold text-sm">${{ p.price }}</p>
                        </div>
                    </div>
                    {% endfor %}
                </div>
            </div>
        {% endfor %}
    </div>
    {% endif %}

    {# Other Sections #}
    {% for key, items in [('One Piece', data.one_piece), ('F1', data.f1), ('Military', data.military)] %}
        {% if items %}
        <div class="mb-12">
            <h3 class="text-2xl font-bold mb-4 border-l-4 border-blue-500 pl-3">{{ key }}</h3>
            <div class="flex overflow-x-auto gap-4 pb-4">
                {% for p in items %}
                <div class="min-w-[200px] w-[200px] bg-white p-3 rounded border">
                     <img src="{{ p.image }}" class="w-full h-32 object-contain" onerror="this.src='https://placehold.co/200?text={{ key }}'">
                     <div class="mt-2">
                        <h5 class="text-sm font-bold truncate">{{ p.name }}</h5>
                        <p class="text-red-600 font-bold text-sm">${{ p.price }}</p>
                    </div>
                </div>
                {% endfor %}
            </div>
        </div>
        {% endif %}
    {% endfor %}
""")

# --- HELPERS ---
MEM_CACHE = {"products": [], "last_sync": 0}

def get_data_fast(force=False):
    global MEM_CACHE
    now = time.time()
    if not force and MEM_CACHE["products"] and (now - MEM_CACHE["last_sync"] < 300):
        return MEM_CACHE["products"]
    
    # Use app context explicitly if needed, though usually fine inside routes
    all_p = Product.query.all()
    MEM_CACHE["products"] = all_p
    MEM_CACHE["last_sync"] = now
    return all_p

def natural_sort_key(s):
    return [int(text) if text.isdigit() else text.lower() for text in re.split('([0-9]+)', s)]

def organize_lego(products):
    data = {
        "ninjago": {},
        "one_piece": [],
        "f1": [],
        "sets": [],
        "military": [],
        "other": []
    }
    
    for p in products:
        cat_str = (p.category or "").lower()
        sub_str = (p.subcategory or "").lower()
        
        # 1. NINJAGO
        if "ninjago" in cat_str or "ninjago" in sub_str:
            season = "General"
            if p.subcategory:
                parts = p.subcategory.split(',') if ',' in p.subcategory else [p.subcategory]
                for part in parts:
                    clean_part = part.strip()
                    if "Season" in clean_part or "Dragon Rising" in clean_part or "Pilot" in clean_part:
                        season = clean_part
                        break
            
            if season not in data["ninjago"]: data["ninjago"][season] = []
            data["ninjago"][season].append(p)
        
        # 2. ONE PIECE
        elif "one piece" in sub_str or "anime" in cat_str: data["one_piece"].append(p)
        # 3. F1
        elif "formula 1" in sub_str or "f1" in sub_str: data["f1"].append(p)
        # 4. MILITARY
        elif "wwii" in sub_str or "military" in sub_str: data["military"].append(p)
        else: data["other"].append(p)

    sorted_seasons = sorted(data["ninjago"].keys(), key=natural_sort_key)
    data["ninjago_sorted"] = [(s, data["ninjago"][s]) for s in sorted_seasons]
    
    return data

# --- ROUTES ---

@app.route('/')
def home():
    try:
        all_p = get_data_fast()
        return render_template_string(HOME_TEMPLATE, products=all_p)
    except Exception as e:
        logging.error(f"Error in home: {e}")
        return f"Error: {str(e)}", 500

@app.route('/lego')
def lego_world():
    try:
        all_p = get_data_fast()
        lego_data = organize_lego(all_p)
        return render_template_string(LEGO_TEMPLATE, data=lego_data)
    except Exception as e:
        logging.error(f"Error in lego_world: {e}")
        return f"Error: {str(e)}", 500

@app.route('/api/sync', methods=['POST'])
def sync_catalog():
    try:
        data = request.json
        items = data.get('items', [])
        
        # Use simple ID set for checking existence
        existing_ids = {p.id for p in Product.query.with_entities(Product.id).all()}
        
        for item in items:
            try:
                # Validate critical fields
                if 'id' not in item or 'price' not in item:
                    continue

                # Handle Subcategory: JSON Array -> String
                sub = item.get('subcategory')
                if isinstance(sub, list):
                    sub = ",".join(sub)
                elif sub is None:
                    sub = ""
                
                # Handle Category List -> String
                cats = item.get('categories')
                cat_val = cats[0] if cats and isinstance(cats, list) and len(cats) > 0 else "General"

                name_val = item.get('name_kh') or item.get('name') or "Unknown Product"

                if item['id'] not in existing_ids:
                    new_p = Product(
                        id=int(item['id']),
                        name=name_val,
                        price=int(item['price']),
                        image=item.get('image', ''),
                        category=cat_val,
                        subcategory=sub
                    )
                    db.session.add(new_p)
                else:
                    # Optional: Update existing
                    p = Product.query.get(item['id'])
                    if p:
                        p.subcategory = sub
                        p.name = name_val
                        p.price = int(item['price'])
            except Exception as item_err:
                logging.warning(f"Skipping item {item.get('id')}: {item_err}")
                continue
                
        db.session.commit()
        get_data_fast(force=True)
        return jsonify(success=True, count=len(items))
    except Exception as e:
        db.session.rollback()
        logging.error(f"Sync Error: {e}")
        return jsonify(success=False, error=str(e)), 500

@app.route('/admin/login')
def admin_login():
    return "Admin Login Page (Placeholder)"

# --- INITIALIZATION ---
if __name__ == "__main__":
    with app.app_context():
        db.create_all()
        # Seed test data if empty
        if not Product.query.first():
            print("Seeding database...")
            db.session.add(Product(id=1, name="Test Lego", price=5000, category="Toy", subcategory="Lego Ninjago,Season 1"))
            db.session.commit()
            
    app.run(host="0.0.0.0", port=5000, debug=True)


