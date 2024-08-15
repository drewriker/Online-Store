"""CRUD Operations"""

from model import db, User, Product, Order, OrderItem
from flask_bcrypt import Bcrypt

bcrypt = Bcrypt()

def register_user(first_name, last_name, email, password, is_admin=False):
    """register a new user"""
    hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')
    user = User(first_name=first_name, last_name=last_name, email=email, password=hashed_password, is_admin=is_admin)
    db.session.add(user)
    db.session.commit()
    return user

def get_user_by_email(email):
    """return user by email"""
    return User.query.filter_by(email=email).first()

def check_password(user, password):
    """check login password with saved hashed password"""
    return bcrypt.check_password_hash(user.password, password)


def get_products():
    """return all products""" 
    return Product.query.all()

def get_product_by_id(product_id):
    """return specific product by ID"""
    return Product.query.get(product_id)

def create_product(name, price, description, image_url):
    """Create a product"""
    product = Product(name=name, price=price, description=description, image_url=image_url)
    return product

def get_all_orders():
    """return all orders"""
    return Order.query.all()

def get_order_by_id(order_id):
    """return order from ID"""
    return Order.query.get(order_id)

def create_order(user_id, total, status='Pending'):
    order = Order(user_id=user_id, total=total, status=status)
    return order

def create_order_item(order_id, product_id, quantity):
    order_item = OrderItem(order_id=order_id, product_id=product_id, quantity=quantity)
    return order_item

def mark_order_complete(order_id):
    """Mark an order as complete"""
    order = Order.query.get(order_id)
    if order:
        order.status = "Complete"
        db.session.commit()
    return order

def mark_order_canceled(order_id):
    """mark an order as canceled"""
    order = Order.query.get(order_id)
    if order:
        order.status = "Canceled"
        db.session.commit()
        return order

def get_orders_by_user(user_id):
    """return orders made by specific user"""
    orders = Order.query.filter_by(user_id=user_id).all()
    return orders

def get_products_by_order(order_id):
    """return all products in order"""
    order = Order.query.get(order_id)
    
    order_items = order.order_items
    
    products = [item.product for item in order_items]
    
    return products