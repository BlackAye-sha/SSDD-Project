from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_bcrypt import Bcrypt
from flask_migrate import Migrate  # <-- import Migrate

db = SQLAlchemy()
login_manager = LoginManager()
bcrypt = Bcrypt()
migrate = Migrate()  # <-- create migrate instance

def create_app():
    app = Flask(__name__)
    app.config.from_object('config.Config')

    db.init_app(app)
    login_manager.init_app(app)
    bcrypt.init_app(app)
    migrate.init_app(app, db)  # <-- initialize migrate with app and db

    # LoginManager config
    login_manager.login_view = 'main.login'
    login_manager.login_message_category = 'info'

    # Import and register Blueprints
    from .routes import main
    app.register_blueprint(main)

    from app.models import User  # import User model for login_manager

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    return app
