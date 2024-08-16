from model import db, User, Product, Order, OrderItem, connect_to_db
from flask import Flask
import crud
import os

# Create a Flask app instance
app = Flask(__name__)

os.system("dropdb -p 5433 floral-store")
os.system("createdb -p 5433 floral-store")


# Connect to the database
connect_to_db(app)

### test data
def seed_data():
    with app.app_context():
        # Drop all tables
        db.drop_all()
        
        # Create tables
        db.create_all()
        
        # Create 5 users
        users = [
            crud.register_user("Admin", "Test", "admin@test.com", "admin123", is_admin=True),
            crud.register_user("John", "Doe", "john.doe@test.com", "password1"),
            crud.register_user("Jane", "Doe", "jane.doe@test.com", "password2"),
            crud.register_user("Alice", "Smith", "alice.smith@test.com", "password3"),
            crud.register_user("Bob", "Johnson", "bob.johnson@test.com", "password4")
        ]
        db.session.add_all(users)
        db.session.commit()

        # Create a product
        product = Product(name='Rose Bouquet', price=2999, description='A beautiful bouquet of red roses.', image_url='http://example.com/rose_bouquet.jpg')
        db.session.add(product)
        db.session.commit()

        # Create 7 orders
        orders = [
            Order(user_id=users[0].id, total=2999),  # Order by Admin
            Order(user_id=users[1].id, total=2999),  # Order by John Doe
            Order(user_id=users[2].id, total=5998),  # Two orders by Jane Doe
            Order(user_id=users[2].id, total=2999),  
            Order(user_id=users[3].id, total=2999),  # Order by Alice Smith
            Order(user_id=users[4].id, total=2999),  # Two orders by Bob Johnson
            Order(user_id=users[4].id, total=2999)
        ]
        db.session.add_all(orders)
        db.session.commit()

        # Add order items for each order
        order_items = []
        for order in orders:
            order_items.append(OrderItem(order_id=order.id, product_id=product.id, quantity=1))
        db.session.add_all(order_items)
        db.session.commit()

        print("Database seeded!")


if __name__ == '__main__':
    seed_data()
