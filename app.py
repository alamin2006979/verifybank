import os
from flask import Flask, render_template, request, redirect, url_for, flash
from extensions import db, login_manager
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin, login_user, logout_user, login_required, current_user

app = Flask(__name__)

# Basic Config
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-secret-key-12345')
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'sqlite:///verification.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

if app.config['SQLALCHEMY_DATABASE_URI'].startswith("postgres://"):
    app.config['SQLALCHEMY_DATABASE_URI'] = app.config['SQLALCHEMY_DATABASE_URI'].replace("postgres://", "postgresql://", 1)

db.init_app(app)
login_manager.init_app(app)

# User Model Definition
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Routes Definition Directly in app.py
@app.route('/')
def index():
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        user = User.query.filter_by(username=username).first()
        if user and check_password_hash(user.password_hash, password):
            login_user(user)
            return redirect('/dashboard')
        flash('Invalid username or password')
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

@app.route('/dashboard')
@login_required
def dashboard():
    return f"Welcome to Verification Portal Dashboard, {current_user.username}!"

# Auto Create Database and Admin User
with app.app_context():
    try:
        db.create_all()
        admin = User.query.filter_by(username='Bankverify2026').first()
        hashed_pw = generate_password_hash('Alamin@202303010031')
        if not admin:
            admin = User(username='Bankverify2026', password_hash=hashed_pw)
            db.session.add(admin)
            db.session.commit()
            print("Default admin 'Bankverify2026' created successfully!")
        else:
            admin.password_hash = hashed_pw
            db.session.commit()
            print("Admin password updated!")
    except Exception as e:
        print(f"DB Init error: {e}")

if __name__ == '__main__':
    app.run(debug=True)
