import os
from flask import Flask, redirect, render_template, request, flash, url_for
from extensions import db, login_manager
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin, login_user, logout_user, login_required

app = Flask(__name__)

app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-secret-key-12345')
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'sqlite:///verification.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

if app.config['SQLALCHEMY_DATABASE_URI'].startswith("postgres://"):
    app.config['SQLALCHEMY_DATABASE_URI'] = app.config['SQLALCHEMY_DATABASE_URI'].replace("postgres://", "postgresql://", 1)

db.init_app(app)
login_manager.init_app(app)

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

try:
    from routes import main_bp
    app.register_blueprint(main_bp)
except Exception as e:
    print(f"Routes blueprint info: {e}")

@app.route('/')
def home():
    return redirect('/login')

with app.app_context():
    try:
        db.create_all()
        admin = User.query.filter_by(username='Bankverify2026').first()
        hashed_pw = generate_password_hash('Alamin@202303010031')
        
        if not admin:
            admin = User(username='Bankverify2026', password_hash=hashed_pw)
            db.session.add(admin)
            db.session.commit()
            print("Admin user created successfully!")
        else:
            admin.password_hash = hashed_pw
            db.session.commit()
            print("Admin password reset successfully!")
    except Exception as e:
        print(f"DB Init error: {e}")

if __name__ == '__main__':
    app.run(debug=True)
