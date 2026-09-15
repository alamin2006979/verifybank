import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from werkzeug.security import generate_password_hash

app = Flask(__name__)

# Basic Config
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-secret-key-12345')
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'sqlite:///verification.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Adjust postgresql database url format for SQLAlchemy if needed
if app.config['SQLALCHEMY_DATABASE_URI'].startswith("postgres://"):
    app.config['SQLALCHEMY_DATABASE_URI'] = app.config['SQLALCHEMY_DATABASE_URI'].replace("postgres://", "postgresql://", 1)

db = SQLAlchemy(app)
login_manager = LoginManager(app)

from models import User
from routes import main_bp

app.register_blueprint(main_bp)

# Auto Create Admin for Render Deployment
with app.app_context():
    try:
        db.create_all()
        admin = User.query.filter_by(username='Bankverify2026').first()
        if not admin:
            admin = User(
                username='Bankverify2026',
                password_hash=generate_password_hash('Alamin@202303010031', method='pbkdf2:sha256')
            )
            db.session.add(admin)
            db.session.commit()
            print("Default admin 'Bankverify2026' created successfully!")
        else:
            admin.password_hash = generate_password_hash('Alamin@202303010031', method='pbkdf2:sha256')
            db.session.commit()
            print("Admin password updated successfully!")
    except Exception as e:
        print(f"Error initializing admin: {e}")

if __name__ == '__main__':
    app.run(debug=True)
