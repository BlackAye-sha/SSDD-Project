from app import db
from flask_login import UserMixin
from datetime import datetime

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), nullable=False, unique=True)
    email = db.Column(db.String(150), nullable=False, unique=True)
    password = db.Column(db.String(150), nullable=False)

     # NEW: Add an is_admin column, default to False
    is_admin = db.Column(db.Boolean, default=False)

    # Relationship to CartItems (books in user's current cart)
    cart_items = db.relationship('CartItem', backref='user', lazy=True)
    # Relationship to Orders made by this user
    orders = db.relationship('Order', backref='user', lazy=True)
    # Relationship to Reviews made by this user
    reviews = db.relationship('Review', backref='user', lazy=True)

    def __repr__(self):
        return f"User('{self.username}', '{self.email}')"

class Book(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    author = db.Column(db.String(100))
    genre = db.Column(db.String(50))
    price = db.Column(db.Float)
    # Optional: add a 'stock' column if you plan to manage inventory
    # stock = db.Column(db.Integer, default=0, nullable=False)

    # Relationship to CartItems (books in various users' carts)
    cart_items = db.relationship('CartItem', backref='book', lazy=True)
    # Relationship to OrderItems that contain this book (historical purchases)
    order_items = db.relationship('OrderItem', backref='book', lazy=True)
    # Relationship to Reviews for this book
    reviews = db.relationship('Review', backref='book', lazy=True)

    def __repr__(self):
        return f"Book('{self.title}', '{self.author}', Price: {self.price})"

class CartItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    book_id = db.Column(db.Integer, db.ForeignKey('book.id'), nullable=False)
    quantity = db.Column(db.Integer, default=1, nullable=False)

    # Relationships are handled by backrefs from User and Book models
    # user = db.relationship('User', backref='user_cart_items', lazy=True) # Redundant
    # book = db.relationship('Book', backref='book_cart_items', lazy=True) # Redundant

    @property
    def total_price(self):
        # This property allows easy calculation of the total price for a cart item
        # It relies on the 'book' object being available through the relationship
        return self.quantity * self.book.price if self.book else 0.0

    def __repr__(self):
        return f"CartItem(User: {self.user_id}, Book: {self.book_id}, Quantity: {self.quantity})"

class Review(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    rating = db.Column(db.Integer, nullable=False) # e.g., 1 to 5 stars
    comment = db.Column(db.Text)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    book_id = db.Column(db.Integer, db.ForeignKey('book.id'), nullable=False)
    # Using datetime.utcnow for consistency and timezone awareness
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

    # Explicit relationships, though backrefs on User and Book already create them
    # user = db.relationship('User', backref='user_reviews') # Redundant
    # book = db.relationship('Book', backref='book_reviews') # Redundant

    def __repr__(self):
        return f"Review(Rating: {self.rating}, Book: {self.book_id}, User: {self.user_id})"

# --- NEW MODELS FOR CHECKOUT AND ORDER HISTORY ---

class Order(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    order_date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    total_amount = db.Column(db.Float, nullable=False)
    status = db.Column(db.String(50), nullable=False, default='pending')
    shipping_address = db.Column(db.Text, nullable=False)
    # NEW: Column to store the chosen payment method
    payment_method = db.Column(db.String(50), nullable=False) # e.g., 'cash_on_delivery', 'easypaisa_transfer'

    items = db.relationship('OrderItem', backref='order', lazy=True)

    def __repr__(self):
        return f"Order('{self.id}', User: {self.user_id}, Total: {self.total_amount}, Status: '{self.status}', Payment: '{self.payment_method}')"

class OrderItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey('order.id'), nullable=False)
    book_id = db.Column(db.Integer, db.ForeignKey('book.id'), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    # Crucial: Stores the price of the book at the exact moment of purchase
    price_at_purchase = db.Column(db.Float, nullable=False)

    # Relationships are handled by backrefs from Order and Book models
    # order = db.relationship('Order', backref='order_items_rel') # Redundant
    # book = db.relationship('Book', backref='book_order_items_rel') # Redundant

    def __repr__(self):
        return f"OrderItem(Order: {self.order_id}, Book: {self.book_id}, Quantity: {self.quantity}, Price: {self.price_at_purchase})"