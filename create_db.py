from app import db, create_app
# Import all your models here, including the new ones
from app.models import User, Book, CartItem, Review, Order, OrderItem # ADD Order, OrderItem

app = create_app()

with app.app_context():
    db.create_all() # This will now create tables for User, Book, CartItem, Review, Order, and OrderItem

    # Check if books already exist to prevent duplicates on successive runs
    if not Book.query.first():
        db.session.add_all([
            # History books
            Book(title="A People’s History of the United States", author="Howard Zinn", genre="history", price=12.99),
            Book(title="Guns, Germs, and Steel", author="Jared Diamond", genre="history", price=14.75),
            Book(title="Sapiens: A Brief History of Humankind", author="Yuval Noah Harari", genre="history", price=15.75),
            Book(title="The Diary of a Young Girl", author="Anne Frank", genre="history", price=10.00),

            # Fanfiction books
            Book(title="My Immortal", author="Tara Gliebile", genre="fanfic", price=5.00),
            Book(title="The Love Hypothesis", author="Ali Hazelwood", genre="fanfic", price=13.99),
            Book(title="Fifty Shades of Grey", author="E.L. James", genre="fanfic", price=17.99),
            Book(title="Harry Potter and the Half-Blood Prince", author="J.K. Rowling", genre="fanfic", price=18.50),

            # Poetry books
            Book(title="Milk and Honey", author="Rupi Kaur", genre="poetry", price=9.99),
            Book(title="The Waste Land", author="T.S. Eliot", genre="poetry", price=7.50),
            Book(title="Leaves of Grass", author="Walt Whitman", genre="poetry", price=8.75),
            Book(title="The Sun and Her Flowers", author="Rupi Kaur", genre="poetry", price=18.25),

            # Quotes books
            Book(title="The Prophet", author="Kahili Gilman", genre="quotes", price=6.99),
            Book(title="Meditations", author="Marcus Aurelius", genre="quotes", price=7.99),
            Book(title="Poor Richard’s Almanack", author="Benjamin Franklin", genre="quotes", price=8.00),
            Book(title="The Book of Awesome", author="Neil Pesticha", genre="quotes", price=9.50)
        ])
        db.session.commit()
        print("✅ Initial books added to the database.")
    else:
        print("Database tables created. Books already exist, skipping initial book addition.")

    print("✅ Database initialization complete.")