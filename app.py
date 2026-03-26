import os
from flask import Flask, render_template

app = Flask(__name__)

# --- PUBLIC ROUTES ---
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

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))


