from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required, current_user
from app.forms import LoginForm, RegisterForm, ReviewForm, CheckoutForm
from app.models import User, Book, CartItem, Review, Order, OrderItem
from app import db, bcrypt
from sqlalchemy import func

main = Blueprint('main', __name__)

@main.route('/')
def landing():
    if current_user.is_authenticated:
        return redirect(url_for('main.home'))
    return render_template('landing.html')

@main.route('/home')
@login_required
def home():
    search_query = request.args.get('search', '').strip()
    genre_filter = request.args.get('genre', '').strip().lower()

    books_query = Book.query

    if search_query:
        books_query = books_query.filter(
            (Book.title.ilike(f'%{search_query}%')) | (Book.author.ilike(f'%{search_query}%'))
        )

    valid_genres = ['history', 'fanfic', 'poetry', 'quotes']
    if genre_filter and genre_filter in valid_genres:
        books_query = books_query.filter(func.lower(Book.genre) == genre_filter)

    books = books_query.all()
    show_books = bool(search_query or genre_filter)

    return render_template(
        'home.html',
        books=books,
        search_query=search_query,
        genre_filter=genre_filter,
        show_books=show_books
    )

@main.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user)
            return redirect(url_for('main.home'))
        flash('Invalid email or password', 'danger')
    return render_template('login.html', form=form)

@main.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        existing_user = User.query.filter_by(email=form.email.data).first()
        if existing_user:
            flash('Email already registered. Please use a different one.', 'danger')
            return redirect(url_for('main.register'))

        hashed_pw = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        new_user = User(username=form.username.data, email=form.email.data, password=hashed_pw)
        db.session.add(new_user)
        db.session.commit()
        flash('Registration successful. Please log in.', 'success')
        return redirect(url_for('main.login'))

    return render_template('register.html', form=form)

@main.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('main.landing'))

@main.route('/category/<genre>')
def category(genre):
    books = Book.query.filter(func.lower(Book.genre) == genre.lower()).all()
    return render_template('category.html', books=books, genre=genre)

@main.route('/cart')
@login_required
def cart():
    items = CartItem.query.filter_by(user_id=current_user.id).all()
    total = sum(item.total_price for item in items)
    return render_template('cart.html', items=items, total=total)

@main.route('/add_to_cart/<int:book_id>', methods=['POST'])
@login_required
def add_to_cart(book_id):
    quantity = int(request.form.get('quantity', 1))
    cart_item = CartItem.query.filter_by(user_id=current_user.id, book_id=book_id).first()
    if cart_item:
        cart_item.quantity += quantity
    else:
        cart_item = CartItem(user_id=current_user.id, book_id=book_id, quantity=quantity)
        db.session.add(cart_item)
    db.session.commit()
    flash('Book added to cart!', 'success')
    return redirect(request.referrer or url_for('main.home'))

@main.route('/book/<int:book_id>', methods=['GET', 'POST'])
@login_required
def book_detail(book_id):
    book = Book.query.get_or_404(book_id)
    form = ReviewForm()
    reviews = Review.query.filter_by(book_id=book_id).order_by(Review.timestamp.desc()).all()

    if form.validate_on_submit():
        new_review = Review(
            rating=int(form.rating.data),
            comment=form.comment.data,
            user_id=current_user.id,
            book_id=book.id
        )
        db.session.add(new_review)
        db.session.commit()
        flash('Your review has been submitted!', 'success')
        return redirect(url_for('main.book_detail', book_id=book.id))

    return render_template('book_detail.html', book=book, reviews=reviews, form=form)

# --- NEW ROUTES FOR CHECKOUT ---

