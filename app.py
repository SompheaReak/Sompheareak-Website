import os
from flask import Flask, render_template, request, redirect, url_for, jsonify, session
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.secret_key = 'somphea_reak_studio_key'

# --- DATABASE SETUP ---
basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'shop.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name_kh = db.Column(db.String(200), nullable=False)
    price = db.Column(db.Integer, nullable=False)
    image = db.Column(db.String(500), nullable=False)
    categories_str = db.Column(db.String(500), default="") 
    subcategory_str = db.Column(db.String(500), default="") 
    stock = db.Column(db.Integer, default=10) # Manage this from Admin

# --- DATA IMPORT LOGIC ---
def seed_database():
    """Import your list from the file into the database"""
    if Product.query.first(): return # Stop if already imported
    
    # PASTE YOUR ENTIRE LIST OF CHARMS HERE
    catalog = [
           // --- Charm
    {"id": 1, "name_kh": "Silver Charm", "price": 400, "image": "/static/images/c01.jpg", "categories": ["Charm"]},
   
     // --- F1 LOGOS (1001 - 1015) ---
    {"id": 1100, "name_kh": "Classic F1 Logo", "price": 3000, "image": "/static/images/charm-f1–101.jpg", "categories": ["Class F1🏎️"]},
    {"id": 1191, "name_kh": "Classic F1", "price": 3000, "image": "/static/images/charm-chain-03.jpg", "categories": ["Class F1🏎️"]},
    {"id": 1192, "name_kh": "Classic F1 - Ferri", "price": 3000, "image": "/static/images/charm-f1-301.jpg", "categories": ["Class F1🏎️"]},
    {"id": 1193, "name_kh": "Classic F1 - Porsche", "price": 3000, "image": "/static/images/charm-f1-302.jpg", "categories": ["Class F1🏎️"]},
    {"id": 1194, "name_kh": "Classic F1 - BMW", "price": 3000, "image": "/static/images/charm-f1-303.jpg", "categories": ["Class F1🏎️"]},
    {"id": 1195, "name_kh": "Classic F1 - BMW", "price": 3000, "image": "/static/images/charm-f1-304.jpg", "categories": ["Class F1🏎️"]},
    
    {"id": 1101, "name_kh": "Classic F1 - Mercedes", "price": 3000, "image": "/static/images/cc15.jpg", "categories": ["Class F1🏎️"]},
    {"id": 1102, "name_kh": "Classic F1 - Ferrari", "price": 3000, "image": "/static/images/cc04.jpg", "categories": ["Class F1🏎️"]},
    {"id": 1103, "name_kh": "Classic F1 - Porsche", "price": 3000, "image": "/static/images/cc12.jpg", "categories": ["Class F1🏎️"]},
    {"id": 1104, "name_kh": "Classic F1 - BMW", "price": 3000, "image": "/static/images/cc06.jpg", "categories": ["Class F1🏎️"]},

     // --- Pink F1 
    {"id": 1200, "name_kh": "Pink F1 Logo", "price": 3000, "image": "/static/images/charm-f1-201.jpg", "categories": ["Pink F1🏎️"]},
    {"id": 1291, "name_kh": "Classic F1 - Mercedes", "price": 3000, "image": "/static/images/charm-chain-03.jpg", "categories": ["pink F1🏎️"]},
    {"id": 1292, "name_kh": "Classic F1 - Ferri", "price": 3000, "image": "/static/images/charm-f1-301.jpg", "categories": ["Pink F1🏎️"]},
    {"id": 1293, "name_kh": "Classic F1 - Porsche", "price": 3000, "image": "/static/images/charm-f1-302.jpg", "categories": ["Pink F1🏎️"]},
    {"id": 1294, "name_kh": "Classic F1 - BMW", "price": 3000, "image": "/static/images/charm-f1-303.jpg", "categories": ["Pink F1🏎️"]},
    {"id": 1295, "name_kh": "Classic F1 - BMW", "price": 3000, "image": "/static/images/charm-f1-304.jpg", "categories": ["Pink F1🏎️"]},

    {"id": 1201, "name_kh": "Pink F1 - Mercedes", "price": 3000, "image": "/static/images/charm-f1-202.jpg", "categories": ["Pink F1🏎️"]},
    {"id": 1202, "name_kh": "Pink F1 - Ferrari", "price": 3000, "image": "/static/images/charm-f1-203.jpg", "categories": ["Pink F1🏎️"]},
    {"id": 1203, "name_kh": "Pink F1 - Porsche", "price": 3000, "image": "/static/images/charm-f1-204.jpg", "categories": ["Pink F1🏎️"]},
    {"id": 1204, "name_kh": "Pink F1 - BMW", "price": 3000, "image": "/static/images/charm-f1-205.jpg", "categories": ["Pink F1🏎️"]},

     // --- CAR LOGOS (1001 - 1015) ---
    {"id": 1001, "name_kh": "Car Charm 01", "price": 3000, "image": "/static/images/cc01.jpg", "categories": ["Car Logo"]},
    {"id": 1002, "name_kh": "Car Charm 02", "price": 3000, "image": "/static/images/cc02.jpg", "categories": ["Car Logo"]},
    {"id": 1003, "name_kh": "Car Charm 03", "price": 3000, "image": "/static/images/cc03.jpg", "categories": ["Car Logo"]},
    {"id": 1004, "name_kh": "Car Charm 04", "price": 3000, "image": "/static/images/cc04.jpg", "categories": ["Car Logo"]},
    {"id": 1005, "name_kh": "Car Charm 05", "price": 3000, "image": "/static/images/cc05.jpg", "categories": ["Car Logo"]},
    {"id": 1006, "name_kh": "Car Charm 06", "price": 3000, "image": "/static/images/cc06.jpg", "categories": ["Car Logo"]},
    {"id": 1007, "name_kh": "Car Charm 07", "price": 3000, "image": "/static/images/cc07.jpg", "categories": ["Car Logo"]}, 
    {"id": 1008, "name_kh": "Car Charm 08", "price": 3000, "image": "/static/images/cc08.jpg", "categories": ["Car Logo"]},
    {"id": 1009, "name_kh": "Car Charm 09", "price": 3000, "image": "/static/images/cc09.jpg", "categories": ["Car Logo"]},
    {"id": 1010, "name_kh": "Car Charm 10", "price": 3000, "image": "/static/images/cc10.jpg", "categories": ["Car Logo"]},
    {"id": 1011, "name_kh": "Car Charm 11", "price": 3000, "image": "/static/images/cc11.jpg", "categories": ["Car Logo"]},
    {"id": 1012, "name_kh": "Car Charm 12", "price": 3000, "image": "/static/images/cc12.jpg", "categories": ["Car Logo"]},
    {"id": 1013, "name_kh": "Car Charm 13", "price": 3000, "image": "/static/images/cc13.jpg", "categories": ["Car Logo"]},
    {"id": 1014, "name_kh": "Car Charm 14", "price": 3000, "image": "/static/images/cc14.jpg", "categories": ["Car Logo"]},
    {"id": 1015, "name_kh": "Car Charm 15", "price": 3000, "image": "/static/images/cc15.jpg", "categories": ["Car Logo"]},
    // --- FLAGS (2001 - 2019) ---
    {"id": 2001, "name_kh": "Flag Charm 01", "price": 3000, "image": "/static/images/cf01.jpg", "categories": ["Flag"], "subcategory": ["All","Football"], "discount": 20},
    {"id": 2002, "name_kh": "Flag Charm 02", "price": 3000, "image": "/static/images/cf02.jpg", "categories": ["Flag"], "subcategory": ["Flag","Football"], "discount": 20},
    {"id": 2003, "name_kh": "Flag Charm 03", "price": 3000, "image": "/static/images/cf03.jpg", "categories": ["Flag"], "subcategory": ["All","Football"], "discount": 20},
    {"id": 2004, "name_kh": "Flag Charm 04", "price": 3000, "image": "/static/images/cf04.jpg", "categories": ["Flag"], "subcategory": ["Flag","Football"], "discount": 20},
    {"id": 2005, "name_kh": "Flag Charm 05", "price": 3000, "image": "/static/images/cf05.jpg", "categories": ["Flag"], "subcategory": ["Flag","Football"], "discount": 20},
    {"id": 2006, "name_kh": "Flag Charm 06", "price": 3000, "image": "/static/images/cf06.jpg", "categories": ["Flag"], "subcategory": ["Flag","Football"], "discount": 20},
    {"id": 2007, "name_kh": "Flag Charm 07", "price": 3000, "image": "/static/images/cf07.jpg", "categories": ["Flag"], "subcategory": ["Flag","Football"], "discount": 20},
    {"id": 2008, "name_kh": "Flag Charm 08", "price": 3000, "image": "/static/images/cf08.jpg", "categories": ["Flag"], "subcategory": ["All","Football"], "discount": 20},
    {"id": 2009, "name_kh": "Flag Charm 09", "price": 3000, "image": "/static/images/cf09.jpg", "categories": ["Flag"], "subcategory": ["All","Football"], "discount": 20},
    {"id": 2010, "name_kh": "Flag Charm 10", "price": 3000, "image": "/static/images/cf10.jpg", "categories": ["Flag"], "subcategory": ["All","Football"], "discount": 20},
    {"id": 2011, "name_kh": "Flag Charm 11", "price": 3000, "image": "/static/images/cf11.jpg", "categories": ["Flag"], "subcategory": ["All","Football"], "discount": 20},
    {"id": 2012, "name_kh": "Flag Charm 12", "price": 3000, "image": "/static/images/cf12.jpg", "categories": ["Flag"], "subcategory": ["All","Football"], "discount": 20},
    {"id": 2013, "name_kh": "Flag Charm 13", "price": 3000, "image": "/static/images/cf13.jpg", "categories": ["Flag"], "subcategory": ["All","Football"], "discount": 20},
    {"id": 2014, "name_kh": "Flag Charm 14", "price": 3000, "image": "/static/images/cf14.jpg", "categories": ["Flag"], "subcategory": ["All","Football"], "discount": 20},
    {"id": 2015, "name_kh": "Flag Charm 15", "price": 3000, "image": "/static/images/cf15.jpg", "categories": ["Flag"], "subcategory": ["All","Football"], "discount": 20},
    {"id": 2016, "name_kh": "Flag Charm 16", "price": 3000, "image": "/static/images/cf16.jpg", "categories": ["Flag"], "subcategory": ["Flag","Football"], "discount": 20},
    {"id": 2017, "name_kh": "Flag Charm 17", "price": 3000, "image": "/static/images/cf17.jpg", "categories": ["Flag"], "subcategory": ["Flag","Football"], "discount": 20},
    {"id": 2018, "name_kh": "Flag Charm 18", "price": 3000, "image": "/static/images/cf18.jpg", "categories": ["Flag"], "subcategory": ["All","Football"], "discount": 20},
    {"id": 2019, "name_kh": "Flag Charm 19", "price": 3000, "image": "/static/images/cf19.jpg", "categories": ["Flag"], "subcategory": ["All","Football"], "discount": 20},

    // --- GEMSTONES (3001 - 3024) ---
    {"id": 3001, "name_kh": "Gemstone Charm 01", "price": 3500, "image": "/static/images/cg01.jpg", "categories": ["Gemstone"], "subcategory": ["Car Logo"], "discount": 20},
    {"id": 3002, "name_kh": "Gemstone Charm 02", "price": 3500, "image": "/static/images/cg02.jpg", "categories": ["Gemstone"], "subcategory": ["All","Football"], "discount": 20},
    {"id": 3003, "name_kh": "Gemstone Charm 03", "price": 3500, "image": "/static/images/cg03.jpg", "categories": ["Gemstone"], "subcategory": ["All","Football"], "discount": 20},
    {"id": 3004, "name_kh": "Gemstone Charm 04", "price": 3500, "image": "/static/images/cg04.jpg", "categories": ["Gemstone"], "subcategory": ["All","Football"], "discount": 20},
    {"id": 3005, "name_kh": "Gemstone Charm 05", "price": 3500, "image": "/static/images/cg05.jpg", "categories": ["Gemstone"], "subcategory": ["All","Football"], "discount": 20},
    {"id": 3006, "name_kh": "Gemstone Charm 06", "price": 3500, "image": "/static/images/cg06.jpg", "categories": ["Gemstone"], "subcategory": ["Car Logo"], "discount": 20},
    {"id": 3007, "name_kh": "Gemstone Charm 07", "price": 3500, "image": "/static/images/cg07.jpg", "categories": ["Gemstone"], "subcategory": ["Car Logo"], "discount": 20},
    {"id": 3008, "name_kh": "Gemstone Charm 08", "price": 3500, "image": "/static/images/cg08.jpg", "categories": ["Gemstone"], "subcategory": ["All","Football"], "discount": 20},
    {"id": 3009, "name_kh": "Gemstone Charm 09", "price": 3500, "image": "/static/images/cg09.jpg", "categories": ["Gemstone"], "subcategory": ["All","Football"], "discount": 20},
    {"id": 3010, "name_kh": "Gemstone Charm 10", "price": 3500, "image": "/static/images/cg10.jpg", "categories": ["Gemstone"], "subcategory": ["All","Football"], "discount": 20},
    {"id": 3011, "name_kh": "Gemstone Charm 11", "price": 3500, "image": "/static/images/cg11.jpg", "categories": ["Gemstone"], "subcategory": ["All","Football"], "discount": 20},
    {"id": 3012, "name_kh": "Gemstone Charm 12", "price": 3500, "image": "/static/images/cg12.jpg", "categories": ["Gemstone"], "subcategory": ["All","Football"], "discount": 20},
    {"id": 3013, "name_kh": "Gemstone Charm 13", "price": 3500, "image": "/static/images/cg13.jpg", "categories": ["Gemstone"], "subcategory": ["All","Football"], "discount": 20},
    {"id": 3014, "name_kh": "Gemstone Charm 14", "price": 3500, "image": "/static/images/cg14.jpg", "categories": ["Gemstone"], "subcategory": ["All","Football"], "discount": 20},
    {"id": 3015, "name_kh": "Gemstone Charm 15", "price": 3500, "image": "/static/images/cg15.jpg", "categories": ["Gemstone"], "subcategory": ["All","Football"], "discount": 20},
    {"id": 3016, "name_kh": "Gemstone Charm 16", "price": 3500, "image": "/static/images/cg16.jpg", "categories": ["Gemstone"], "subcategory": ["Car Logo"], "discount": 20},
    {"id": 3017, "name_kh": "Gemstone Charm 17", "price": 3500, "image": "/static/images/cg17.jpg", "categories": ["Gemstone"], "subcategory": ["Car Logo"], "discount": 20},
    {"id": 3018, "name_kh": "Gemstone Charm 18", "price": 3500, "image": "/static/images/cg18.jpg", "categories": ["Gemstone"], "subcategory": ["All","Football"], "discount": 20},
    {"id": 3019, "name_kh": "Gemstone Charm 19", "price": 3500, "image": "/static/images/cg19.jpg", "categories": ["Gemstone"], "subcategory": ["All","Football"], "discount": 20},
    {"id": 3020, "name_kh": "Gemstone Charm 20", "price": 3500, "image": "/static/images/cg20.jpg", "categories": ["Gemstone"], "subcategory": ["All","Football"], "discount": 20},
    {"id": 3021, "name_kh": "Gemstone Charm 21", "price": 5000, "image": "/static/images/cg21.jpg", "categories": ["Gemstone"], "subcategory": ["Car Logo"], "discount": 20},
    {"id": 3022, "name_kh": "Gemstone Charm 22", "price": 5000, "image": "/static/images/cg22.jpg", "categories": ["Gemstone"], "subcategory": ["All","Football"], "discount": 20},
    {"id": 3023, "name_kh": "Gemstone Charm 23", "price": 5000, "image": "/static/images/cg23.jpg", "categories": ["Gemstone"], "subcategory": ["All","Football"], "discount": 20},
    {"id": 3024, "name_kh": "Gemstone Charm 24", "price": 5000, "image": "/static/images/cg24.jpg", "categories": ["Gemstone"], "subcategory": ["All","Football"], "discount": 20},

    // --- Chain (4001 - 4016) ---
    {"id": 4001, "name_kh": "Chain Charm 01", "price": 3000, "image": "/static/images/charm-chain-01.jpg", "categories": ["Chain"], "subcategory": ["All","Football"], "discount": 20},
    {"id": 4002, "name_kh": "Chain Charm 02", "price": 3000, "image": "/static/images/charm-chain-02.jpg", "categories": ["Chain"], "subcategory": ["Flag","Football"], "discount": 20},
    {"id": 4003, "name_kh": "Chain Charm 03", "price": 3000, "image": "/static/images/charm-chain-03.jpg", "categories": ["Chain"], "subcategory": ["All","Football"], "discount": 20},
    {"id": 4004, "name_kh": "Chain Charm 04", "price": 3000, "image": "/static/images/charm-chain-04.jpg", "categories": ["Chain"], "subcategory": ["Flag","Football"], "discount": 20},
    {"id": 4005, "name_kh": "Chain Charm 05", "price": 3000, "image": "/static/images/charm-chain-05.jpg", "categories": ["Chain"], "subcategory": ["All","Football"], "discount": 20},
    {"id": 4006, "name_kh": "Chain Charm 06", "price": 3000, "image": "/static/images/charm-chain-06.jpg", "categories": ["Chain"], "subcategory": ["Flag","Football"], "discount": 20},
    {"id": 4007, "name_kh": "Chain Charm 07", "price": 3000, "image": "/static/images/charm-chain-07.jpg", "categories": ["Chain"], "subcategory": ["All","Football"], "discount": 20},
    {"id": 4008, "name_kh": "Chain Charm 08", "price": 3000, "image": "/static/images/charm-chain-08.jpg", "categories": ["Chain"], "subcategory": ["Flag","Football"], "discount": 20},
    {"id": 4009, "name_kh": "Chain Charm 09", "price": 3000, "image": "/static/images/charm-chain-09.jpg", "categories": ["Chain"], "subcategory": ["All","Football"], "discount": 20},
    {"id": 4010, "name_kh": "Chain Charm 10", "price": 3000, "image": "/static/images/charm-chain-10.jpg", "categories": ["Chain"], "subcategory": ["Flag","Football"], "discount": 20},
    {"id": 4011, "name_kh": "Chain Charm 11", "price": 3000, "image": "/static/images/charm-chain-11.jpg", "categories": ["Chain"], "subcategory": ["All","Football"], "discount": 20},
    {"id": 4012, "name_kh": "Chain Charm 12", "price": 3000, "image": "/static/images/charm-chain-12.jpg", "categories": ["Chain"], "subcategory": ["Flag","Football"], "discount": 20},
    {"id": 4013, "name_kh": "Chain Charm 13", "price": 3000, "image": "/static/images/charm-chain-13.jpg", "categories": ["Chain"], "subcategory": ["All","Football"], "discount": 20},
    {"id": 4014, "name_kh": "Chain Charm 14", "price": 3000, "image": "/static/images/charm-chain-14.jpg", "categories": ["Chain"], "subcategory": ["Flag","Football"], "discount": 20},
    {"id": 4015, "name_kh": "Chain Charm 15", "price": 3000, "image": "/static/images/charm-chain-15.jpg", "categories": ["Chain"], "subcategory": ["All","Football"], "discount": 20},
    {"id": 4016, "name_kh": "Chain Charm 16", "price": 3000, "image": "/static/images/charm-chain-16.jpg", "categories": ["Chain"], "subcategory": ["Flag","Football"], "discount": 20},

    // --- Football Club (5001 - 5015) ---
    {"id": 5001, "name_kh": "Barcelona", "price": 3000, "image": "/static/images/charm-footballclub-01.jpg", "categories": ["Football Club Logo"]},
    {"id": 5002, "name_kh": "Real Madrid", "price": 3000, "image": "/static/images/charm-footballclub-02.jpg", "categories": ["Football Club Logo"]},
    {"id": 5003, "name_kh": "Barcelona", "price": 3000, "image": "/static/images/charm-footballclub-03.jpg", "categories": ["Football Club Logo"]},
    {"id": 5004, "name_kh": "Barcelona", "price": 3000, "image": "/static/images/charm-footballclub-04.jpg", "categories": ["Football Club Logo"]},
    {"id": 5005, "name_kh": "Barcelona", "price": 3000, "image": "/static/images/charm-footballclub-05.jpg", "categories": ["Football Club Logo"]},
    {"id": 5006, "name_kh": "Barcelona", "price": 3000, "image": "/static/images/charm-footballclub-06.jpg", "categories": ["Football Club Logo"]},
    {"id": 5007, "name_kh": "Barcelona", "price": 3000, "image": "/static/images/charm-footballclub-07.jpg", "categories": ["Football Club Logo"]},
    {"id": 5008, "name_kh": "Barcelona", "price": 3000, "image": "/static/images/charm-footballclub-08.jpg", "categories": ["Football Club Logo"]},
    {"id": 5009, "name_kh": "Barcelona", "price": 3000, "image": "/static/images/charm-footballclub-09.jpg", "categories": ["Football Club Logo"]},
    {"id": 5010, "name_kh": "Barcelona", "price": 3000, "image": "/static/images/charm-footballclub-10.jpg", "categories": ["Football Club Logo"]},
    {"id": 5011, "name_kh": "Barcelona", "price": 3000, "image": "/static/images/charm-footballclub-11.jpg", "categories": ["Football Club Logo"]},
    {"id": 5012, "name_kh": "Barcelona", "price": 3000, "image": "/static/images/charm-footballclub-12.jpg", "categories": ["Football Club Logo"]},
    {"id": 5013, "name_kh": "Barcelona", "price": 3000, "image": "/static/images/charm-footballclub-13.jpg", "categories": ["Football Club Logo"]},
    {"id": 5014, "name_kh": "Barcelona", "price": 3000, "image": "/static/images/charm-footballclub-14.jpg", "categories": ["Football Club Logo"]},
    {"id": 5015, "name_kh": "Barcelona", "price": 3000, "image": "/static/images/charm-footballclub-15.jpg", "categories": ["Football Club Logo"]},

    // --- Black Lover (6001 - 6007) ---
    {"id": 6001, "name_kh": "Black Charm 01", "price": 3000, "image": "/static/images/cb01.jpg", "categories": ["Black Lover"], "subcategory": ["All","Football"], "discount": 20},
    {"id": 6002, "name_kh": "Black Charm 02", "price": 3000, "image": "/static/images/cb02.jpg", "categories": ["Black Lover"], "subcategory": ["Flag","Football"], "discount": 20},
    {"id": 6003, "name_kh": "Black Charm 03", "price": 3000, "image": "/static/images/cb03.jpg", "categories": ["Black Lover"], "subcategory": ["All","Football"], "discount": 20},
    {"id": 6004, "name_kh": "Black Charm 04", "price": 3000, "image": "/static/images/cb04.jpg", "categories": ["Black Lover"], "subcategory": ["Flag","Football"], "discount": 20},
    {"id": 6005, "name_kh": "Black Charm 05", "price": 3000, "image": "/static/images/cb05.jpg", "categories": ["Black Lover"], "subcategory": ["Flag","Football"], "discount": 20},
    {"id": 6006, "name_kh": "Black Charm 06", "price": 3000, "image": "/static/images/cb06.jpg", "categories": ["Black Lover"], "subcategory": ["Flag","Football"], "discount": 20},
    {"id": 6007, "name_kh": "Black Charm 07", "price": 3000, "image": "/static/images/cb07.jpg", "categories": ["Black Lover"], "subcategory": ["Flag","Football"], "discount": 20},

    // --- Dog&Cat Lover (7001 - 7007) ---
    {"id": 7001, "name_kh": "Cat&Dog Charm 01", "price": 3000, "image": "/static/images/charm-animal-01.jpg", "categories": ["Dog&Cat Lover"], "subcategory": ["All","Football"], "discount": 20},
    {"id": 7002, "name_kh": "Cat&Dog Charm 02", "price": 3000, "image": "/static/images/charm-animal-02.jpg", "categories": ["Dog&Cat Lover"], "subcategory": ["Flag","Football"], "discount": 20},
    {"id": 7003, "name_kh": "Cat&Dog Charm 03", "price": 3000, "image": "/static/images/charm-animal-03.jpg", "categories": ["Dog&Cat Lover"], "subcategory": ["All","Football"], "discount": 20},
    {"id": 7004, "name_kh": "Cat&Dog Charm 04", "price": 3000, "image": "/static/images/charm-animal-04.jpg", "categories": ["Dog&Cat Lover"], "subcategory": ["Flag","Football"], "discount": 20},
    {"id": 7005, "name_kh": "Cat&Dog Charm 05", "price": 3000, "image": "/static/images/charm-animal-05.jpg", "categories": ["Dog&Cat Lover"], "subcategory": ["Flag","Football"], "discount": 20},
    {"id": 7006, "name_kh": "Cat&Dog Charm 06", "price": 3000, "image": "/static/images/charm-animal-06.jpg", "categories": ["Dog&Cat Lover"], "subcategory": ["Flag","Football"], "discount": 20},
    {"id": 7007, "name_kh": "Cat&Dog Charm 07", "price": 3000, "image": "/static/images/charm-animal-07.jpg", "categories": ["Dog&Cat Lover"], "subcategory": ["Flag","Football"], "discount": 20},
    // --- Blue Sea Lover (7011-7025) ---
    {"id": 7011, "name_kh": "Blue Sea Lover 01", "price": 3000, "image": "/static/images/charm-bluesealover-01.jpg", "categories": ["Blue Sea Lover🌊"], "subcategory": ["All","Football"], "discount": 20},
    {"id": 7012, "name_kh": "Blue Sea Lover 02", "price": 3000, "image": "/static/images/charm-bluesealover-02.jpg", "categories": ["Blue Sea Lover🌊"], "subcategory": ["Flag","Football"], "discount": 20},
    {"id": 7013, "name_kh": "Blue Sea Lover 03", "price": 3000, "image": "/static/images/charm-bluesealover-03.jpg", "categories": ["Blue Sea Lover🌊"], "subcategory": ["All","Football"], "discount": 20},
    {"id": 7014, "name_kh": "Blue Sea Lover 04", "price": 3000, "image": "/static/images/charm-bluesealover-04.jpg", "categories": ["Blue Sea Lover🌊"], "subcategory": ["Flag","Football"], "discount": 20},
    {"id": 7015, "name_kh": "Blue Sea Lover 05", "price": 3000, "image": "/static/images/charm-bluesealover-05.jpg", "categories": ["Blue Sea Lover🌊"], "subcategory": ["Flag","Football"], "discount": 20},
    {"id": 7016, "name_kh": "Blue Sea Lover 06", "price": 3000, "image": "/static/images/charm-bluesealover-06.jpg", "categories": ["Blue Sea Lover🌊"], "subcategory": ["Flag","Football"], "discount": 20},
    {"id": 7017, "name_kh": "Blue Sea Lover 07", "price": 3000, "image": "/static/images/charm-bluesealover-07.jpg", "categories": ["Blue Sea Lover🌊"], "subcategory": ["Flag","Football"], "discount": 20},
    {"id": 7018, "name_kh": "Blue Sea Lover 08", "price": 3000, "image": "/static/images/charm-bluesealover-08.jpg", "categories": ["Blue Sea Lover🌊"], "subcategory": ["All","Football"], "discount": 20},
    {"id": 7019, "name_kh": "Blue Sea Lover 09", "price": 3000, "image": "/static/images/charm-bluesealover-09.jpg", "categories": ["Blue Sea Lover🌊"], "subcategory": ["Flag","Football"], "discount": 20},
    {"id": 7020, "name_kh": "Blue Sea Lover 10", "price": 3000, "image": "/static/images/charm-bluesealover-10.jpg", "categories": ["Blue Sea Lover🌊"], "subcategory": ["All","Football"], "discount": 20},
    {"id": 7021, "name_kh": "Blue Sea Lover 11", "price": 3000, "image": "/static/images/charm-bluesealover-11.jpg", "categories": ["Blue Sea Lover🌊"], "subcategory": ["Flag","Football"], "discount": 20},
    {"id": 7022, "name_kh": "Blue Sea Lover 12", "price": 3000, "image": "/static/images/charm-bluesealover-12.jpg", "categories": ["Blue Sea Lover🌊"], "subcategory": ["Flag","Football"], "discount": 20},
    {"id": 7023, "name_kh": "Blue Sea Lover 13", "price": 3000, "image": "/static/images/charm-bluesealover-13.jpg", "categories": ["Blue Sea Lover🌊"], "subcategory": ["Flag","Football"], "discount": 20},
    {"id": 7024, "name_kh": "Blue Sea Lover 14", "price": 3000, "image": "/static/images/charm-bluesealover-14.jpg", "categories": ["Blue Sea Lover🌊"], "subcategory": ["Flag","Football"], "discount": 20},
    {"id": 7025, "name_kh": "Blue Sea Lover 15", "price": 3000, "image": "/static/images/charm-bluesealover-15.jpg", "categories": ["Blue Sea Lover🌊"], "subcategory": ["Flag","Football"], "discount": 20},

    // --- Pink Lover (8001 - 8009) ---
    {"id": 8001, "name_kh": "Pink Charm 01", "price": 3000, "image": "/static/images/cp01.jpg", "categories": ["Pink Lover"], "subcategory": ["All","Football"], "discount": 20},
    {"id": 8002, "name_kh": "Pink Charm 02", "price": 3000, "image": "/static/images/cp02.jpg", "categories": ["Pink Lover"], "subcategory": ["Flag","Football"], "discount": 20},
    {"id": 8003, "name_kh": "Pink Charm 03", "price": 3000, "image": "/static/images/cp03.jpg", "categories": ["Pink Lover"], "subcategory": ["All","Football"], "discount": 20},
    {"id": 8004, "name_kh": "Pink Charm 04", "price": 3000, "image": "/static/images/cp04.jpg", "categories": ["Pink Lover"], "subcategory": ["Flag","Football"], "discount": 20},
    {"id": 8005, "name_kh": "Pink Charm 05", "price": 3000, "image": "/static/images/cp05.jpg", "categories": ["Pink Lover"], "subcategory": ["Flag","Football"], "discount": 20},
    {"id": 8006, "name_kh": "Pink Charm 06", "price": 3000, "image": "/static/images/cp06.jpg", "categories": ["Pink Lover"], "subcategory": ["Flag","Football"], "discount": 20},
    {"id": 8007, "name_kh": "Pink Charm 07", "price": 3000, "image": "/static/images/cp07.jpg", "categories": ["Pink Lover"], "subcategory": ["Flag","Football"], "discount": 20},
    {"id": 8008, "name_kh": "Pink Charm 08", "price": 3000, "image": "/static/images/cp08.jpg", "categories": ["Pink Lover"], "subcategory": ["Flag","Football"], "discount": 20},
    {"id": 8009, "name_kh": "Pink Charm 09", "price": 3000, "image": "/static/images/cp09.jpg", "categories": ["Pink Lover"], "subcategory": ["Flag","Football"], "discount": 20},
 
    // --- PINK LETTERS (9001 - 9026) ---
    {"id": 9001, "name_kh": "Pink Letter Charm A", "price": 1200, "image": "/static/images/ap.jpg", "categories": ["Pink Letter"], "subcategory": ["All","Football"], "discount": 20},
    {"id": 9002, "name_kh": "Pink Letter Charm B", "price": 1200, "image": "/static/images/bp.jpg", "categories": ["Pink Letter"], "subcategory": ["Flag","Football"], "discount": 20},
    {"id": 9003, "name_kh": "Pink Letter Charm C", "price": 1200, "image": "/static/images/cp.jpg", "categories": ["Pink Letter"], "subcategory": ["All","Football"], "discount": 20},
    {"id": 9004, "name_kh": "Pink Letter Charm D", "price": 1200, "image": "/static/images/dp.jpg", "categories": ["Pink Letter"], "subcategory": ["Flag","Football"], "discount": 20},
    {"id": 9005, "name_kh": "Pink Letter Charm E", "price": 1200, "image": "/static/images/ep.jpg", "categories": ["Pink Letter"], "subcategory": ["Flag","Football"], "discount": 20},
    {"id": 9006, "name_kh": "Pink Letter Charm F", "price": 1200, "image": "/static/images/fp.jpg", "categories": ["Pink Letter"], "subcategory": ["Flag","Football"], "discount": 20},
    {"id": 9007, "name_kh": "Pink Letter Charm G", "price": 1200, "image": "/static/images/gp.jpg", "categories": ["Pink Letter"], "subcategory": ["Flag","Football"], "discount": 20},
    {"id": 9008, "name_kh": "Pink Letter Charm H", "price": 1200, "image": "/static/images/hp.jpg", "categories": ["Pink Letter"], "subcategory": ["All","Football"], "discount": 20},
    {"id": 9009, "name_kh": "Pink Letter Charm I", "price": 1200, "image": "/static/images/ip.jpg", "categories": ["Pink Letter"], "subcategory": ["All","Football"], "discount": 20},
    {"id": 9010, "name_kh": "Pink Letter Charm J", "price": 1200, "image": "/static/images/jp.jpg", "categories": ["Pink Letter"], "subcategory": ["All","Football"], "discount": 20},
    {"id": 9011, "name_kh": "Pink Letter Charm K", "price": 1200, "image": "/static/images/kp.jpg", "categories": ["Pink Letter"], "subcategory": ["All","Football"], "discount": 20},
    {"id": 9012, "name_kh": "Pink Letter Charm L", "price": 1200, "image": "/static/images/lp.jpg", "categories": ["Pink Letter"], "subcategory": ["All","Football"], "discount": 20},
    {"id": 9013, "name_kh": "Pink Letter Charm M", "price": 1200, "image": "/static/images/mp.jpg", "categories": ["Pink Letter"], "subcategory": ["All","Football"], "discount": 20},
    {"id": 9014, "name_kh": "Pink Letter Charm N", "price": 1200, "image": "/static/images/np.jpg", "categories": ["Pink Letter"], "subcategory": ["All","Football"], "discount": 20},
    {"id": 9015, "name_kh": "Pink Letter Charm O", "price": 1200, "image": "/static/images/op.jpg", "categories": ["Pink Letter"], "subcategory": ["All","Football"], "discount": 20},
    {"id": 9016, "name_kh": "Pink Letter Charm P", "price": 1200, "image": "/static/images/pp.jpg", "categories": ["Pink Letter"], "subcategory": ["Flag","Football"], "discount": 20},
    {"id": 9017, "name_kh": "Pink Letter Charm Q", "price": 1200, "image": "/static/images/qp.jpg", "categories": ["Pink Letter"], "subcategory": ["Flag","Football"], "discount": 20},
    {"id": 9018, "name_kh": "Pink Letter Charm R", "price": 1200, "image": "/static/images/rp.jpg", "categories": ["Pink Letter"], "subcategory": ["All","Football"], "discount": 20},
    {"id": 9019, "name_kh": "Pink Letter Charm S", "price": 1200, "image": "/static/images/sp.jpg", "categories": ["Pink Letter"], "subcategory": ["All","Football"], "discount": 20},
    {"id": 9020, "name_kh": "Pink Letter Charm T", "price": 1200, "image": "/static/images/tp.jpg", "categories": ["Pink Letter"], "subcategory": ["All","Football"], "discount": 20},
    {"id": 9021, "name_kh": "Pink Letter Charm U", "price": 1200, "image": "/static/images/up.jpg", "categories": ["Pink Letter"], "subcategory": ["All","Football"], "discount": 20},
    {"id": 9022, "name_kh": "Pink Letter Charm V", "price": 1200, "image": "/static/images/vp.jpg", "categories": ["Pink Letter"], "subcategory": ["All","Football"], "discount": 20},
    {"id": 9023, "name_kh": "Pink Letter Charm W", "price": 1200, "image": "/static/images/wp.jpg", "categories": ["Pink Letter"], "subcategory": ["Flag","Football"], "discount": 20},
    {"id": 9024, "name_kh": "Pink Letter Charm X", "price": 1200, "image": "/static/images/xp.jpg", "categories": ["Pink Letter"], "subcategory": ["Flag","Football"], "discount": 20},
    {"id": 9025, "name_kh": "Pink Letter Charm Y", "price": 1200, "image": "/static/images/yp.jpg", "categories": ["Pink Letter"], "subcategory": ["All","Football"], "discount": 20},
    {"id": 9026, "name_kh": "Pink Letter Charm Z", "price": 1200, "image": "/static/images/zp.jpg", "categories": ["Pink Letter"], "subcategory": ["All","Football"], "discount": 20},

    // --- SILVER/GOLD LETTERS (1101 - 1126) ---
    {"id": 1101, "name_kh": "Letter Charm A", "price": 1200, "image": "/static/images/a.jpg", "categories": ["Letter"], "subcategory": ["All","Football"], "discount": 20},
    {"id": 1102, "name_kh": "Letter Charm B", "price": 1200, "image": "/static/images/b.jpg", "categories": ["Letter"], "subcategory": ["Flag","Football"], "discount": 20},
    {"id": 1103, "name_kh": "Letter Charm C", "price": 1200, "image": "/static/images/c.jpg", "categories": ["Letter"], "subcategory": ["All","Football"], "discount": 20},
    {"id": 1104, "name_kh": "Letter Charm D", "price": 1200, "image": "/static/images/d.jpg", "categories": ["Letter"], "subcategory": ["Flag","Football"], "discount": 20},
    {"id": 1105, "name_kh": "Letter Charm E", "price": 1200, "image": "/static/images/e.jpg", "categories": ["Letter"], "subcategory": ["Flag","Football"], "discount": 20},
    {"id": 1106, "name_kh": "Letter Charm F", "price": 1200, "image": "/static/images/f.jpg", "categories": ["Letter"], "subcategory": ["Flag","Football"], "discount": 20},
    {"id": 1107, "name_kh": "Letter Charm G", "price": 1200, "image": "/static/images/g.jpg", "categories": ["Letter"], "subcategory": ["Flag","Football"], "discount": 20},
    {"id": 1108, "name_kh": "Letter Charm H", "price": 1200, "image": "/static/images/h.jpg", "categories": ["Letter"], "subcategory": ["All","Football"], "discount": 20},
    {"id": 1109, "name_kh": "Letter Charm I", "price": 1200, "image": "/static/images/i.jpg", "categories": ["Letter"], "subcategory": ["All","Football"], "discount": 20},
    {"id": 1110, "name_kh": "Letter Charm J", "price": 1200, "image": "/static/images/j.jpg", "categories": ["Letter"], "subcategory": ["All","Football"], "discount": 20},
    {"id": 1111, "name_kh": "Letter Charm K", "price": 1200, "image": "/static/images/k.jpg", "categories": ["Letter"], "subcategory": ["All","Football"], "discount": 20},
    {"id": 1112, "name_kh": "Letter Charm L", "price": 1200, "image": "/static/images/l.jpg", "categories": ["Letter"], "subcategory": ["All","Football"], "discount": 20},
    {"id": 1113, "name_kh": "Letter Charm M", "price": 1200, "image": "/static/images/m.jpg", "categories": ["Letter"], "subcategory": ["All","Football"], "discount": 20},
    {"id": 1114, "name_kh": "Letter Charm N", "price": 1200, "image": "/static/images/n.jpg", "categories": ["Letter"], "subcategory": ["All","Football"], "discount": 20},
    {"id": 1115, "name_kh": "Letter Charm O", "price": 1200, "image": "/static/images/o.jpg", "categories": ["Letter"], "subcategory": ["All","Football"], "discount": 20},
    {"id": 1116, "name_kh": "Letter Charm P", "price": 1200, "image": "/static/images/p.jpg", "categories": ["Letter"], "subcategory": ["Flag","Football"], "discount": 20},
    {"id": 1117, "name_kh": "Letter Charm Q", "price": 1200, "image": "/static/images/q.jpg", "categories": ["Letter"], "subcategory": ["Flag","Football"], "discount": 20},
    {"id": 1118, "name_kh": "Letter Charm R", "price": 1200, "image": "/static/images/r.jpg", "categories": ["Letter"], "subcategory": ["All","Football"], "discount": 20},
    {"id": 1119, "name_kh": "Letter Charm S", "price": 1200, "image": "/static/images/s.jpg", "categories": ["Letter"], "subcategory": ["All","Football"], "discount": 20},
    {"id": 1120, "name_kh": "Letter Charm T", "price": 1200, "image": "/static/images/t.jpg", "categories": ["Letter"], "subcategory": ["All","Football"], "discount": 20},
    {"id": 1121, "name_kh": "Letter Charm U", "price": 1200, "image": "/static/images/u.jpg", "categories": ["Letter"], "subcategory": ["All","Football"], "discount": 20},
    {"id": 1122, "name_kh": "Letter Charm V", "price": 1200, "image": "/static/images/v.jpg", "categories": ["Letter"], "subcategory": ["All","Football"], "discount": 20},
    {"id": 1123, "name_kh": "Letter Charm W", "price": 1200, "image": "/static/images/w.jpg", "categories": ["Letter"], "subcategory": ["Flag","Football"], "discount": 20},
    {"id": 1124, "name_kh": "Letter Charm X", "price": 1200, "image": "/static/images/x.jpg", "categories": ["Letter"], "subcategory": ["Flag","Football"], "discount": 20},
    {"id": 1125, "name_kh": "Letter Charm Y", "price": 1200, "image": "/static/images/y.jpg", "categories": ["Letter"], "subcategory": ["All","Football"], "discount": 20},
    {"id": 1126, "name_kh": "Letter Charm Z", "price": 1200, "image": "/static/images/z.jpg", "categories": ["Letter"], "subcategory": ["All","Football"], "discount": 20},

    // --- STEAV (1201 - 1213) ---
    {"id": 1201, "name_kh": "Steav Charm 01", "price": 3000, "image": "/static/images/cm01.jpg", "categories": ["Steav"], "subcategory": ["Car Logo"], "discount": 20},
    {"id": 1202, "name_kh": "Steav Charm 02", "price": 3000, "image": "/static/images/cm02.jpg", "categories": ["Steav"], "subcategory": ["All","Football"], "discount": 20},
    {"id": 1203, "name_kh": "Steav Charm 03", "price": 3000, "image": "/static/images/cm03.jpg", "categories": ["Steav"], "subcategory": ["All","Football"], "discount": 20},
    {"id": 1204, "name_kh": "Steav Charm 04", "price": 3000, "image": "/static/images/cm04.jpg", "categories": ["Steav"], "subcategory": ["All","Football"], "discount": 20},
    {"id": 1205, "name_kh": "Steav Charm 05", "price": 3000, "image": "/static/images/cm05.jpg", "categories": ["Steav"], "subcategory": ["All","Football"], "discount": 20},
    {"id": 1206, "name_kh": "Steav Charm 06", "price": 3000, "image": "/static/images/cm06.jpg", "categories": ["Steav"], "subcategory": ["Car Logo"], "discount": 20},
    {"id": 1207, "name_kh": "Steav Charm 07", "price": 3000, "image": "/static/images/cm07.jpg", "categories": ["Steav"], "subcategory": ["Car Logo"], "discount": 20},
    {"id": 1208, "name_kh": "Steav Charm 08", "price": 3000, "image": "/static/images/cm08.jpg", "categories": ["Steav"], "subcategory": ["All","Football"], "discount": 20},
    {"id": 1209, "name_kh": "Steav Charm 09", "price": 3000, "image": "/static/images/cm09.jpg", "categories": ["Steav"], "subcategory": ["All","Football"], "discount": 20},
    {"id": 1210, "name_kh": "Steav Charm 10", "price": 3000, "image": "/static/images/cm10.jpg", "categories": ["Steav"], "subcategory": ["All","Football"], "discount": 20},
    {"id": 1211, "name_kh": "Steav Charm 11", "price": 3000, "image": "/static/images/cm11.jpg", "categories": ["Steav"], "subcategory": ["All","Football"], "discount": 20},
    {"id": 1212, "name_kh": "Steav Charm 12", "price": 3000, "image": "/static/images/cm12.jpg", "categories": ["Steav"], "subcategory": ["All","Football"], "discount": 20},
    {"id": 1213, "name_kh": "Steav Charm 13", "price": 4000, "image": "/static/images/cm13.jpg", "categories": ["Steav"], "subcategory": ["All","Football"], "discount": 20},
    
    // --- Cartoon (1301) ---
    {"id": 1301, "name_kh": "Cartoon Charm", "price": 3000, "image": "/static/images/ct01.jpg", "categories": ["Cartoon"]},

    // --- CUTIE (1401 - 1416) ---
    {"id": 1401, "name_kh": "Cutie Charm 01", "price": 3000, "image": "/static/images/cw01.jpg", "categories": ["Cutie"], "subcategory": ["Car Logo"], "discount": 20},
    {"id": 1402, "name_kh": "Cutie Charm 02", "price": 3000, "image": "/static/images/cw02.jpg", "categories": ["Cutie"], "subcategory": ["All","Football"], "discount": 20},
    {"id": 1403, "name_kh": "Cutie Charm 03", "price": 3000, "image": "/static/images/cw03.jpg", "categories": ["Cutie"], "subcategory": ["All","Football"], "discount": 20},
    {"id": 1404, "name_kh": "Cutie Charm 04", "price": 3000, "image": "/static/images/cw04.jpg", "categories": ["Cutie"], "subcategory": ["All","Football"], "discount": 20},
    {"id": 1405, "name_kh": "Cutie Charm 05", "price": 3000, "image": "/static/images/cw05.jpg", "categories": ["Cutie"], "subcategory": ["All","Football"], "discount": 20},
    {"id": 1406, "name_kh": "Cutie Charm 06", "price": 4000, "image": "/static/images/cw06.jpg", "categories": ["Cutie"], "subcategory": ["Car Logo"], "discount": 20},
    {"id": 1407, "name_kh": "Cutie Charm 07", "price": 4000, "image": "/static/images/cw07.jpg", "categories": ["Cutie"], "subcategory": ["Car Logo"], "discount": 20},
    {"id": 1408, "name_kh": "Cutie Charm 08", "price": 4000, "image": "/static/images/cw08.jpg", "categories": ["Cutie"], "subcategory": ["All","Football"], "discount": 20},
    {"id": 1409, "name_kh": "Cutie Charm 09", "price": 4000, "image": "/static/images/cw09.jpg", "categories": ["Cutie"], "subcategory": ["All","Football"], "discount": 20},
    {"id": 1410, "name_kh": "Cutie Charm 10", "price": 4000, "image": "/static/images/cw10.jpg", "categories": ["Cutie"], "subcategory": ["All","Football"], "discount": 20}, 
    {"id": 1411, "name_kh": "Cutie Charm 11", "price": 4000, "image": "/static/images/cw11.jpg", "categories": ["Cutie"], "subcategory": ["All","Football"], "discount": 20},
    {"id": 1412, "name_kh": "Cutie Charm 12", "price": 4000, "image": "/static/images/cw12.jpg", "categories": ["Cutie"], "subcategory": ["All","Football"], "discount": 20},
    {"id": 1413, "name_kh": "Cutie Charm 13", "price": 4000, "image": "/static/images/cw13.jpg", "categories": ["Cutie"], "subcategory": ["All","Football"], "discount": 20},
    {"id": 1414, "name_kh": "Cutie Charm 14", "price": 4000, "image": "/static/images/cw14.jpg", "categories": ["Cutie"], "subcategory": ["All","Football"], "discount": 20},
    {"id": 1415, "name_kh": "Cutie Charm 15", "price": 4000, "image": "/static/images/cw15.jpg", "categories": ["Cutie"], "subcategory": ["All","Football"], "discount": 20},
    {"id": 1416, "name_kh": "Cutie Charm 16", "price": 4000, "image": "/static/images/cw16.jpg", "categories": ["Cutie"], "subcategory": ["All","Football"], "discount": 20},

    // --- Bubble (1501 - 1512) ---
    {"id": 1501, "name_kh": " Charm 01", "price": 3000, "image": "/static/images/charm-bubble-01.jpg", "categories": ["Slay💅"], "subcategory": ["Car Logo"], "discount": 20},
    {"id": 1502, "name_kh": " Charm 02", "price": 3000, "image": "/static/images/charm-bubble-02.jpg", "categories": ["Slay💅"], "subcategory": ["All","Football"], "discount": 20},
    {"id": 1503, "name_kh": " Charm 03", "price": 3000, "image": "/static/images/charm-bubble-03.jpg", "categories": ["Slay💅"], "subcategory": ["All","Football"], "discount": 20},
    {"id": 1504, "name_kh": " Charm 04", "price": 3000, "image": "/static/images/charm-bubble-04.jpg", "categories": ["Slay💅"], "subcategory": ["All","Football"], "discount": 20},
    {"id": 1505, "name_kh": " Charm 05", "price": 3000, "image": "/static/images/charm-bubble-05.jpg", "categories": ["Slay💅"], "subcategory": ["All","Football"], "discount": 20},
    {"id": 1506, "name_kh": " Charm 06", "price": 3000, "image": "/static/images/charm-bubble-06.jpg", "categories": ["Slay💅"], "subcategory": ["Car Logo"], "discount": 20},
    {"id": 1507, "name_kh": " Charm 07", "price": 3000, "image": "/static/images/charm-bubble-07.jpg", "categories": ["Slay💅"], "subcategory": ["Car Logo"], "discount": 20},
    {"id": 1508, "name_kh": " Charm 08", "price": 3000, "image": "/static/images/charm-bubble-08.jpg", "categories": ["Slay💅"], "subcategory": ["All","Football"], "discount": 20},
    {"id": 1509, "name_kh": " Charm 09", "price": 3000, "image": "/static/images/charm-bubble-09.jpg", "categories": ["Slay💅"], "subcategory": ["All","Football"], "discount": 20},
    {"id": 1510, "name_kh": " Charm 10", "price": 3000, "image": "/static/images/charm-bubble-10.jpg", "categories": ["Slay💅"], "subcategory": ["All","Football"], "discount": 20},
    {"id": 1511, "name_kh": " Charm 11", "price": 3000, "image": "/static/images/charm-bubble-11.jpg", "categories": ["Slay💅"], "subcategory": ["All","Football"], "discount": 20},
    {"id": 1512, "name_kh": " Charm 12", "price": 3000, "image": "/static/images/charm-bubble-12.jpg", "categories": ["Slay💅"], "subcategory": ["All","Football"], "discount": 20},

    // --- Cute Cat (1601 - 1612) ---
    {"id": 1601, "name_kh": " Charm 01", "price": 3000, "image": "/static/images/charm-cutecat-01.jpg", "categories": ["Cute Cat"], "subcategory": ["Car Logo"], "discount": 20},
    {"id": 1602, "name_kh": " Charm 02", "price": 3000, "image": "/static/images/charm-cutecat-02.jpg", "categories": ["Cute Cat"], "subcategory": ["All","Football"], "discount": 20},
    {"id": 1603, "name_kh": " Charm 03", "price": 3000, "image": "/static/images/charm-cutecat-03.jpg", "categories": ["Cute Cat"], "subcategory": ["All","Football"], "discount": 20},
    {"id": 1604, "name_kh": " Charm 04", "price": 3000, "image": "/static/images/charm-cutecat-04.jpg", "categories": ["Cute Cat"], "subcategory": ["All","Football"], "discount": 20},
    {"id": 1605, "name_kh": " Charm 05", "price": 3000, "image": "/static/images/charm-cutecat-05.jpg", "categories": ["Cute Cat"], "subcategory": ["All","Football"], "discount": 20},
    {"id": 1606, "name_kh": " Charm 06", "price": 3000, "image": "/static/images/charm-cutecat-06.jpg", "categories": ["Cute Cat"], "subcategory": ["Car Logo"], "discount": 20},
    {"id": 1607, "name_kh": " Charm 07", "price": 3000, "image": "/static/images/charm-cutecat-07.jpg", "categories": ["Cute Cat"], "subcategory": ["Car Logo"], "discount": 20},
    {"id": 1608, "name_kh": " Charm 08", "price": 3000, "image": "/static/images/charm-cutecat-08.jpg", "categories": ["Cute Cat"], "subcategory": ["All","Football"], "discount": 20},
    {"id": 1609, "name_kh": " Charm 09", "price": 3000, "image": "/static/images/charm-cutecat-09.jpg", "categories": ["Cute Cat"], "subcategory": ["All","Football"], "discount": 20},
    {"id": 1610, "name_kh": " Charm 10", "price": 3000, "image": "/static/images/charm-cutecat-10.jpg", "categories": ["Cute Cat"], "subcategory": ["All","Football"], "discount": 20},
    {"id": 1611, "name_kh": " Charm 11", "price": 3000, "image": "/static/images/charm-cutecat-11.jpg", "categories": ["Cute Cat"], "subcategory": ["All","Football"], "discount": 20},
    {"id": 1612, "name_kh": " Charm 12", "price": 3000, "image": "/static/images/charm-cutecat-12.jpg", "categories": ["Cute Cat"], "subcategory": ["All","Football"], "discount": 20},

    // --- Rok Jit (1701 - 1708) ---
    {"id": 1701, "name_kh": "Rok Jit 01", "price": 3000, "image": "/static/images/charm-rokjit-01.jpg", "categories": ["Rok Jit💔"]},
    {"id": 1702, "name_kh": "Rok Jit 02", "price": 3000, "image": "/static/images/charm-rokjit-02.jpg", "categories": ["Rok Jit💔"]},
    {"id": 1703, "name_kh": "Rok Jit 03", "price": 3000, "image": "/static/images/charm-rokjit-03.jpg", "categories": ["Rok Jit💔"]},
    {"id": 1704, "name_kh": "Rok Jit 04", "price": 3000, "image": "/static/images/charm-rokjit-04.jpg", "categories": ["Rok Jit💔"]},
    {"id": 1705, "name_kh": "Rok Jit 05", "price": 3000, "image": "/static/images/charm-rokjit-05.jpg", "categories": ["Rok Jit💔"]},
    {"id": 1706, "name_kh": "Rok Jit 06", "price": 3000, "image": "/static/images/charm-rokjit-06.jpg", "categories": ["Rok Jit💔"]},
    {"id": 1707, "name_kh": "Rok Jit 07", "price": 3000, "image": "/static/images/charm-rokjit-07.jpg", "categories": ["Rok Jit💔"]}, 
    {"id": 1708, "name_kh": "Rok Jit 08", "price": 3000, "image": "/static/images/charm-rokjit-08.jpg", "categories": ["Rok Jit💔"]},

    // --- 8 Ball (1801 - 1803) ---
    {"id": 1801, "name_kh": "8 Ball 🎱 01", "price": 3000, "image": "/static/images/charm-8ball-01.jpg", "categories": ["8 Ball 🎱"]},
    {"id": 1802, "name_kh": "8 Ball 🎱 02", "price": 3000, "image": "/static/images/charm-8ball-02.jpg", "categories": ["8 Ball 🎱"]},
    {"id": 1803, "name_kh": "8 Ball 🎱 03", "price": 3000, "image": "/static/images/charm-8ball-03.jpg", "categories": ["8 Ball 🎱"]},

    // --- Cherry (1901) ---
    {"id": 1901, "name_kh": "Cherry 🍒 01", "price": 3000, "image": "/static/images/charm-cherry-01.jpg", "categories": ["Cherry 🍒"]},

    // --- Christmas (2001)
    {"id": 2001, "name_kh": "Christmas 🎄 01", "price": 3000, "image": "/static/images/charm-christmas-01.jpg", "categories": ["Christmas 🎄"]},
    {"id": 2002, "name_kh": "Christmas 🎄 02", "price": 3000, "image": "/static/images/charm-christmas-02.jpg", "categories": ["Christmas 🎄"]},
    {"id": 2003, "name_kh": "Christmas 🎄 03", "price": 3000, "image": "/static/images/charm-christmas-03.jpg", "categories": ["Christmas 🎄"]},
    {"id": 2004, "name_kh": "Christmas 🎄 04", "price": 3000, "image": "/static/images/charm-christmas-04.jpg", "categories": ["Christmas 🎄"]},
    {"id": 2005, "name_kh": "Christmas 🎄 05", "price": 3000, "image": "/static/images/charm-christmas-05.jpg", "categories": ["Christmas 🎄"]},
    {"id": 2006, "name_kh": "Christmas 🎄 06", "price": 3000, "image": "/static/images/charm-christmas-06.jpg", "categories": ["Christmas 🎄"]},
    {"id": 2007, "name_kh": "Christmas 🎄 07", "price": 3000, "image": "/static/images/charm-christmas-07.jpg", "categories": ["Christmas 🎄"]}, 
    {"id": 2008, "name_kh": "Christmas 🎄 08", "price": 3000, "image": "/static/images/charm-christmas-08.jpg", "categories": ["Christmas 🎄"]},
    {"id": 2009, "name_kh": "Christmas 🎄 09", "price": 3000, "image": "/static/images/charm-christmas-09.jpg", "categories": ["Christmas 🎄"]},

    {"id": 2011, "name_kh": "Christmas 🎄 01", "price": 3000, "image": "/static/images/charm-christmas-11.jpg", "categories": ["Christmas 🎄"]},
    {"id": 2012, "name_kh": "Christmas 🎄 02", "price": 3000, "image": "/static/images/charm-christmas-12.jpg", "categories": ["Christmas 🎄"]},
    {"id": 2013, "name_kh": "Christmas 🎄 03", "price": 3000, "image": "/static/images/charm-christmas-13.jpg", "categories": ["Christmas 🎄"]},
    {"id": 2014, "name_kh": "Christmas 🎄 04", "price": 3000, "image": "/static/images/charm-christmas-14.jpg", "categories": ["Christmas 🎄"]},
    {"id": 2015, "name_kh": "Christmas 🎄 05", "price": 3000, "image": "/static/images/charm-christmas-15.jpg", "categories": ["Christmas 🎄"]},
    {"id": 2016, "name_kh": "Christmas 🎄 06", "price": 3000, "image": "/static/images/charm-christmas-16.jpg", "categories": ["Christmas 🎄"]},
    {"id": 2017, "name_kh": "Christmas 🎄 07", "price": 3000, "image": "/static/images/charm-christmas-17.jpg", "categories": ["Christmas 🎄"]}, 
    {"id": 2018, "name_kh": "Christmas 🎄 08", "price": 3000, "image": "/static/images/charm-christmas-18.jpg", "categories": ["Christmas 🎄"]},
    {"id": 2019, "name_kh": "Christmas 🎄 09", "price": 3000, "image": "/static/images/charm-christmas-19.jpg", "categories": ["Christmas 🎄"]},

    {"id": 2021, "name_kh": "Christmas 🎄 01", "price": 3000, "image": "/static/images/charm-christmas-21.jpg", "categories": ["Christmas 🎄"]},
    {"id": 2022, "name_kh": "Christmas 🎄 02", "price": 3000, "image": "/static/images/charm-christmas-22.jpg", "categories": ["Christmas 🎄"]},
    {"id": 2023, "name_kh": "Christmas 🎄 03", "price": 3000, "image": "/static/images/charm-christmas-23.jpg", "categories": ["Christmas 🎄"]},
    {"id": 2024, "name_kh": "Christmas 🎄 04", "price": 3000, "image": "/static/images/charm-christmas-04.jpg", "categories": ["Christmas 🎄"]},
    {"id": 2025, "name_kh": "Christmas 🎄 05", "price": 3000, "image": "/static/images/charm-christmas-05.jpg", "categories": ["Christmas 🎄"]},
    {"id": 2026, "name_kh": "Christmas 🎄 06", "price": 3000, "image": "/static/images/charm-christmas-06.jpg", "categories": ["Christmas 🎄"]},
    {"id": 2027, "name_kh": "Christmas 🎄 07", "price": 3000, "image": "/static/images/charm-christmas-07.jpg", "categories": ["Christmas 🎄"]}, 
    {"id": 2028, "name_kh": "Christmas 🎄 08", "price": 3000, "image": "/static/images/charm-christmas-08.jpg", "categories": ["Christmas 🎄"]},
    {"id": 2029, "name_kh": "Christmas 🎄 09", "price": 3000, "image": "/static/images/charm-christmas-09.jpg", "categories": ["Christmas 🎄"]},

    // --- Christmas (2001)
    {"id": 2101, "name_kh": "Flower 🌹 01", "price": 3000, "image": "/static/images/charm-flower-01.jpg", "categories": ["Flower 🌹"]},
    {"id": 2102, "name_kh": "Flower 🌹 02", "price": 3000, "image": "/static/images/charm-flower-02.jpg", "categories": ["Flower 🌹"]},
    {"id": 2103, "name_kh": "Flower 🌹 03", "price": 3000, "image": "/static/images/charm-flower-03.jpg", "categories": ["Flower 🌹"]},
    {"id": 2104, "name_kh": "Flower 🌹 04", "price": 3000, "image": "/static/images/charm-flower-04.jpg", "categories": ["Flower 🌹"]},
    {"id": 2105, "name_kh": "Flower 🌹 05", "price": 3000, "image": "/static/images/charm-flower-05.jpg", "categories": ["Flower 🌹"]},
    {"id": 2106, "name_kh": "Flower 🌹 06", "price": 3000, "image": "/static/images/charm-flower-06.jpg", "categories": ["Flower 🌹"]},
    {"id": 2107, "name_kh": "Flower 🌹 07", "price": 3000, "image": "/static/images/charm-flower-07.jpg", "categories": ["Flower 🌹"]}, 
    {"id": 2108, "name_kh": "Flower 🌹 08", "price": 3000, "image": "/static/images/charm-flower-08.jpg", "categories": ["Flower 🌹"]},
    {"id": 2109, "name_kh": "Flower 🌹 09", "price": 3000, "image": "/static/images/charm-flower-09.jpg", "categories": ["Flower 🌹"]},
   ]

    for item in catalog:
        # Check if Italy Bracelet is in categories to ensure it shows in studio
        cats = ", ".join(item['categories'])
        sub = item.get('subcategory', 'General')
        
        new_product = Product(
            id=item['id'],
            name_kh=item['name_kh'],
            price=item['price'],
            image=item['image'],
            categories_str=cats,
            subcategory_str=sub,
            stock=10 # Initial stock value
        )
        db.session.add(new_product)
    
    db.session.commit()
    print("✅ All charms imported to Database!")

