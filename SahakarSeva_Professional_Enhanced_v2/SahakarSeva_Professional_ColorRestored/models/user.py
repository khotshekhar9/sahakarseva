from database import db
from flask_login import UserMixin
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash

class User(db.Model, UserMixin):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False, index=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(20), nullable=False)  # 'admin', 'worker', 'customer'
    theme_preference = db.Column(db.String(10), nullable=False, default='light')  # 'light' or 'dark'
    phone = db.Column(db.String(20), nullable=True)
    address = db.Column(db.Text, nullable=True)
    profile_pic = db.Column(db.String(255), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    is_archived = db.Column(db.Boolean, default=False, nullable=False)
    two_factor_secret = db.Column(db.String(100), nullable=True)
    two_factor_enabled = db.Column(db.Boolean, default=False, nullable=False)
    dashboard_config = db.Column(db.Text, nullable=True)

    # Relationships
    worker_profile = db.relationship('Worker', backref='user', uselist=False, cascade="all, delete-orphan")
    customer_profile = db.relationship('Customer', backref='user', uselist=False, cascade="all, delete-orphan")

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return f'<User {self.username} ({self.role})>'
