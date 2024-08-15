"""Server for Floral Store app."""
import os, stripe
from flask import Flask, render_template, url_for, flash, session, redirect, request, jsonify
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from model import connect_to_db, db
from forms import RegistrationForm, LoginForm
import crud, model
from jinja2 import StrictUndefined

app = Flask(__name__)
app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY")
app.jinja_env.undefined = StrictUndefined

stripe.api_key = os.environ.get("STRIPE_SECRET_KEY")

# Initialize Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"

@login_manager.user_loader
def load_user(user_id):
    return model.User.query.get(int(user_id))

#App routes
@app.route('/')
def home():
    return render_template("base.html", first_name=session.get('first_name'))

@app.route('/products')
def products():
    products = crud.get_products()
    return render_template('products.html', products=products)

@app.route('/cart')
def cart():
    items = session.get('cart', [])
    return render_template('cart.html', items=items)

@app.route("/empty-cart")
def empty_cart():
    session['cart'] = []
    
    return redirect("/cart")

@app.route('/add-to-cart/<int:product_id>', methods=["POST"])
@login_required
def add_to_cart(product_id):
    product = crud.get_product_by_id(product_id)
    
    if not product:
        flash("Product not found")
        return redirect(url_for('products'))
    
    quantity = request.form.get('quantity', type=int)
    if not quantity or quantity < 1:
        flash("Invalid quantity")
        return redirect(url_for('products'))
    
    cart = session.get('cart', [])
    
    for item in cart:
        if item['id'] == product_id:
            if 'quantity' in item:
                item['quantity'] += quantity
            else:
                item['quantity'] = quantity
            break
    else:
        cart.append({'id': product.id, 'name': product.name, 'price': product.price, 'quantity': quantity})
    
    session['cart'] = cart
    flash("Item successfully added to cart")
    return redirect(url_for('products'))

@app.route('/orders')
@login_required
def orders():
    user_id = session['user_id']
    orders = crud.get_orders_by_user(user_id)
    return render_template("orders.html", orders=orders)

@app.route('/orders/<int:order_id>', methods=['GET', 'POST'])
@login_required
def order_details(order_id):
    order = crud.get_order_by_id(order_id)
    products = crud.get_products_by_order(order_id)
    total = order.total
    return render_template("order_details.html", products=products, order_id=order_id, total=total)


@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegistrationForm()
    
    #pull info from form
    first_name = form.first_name.data
    last_name = form.last_name.data
    email = form.email.data
    password = form.password.data
    
    if form.validate_on_submit():
        user = crud.register_user(first_name=first_name, last_name=last_name, email=email, password=password)
        flash("Your account has been created!", "success")
        return redirect(url_for('login'))
    else:
        flash("Failed to make account")
    return render_template('register.html', form=form)

@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = crud.get_user_by_email(form.email.data)
        if user and crud.check_password(user, form.password.data):
            login_user(user)
            session['user_id'] = user.id
            session['is_admin'] = user.is_admin
            session['first_name'] = user.first_name
            flash("You have been logged in!", "success")
            return redirect(url_for('home'))
        else:
            flash("Login Unsuccessful. Please check email and password", 'danger')
    return render_template('login.html', form=form)

@app.route('/logout')
@login_required
def logout():
    logout_user()
    session.clear()
    flash('You have been logged out', 'info')
    return redirect(url_for('home'))



"""ADMIN ROUTES"""
@app.route('/admin')
@login_required
def admin():
    if not current_user.is_admin:
        flash("Your are not authorized to access this page", "danger")
        return redirect(url_for("home"))
    products = crud.get_products()
    return render_template('admin.html', products=products)

@app.route('/admin/add', methods=['GET', 'POST'])
@login_required
def add_product():
    if not current_user.is_admin:
        flash("Your are not authorized to access this page", "danger")
        return redirect(url_for("home"))
    if request.method == 'POST':
        name = request.form['name']
        price = int(request.form['price'])
        description = request.form['description']
        image_url = request.form['image_url']
        new_product = crud.create_product(name, price, description, image_url)
        db.session.add(new_product)
        db.session.commit()
        flash("Successfully added product!", 'success')
        return redirect(url_for('admin'))
    return render_template('add_product.html')