# --- ROUTES ---

@app.route('/custom-bracelet')
def custom_bracelet():
    # Fetch charms and pass to Studio
    charms_db = Product.query.filter(Product.categories_str.contains('Italy Bracelet')).all()
    charms_list = []
    for c in charms_db:
        charms_list.append({
            "id": c.id, "name_kh": c.name_kh, "price": c.price, 
            "image": c.image, "stock": c.stock,
            "categories": [cat.strip() for cat in c.categories_str.split(',')]
        })
    return render_template('custom_bracelet.html', charms_json=charms_list)

@app.route('/admin/products')
def admin_products():
    # Group products by subcategory for easy scrolling
    all_p = Product.query.all()
    grouped = {}
    for p in all_p:
        sub = p.subcategory_str if p.subcategory_str else "General"
        if sub not in grouped: grouped[sub] = []
        grouped[sub].append(p)
    return render_template('admin_products.html', grouped=grouped)

@app.route('/admin/update-stock', methods=['POST'])
def update_stock():
    data = request.json
    p = Product.query.get(data.get('id'))
    if p:
        p.stock = int(data.get('amount'))
        db.session.commit()
        return jsonify({"success": True})
    return jsonify({"success": False})

@app.route('/api/deduct-stock', methods=['POST'])
def deduct_stock():
    """Call this from JS when design is saved"""
    data = request.json
    for pid in data.get('ids', []):
        p = Product.query.get(pid)
        if p and p.stock > 0: p.stock -= 1
    db.session.commit()
    return jsonify({"success": True})

with app.app_context():
    db.create_all()
    seed_database()

if __name__ == '__main__':
    app.run(debug=True)

