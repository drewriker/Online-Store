import os
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin


db = SQLAlchemy()

class User(db.Model, UserMixin):
    """Users"""
    
    __tablename__ = "users"
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    first_name = db.Column(db.String(100))
    last_name = db.Column(db.String(100))  
    email = db.Column(db.String(255), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    is_admin = db.Column(db.Boolean, default=False)

    # Relationship to orders
    orders = db.relationship('Order', backref='user', lazy=True)

    def __init__(self, email, password, first_name, last_name, is_admin=False):
        self.email = email
        self.password = password
        self.first_name = first_name
        self.last_name = last_name
        self.is_admin = is_admin
    
    # #Flask-Login methods
    # def is_active(self):
    #     return True  # Assuming all users are active

    # def is_authenticated(self):
    #     return True  # Assuming all logged-in users are authenticated

    # def is_anonymous(self):
    #     return False  # Assuming no anonymous users

    # def get_id(self):
    #     return str(self.id)
    

class Product(db.Model):
    """Products"""
    
    __tablename__ = "products"
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(255), unique=True, nullable=False)
    price = db.Column(db.Integer, nullable=False) #price in cents
    description = db.Column(db.Text)
    image_url = db.Column(db.String(255))
    
    # Relationship to order items
    order_items = db.relationship('OrderItem', backref='product', lazy=True)
    
    def __init__(self, name, price, description, image_url):
        self.name = name
        self.price = price
        self.description = description
        self.image_url = image_url

class Order(db.Model):
    """User Orders"""
    
    __tablename__ = 'orders'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    total = db.Column(db.Numeric, nullable=False)
    status = db.Column(db.String(50), nullable=False, default='Pending')
    created_at = db.Column(db.DateTime, default=db.func.now())
    
    # Relationship to order items
    order_items = db.relationship('OrderItem', backref='order', lazy=True)

class OrderItem(db.Model):
    """Order Items"""
    
    __tablename__ = 'order_items'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    order_id = db.Column(db.Integer, db.ForeignKey('orders.id'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)

def connect_to_db(app):
    app.config["SQLALCHEMY_DATABASE_URI"] = "postgresql://drewriker@localhost:5433/floral-store"
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    db.app = app
    db.init_app(app)
    print("Connected to db...")
    
if __name__ == "__main__":
    from flask import Flask
    app = Flask(__name__)
    connect_to_db(app)
