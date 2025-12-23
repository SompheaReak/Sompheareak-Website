from app import app, db

with app.app_context():
    print("Creating database...")
    db.drop_all() # Deletes old structure if it exists
    db.create_all() # Creates new shop.db with all columns
    print("✅ shop.db has been created in your folder!")

