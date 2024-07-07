from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
from config import config_by_name

db = SQLAlchemy()
DB_NAME = "database.db"

def create_app():
    app = Flask(__name__)
    app.config.from_object(config_by_name['development'])

    db.init_app(app)
    migrate = Migrate(app, db)
    
    # from chat import chat
    from routes.auth import auth
    from routes.user import user

    app.register_blueprint(auth, url_prefix='/api/v1/auth')
    app.register_blueprint(user, url_prefix='/api/v1/user')

    from models.User import User

    # create_database(app)

    login_manager = LoginManager()
    login_manager.init_app(app)
    login_manager.login_view = 'auth.protect'

    @login_manager.user_loader
    def load_user(id):
        return User.query.get(int(id))

    return app