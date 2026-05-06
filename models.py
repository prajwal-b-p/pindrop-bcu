from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from datetime import datetime

db = SQLAlchemy()

# User Table
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True, nullable=False)
    email = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(20), default='STUDENT')
    department = db.Column(db.String(100), nullable=True)
    # Relationships
    items = db.relationship('Item', backref='user', lazy=True)
    reports = db.relationship('Report', backref='reporter', lazy=True)

# Category Table
class Category(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    items = db.relationship('Item', backref='category', lazy=True)

# Item Table
class Item(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    type = db.Column(db.String(10), nullable=False)  # 'LOST' or 'FOUND'
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=False)
    location = db.Column(db.String(200), nullable=False)
    latitude = db.Column(db.Float, nullable=True)
    longitude = db.Column(db.Float, nullable=True)
    date_occurred = db.Column(db.Date, nullable=False)
    image_file = db.Column(db.String(255), nullable=True, default='default.jpg')
    contact_name = db.Column(db.String(150), nullable=False)
    contact_number = db.Column(db.String(20), nullable=False)
    verification_code = db.Column(db.String(10), unique=True, nullable=True, default=None)
    status = db.Column(db.String(20), default='OPEN') # OPEN, CLAIMED, RESOLVED
    is_high_value = db.Column(db.Boolean, default=False)
    assigned_department = db.Column(db.String(100), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Foreign Keys
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    category_id = db.Column(db.Integer, db.ForeignKey('category.id'), nullable=True)

# Match Table
class Match(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    score = db.Column(db.Float, default=0.0)
    
    # We store the IDs of the two items that matched
    lost_item_id = db.Column(db.Integer, db.ForeignKey('item.id'), nullable=False)
    found_item_id = db.Column(db.Integer, db.ForeignKey('item.id'), nullable=False)
    
    # Relationships to access the actual Item objects
    lost_item = db.relationship('Item', foreign_keys=[lost_item_id])
    found_item = db.relationship('Item', foreign_keys=[found_item_id])

# Report Table
class Report(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    reason = db.Column(db.Text, nullable=False)
    item_id = db.Column(db.Integer, db.ForeignKey('item.id'), nullable=False)
    reporter_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    is_resolved = db.Column(db.Boolean, default=False)