from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager


db = SQLAlchemy()
login_manager = LoginManager()

# from cryptography.fernet import Fernet

# key = Fernet.generate_key()
# with open("secret.key", "wb") as key_file:
#     key_file.write(key)

def create_app():
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_pyfile('../instance/config.py')

    db.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'

    from app.models import User, File
    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    from app.routes import auth_routes, upload_routes, download_routes
    app.register_blueprint(auth_routes.bp, url_prefix='/auth')
    app.register_blueprint(upload_routes.bp, url_prefix='/auth')
    app.register_blueprint(download_routes.bp, url_prefix='/auth')

    return app