@app.route('/admin/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_product(id):
    if not current_user.is_admin:
        flash("Your are not authorized to access this page", "danger")
        return redirect(url_for("home"))
    
    product = crud.get_product_by_id(id)
    if request.method == 'POST':
        product.name = request.form['name']
        product.price = request.form['price']
        product.description = request.form['description']
        product.image_url = request.form['image_url']
        db.session.commit()
        flash("Product updated successfully!", "success")
        return redirect(url_for('admin'))
    return render_template('edit_product.html', product=product)

@app.route('/admin/orders')
@login_required
def admin_orders():
    if not current_user.is_admin:
        flash("Your are not authorized to access this page", "danger")
        return redirect(url_for("home"))
    
    orders = crud.get_all_orders()
    return render_template("admin_orders.html", orders=orders)

@app.route('/admin/orders/<int:order_id>/complete', methods=['POST'])
@login_required
def complete_order(order_id):
    if not current_user.is_admin:
        flash("Your are not authorized to access this page", "danger")
        return redirect(url_for("home"))
    
    order = crud.mark_order_complete(order_id)
    if order:
        flash(f"Order {order_id} marked as complete", "success")
    else:
        flash(f"Order {order_id} not found", "danger")
    return redirect(url_for('admin_orders'))

@app.route('/cancel-order/<int:order_id>', methods=['POST'])
@login_required
def cancel_order(order_id):
    if not current_user.is_admin:
        flash("Your are not authorized to access this page", "danger")
        return redirect(url_for("home"))
    # Fetch the order and update its status to "Canceled"
    order = crud.mark_order_canceled(order_id)
    if order:
        flash(f"Order {order_id} marked as canceled", "success")
    else:
        flash(f"Order {order_id} not found", "danger")
    return redirect(url_for('admin_orders'))


############ Stripe Checkout ############

@app.route('/create-checkout-session', methods=['POST'])
@login_required
def create_checkout_session():
    cart = session.get('cart', [])
    # check if there are items in cart
    if not cart:
        flash('Cart is empty', 'danger')
        return redirect(url_for('cart'))
    # check is user is signed in
    user_id = session.get('user_id')
    if not user_id: 
        flash("User not logged in", "danger")
        return redirect(url_for('login'))
    
    try:
        #calculate total cost in cents
        total_amount = sum(item['price'] * item['quantity'] for item in cart)
        
        # create new order in database
        order = crud.create_order(user_id=user_id, total=total_amount, status="Pending")
        db.session.add(order)
        db.session.commit()
        
        #create order items
        for item in cart:
            order_item = crud.create_order_item(
                order_id=order.id,
                product_id=item['id'],
                quantity=item['quantity']
            )
            db.session.add(order_item)
        db.session.commit()
        
        # store order id in session
        session['order_id'] = order.id
        
        # create Stripe session
        line_items = [{
            'price_data': {
                'currency': 'usd',
                'product_data': {
                    'name': item['name'],
                },
                'unit_amount': item['price'],  # price in cents
            },
            'quantity': item['quantity'],
        } for item in cart]
        
        checkout_session = stripe.checkout.Session.create(
            payment_method_types=['card'],
            line_items=line_items,
            mode='payment',
            success_url=url_for('payment_success', _external=True),
            cancel_url=url_for('payment_cancel', _external=True)
        )
        
        return jsonify({'id': checkout_session.id})
        
    except Exception as e:
        db.session.rollback()
        flash("An error occurred while creating the checkout session", "danger")
        return jsonify({'error': str(e)}), 500

@app.route('/payment-success')
def payment_success():
    order_id = session.get('order_id')
    if order_id:
        order = model.Order.query.get(order_id)
        if order:
            order.status = 'Pending'
            db.session.commit()
            flash('Payment successful, order completed.', 'success')
            session.pop('cart', None)  # Clear the cart
            session.pop('order_id', None)  # Clear the order ID from session
        else:
            flash('Order not found.', 'danger')

    return redirect(url_for('home'))

@app.route('/payment-cancel')
def payment_cancel():
    order_id = session.get('order_id')
    if order_id:
        order = model.Order.query.get(order_id)
        if order:
            order.status = 'Canceled'
            db.session.commit()
            flash('Payment canceled.', 'info')

    return redirect(url_for('cart'))


if __name__ == "__main__":
    connect_to_db(app)
    app.run(host="0.0.0.0", debug=True)