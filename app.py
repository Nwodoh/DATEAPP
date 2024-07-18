from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
from flask_cors import CORS
from config import config_by_name

db = SQLAlchemy()
DB_NAME = "database.db"

def create_app():
    app = Flask(__name__)
    CORS(app, resources={r"/*": {"supports_credentials": True}})
    
    app.config.from_object(config_by_name['development'])

    db.init_app(app)
    migrate = Migrate(app, db)
    
    # from chat import chat
    from routes.auth import auth
    from routes.user import user
    from routes.chat import chat
    from routes.image import image

    app.register_blueprint(auth, url_prefix='/api/v1/auth')
    app.register_blueprint(user, url_prefix='/api/v1/user')
    app.register_blueprint(chat, url_prefix='/api/v1/chat')
    app.register_blueprint(image, url_prefix='/api/v1/image')

    from models.User import User

    login_manager = LoginManager()
    login_manager.init_app(app)
    login_manager.login_view = 'auth.protect'

    @login_manager.user_loader
    def load_user(id):
        return User.query.get(int(id))

    return app