@main.route("/checkout", methods=['GET', 'POST'])
@login_required
def checkout():
    cart_items = CartItem.query.filter_by(user_id=current_user.id).all()

    if not cart_items:
        flash('Your cart is empty. Please add items before checking out.', 'warning')
        return redirect(url_for('main.cart'))

    form = CheckoutForm()
    easypaisa_details = {
        'account_name': 'Book_Store - Najaf Riaz',
        'account_number': '0327-6505465' # Replace with actual EasyPaisa account number
    }

    if form.validate_on_submit():
        total_amount = sum(item.total_price for item in cart_items)

        try:
            new_order = Order(
                user_id=current_user.id,
                total_amount=total_amount,
                shipping_address=form.shipping_address.data,
                payment_method=form.payment_method.data
            )
            db.session.add(new_order)
            db.session.commit()

            for cart_item in cart_items:
                order_item = OrderItem(
                    order_id=new_order.id,
                    book_id=cart_item.book_id,
                    quantity=cart_item.quantity,
                    price_at_purchase=cart_item.book.price
                )
                db.session.add(order_item)
                db.session.delete(cart_item)

            db.session.commit()

            flash('Your order has been placed successfully!', 'success')
            return redirect(url_for('main.order_confirmation', order_id=new_order.id))

        except Exception as e:
            db.session.rollback()
            flash(f'An error occurred while placing your order: {e}', 'danger')
            print(f"Error placing order: {e}")

    total_cart_price = sum(item.total_price for item in cart_items)
    return render_template(
        'checkout.html',
        title='Checkout',
        form=form,
        cart_items=cart_items,
        total_cart_price=total_cart_price,
        easypaisa_details=easypaisa_details
    )

@main.route("/order_confirmation/<int:order_id>")
@login_required
def order_confirmation(order_id):
    order = Order.query.get_or_404(order_id)
    if order.user_id != current_user.id:
        flash('You do not have permission to view this order.', 'danger')
        return redirect(url_for('main.home'))

    order_items = OrderItem.query.filter_by(order_id=order.id).all()
    easypaisa_details = {
        'account_name': 'Your Name Here',
        'account_number': '03XX-XXXXXXX' # Replace with actual EasyPaisa account number
    }

    return render_template(
        'order_confirmation.html',
        title='Order Confirmation',
        order=order,
        order_items=order_items,
        easypaisa_details=easypaisa_details
    )

@main.route("/order_history")
@login_required
def order_history():
    user_orders = Order.query.filter_by(user_id=current_user.id).order_by(Order.order_date.desc()).all()
    return render_template('order_history.html', title='Order History', orders=user_orders)

@main.route("/order_details/<int:order_id>")
@login_required
def order_details(order_id):
    order = Order.query.get_or_404(order_id)
    if order.user_id != current_user.id:
        flash('You do not have permission to view this order.', 'danger')
        return redirect(url_for('main.order_history'))

    order_items = OrderItem.query.filter_by(order_id=order.id).all()
    return render_template('order_details.html', title=f'Order #{order.id} Details', order=order, order_items=order_items)


# --- BASIC ADMIN ROUTES (FOR DEVELOPMENT/TESTING ONLY - NOT SECURE FOR PRODUCTION) ---

@main.route("/admin/orders")
@login_required
def admin_view_orders():
    # --- NEW ADMIN CHECK ---
    if not current_user.is_admin:
        flash("Access denied. You must be an administrator to view this page.", "danger")
        return redirect(url_for('main.home')) # Redirect to home if not admin
    # --- END ADMIN CHECK ---

    all_orders = Order.query.order_by(Order.order_date.desc()).all()
    return render_template('admin_orders_list.html', title='Manage Orders', orders=all_orders)


@main.route("/admin/update_order/<int:order_id>", methods=['GET', 'POST'])
@login_required
def admin_update_order(order_id):
    # --- NEW ADMIN CHECK ---
    if not current_user.is_admin:
        flash("Access denied. You must be an administrator to update orders.", "danger")
        return redirect(url_for('main.home')) # Redirect to home if not admin
    # --- END ADMIN CHECK ---

    order = Order.query.get_or_404(order_id)
    valid_statuses = ['pending', 'processing', 'shipped', 'completed', 'cancelled']

    if request.method == 'POST':
        new_status = request.form.get('status')
        if new_status and new_status in valid_statuses:
            order.status = new_status
            db.session.commit()
            flash(f"Order #{order.id} status updated to '{new_status.title()}'", "success")
            return redirect(url_for('main.admin_view_orders'))
        else:
            flash("Invalid status selected.", "danger")

    return render_template(
        'admin_update_order.html',
        title=f'Update Order #{order.id}',
        order=order,
        statuses=valid_statuses
    )