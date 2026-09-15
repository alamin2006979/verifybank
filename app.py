import os
from flask import Flask
from extensions import db, login_manager
from werkzeug.security import generate_password_hash

app = Flask(__name__)

# Basic Config
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-secret-key-12345')
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'sqlite:///verification.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

if app.config['SQLALCHEMY_DATABASE_URI'].startswith("postgres://"):
    app.config['SQLALCHEMY_DATABASE_URI'] = app.config['SQLALCHEMY_DATABASE_URI'].replace("postgres://", "postgresql://", 1)

db.init_app(app)
login_manager.init_app(app)

# Fallback routes import or blueprint setup
try:
    from routes import main_bp
    app.register_blueprint(main_bp)
except ImportError:
    pass

# Auto Create Admin for Render Deployment
with app.app_context():
    try:
        db.create_all()
        # Dynamic User creation using reflection if models import fails
        from sqlalchemy import text
        db.session.execute(text("""
            CREATE TABLE IF NOT EXISTS user (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username VARCHAR(80) UNIQUE NOT NULL,
                password_hash VARCHAR(255) NOT NULL
            );
        """))
        db.session.commit()
        
        # Check and insert admin directly
        res = db.session.execute(text("SELECT * FROM user WHERE username = 'Bankverify2026'")).fetchone()
        hashed_pw = generate_password_hash('Alamin@202303010031', method='pbkdf2:sha256')
        if not res:
            db.session.execute(text("INSERT INTO user (username, password_hash) VALUES ('Bankverify2026', :pw)"), {'pw': hashed_pw})
            db.session.commit()
            print("Default admin created successfully!")
        else:
            db.session.execute(text("UPDATE user SET password_hash = :pw WHERE username = 'Bankverify2026'"), {'pw': hashed_pw})
            db.session.commit()
            print("Admin password updated!")
    except Exception as e:
        print(f"Database init info: {e}")

if __name__ == '__main__':
    app.run(debug=True)
