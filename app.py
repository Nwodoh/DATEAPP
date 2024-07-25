from flask_socketio import SocketIO, send, join_room, emit
from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager, current_user
from flask_cors import CORS
from config import config_by_name
from utils.helpers import get_chat_room_key

db = SQLAlchemy()
DB_NAME = "database.db"

def create_app():
    app = Flask(__name__)
    socketio = SocketIO(app, cors_allowed_origins="*", cookie="True")
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

    @socketio.on('connect')
    def handle_connect(user):
        print(user)
        send('Connected to server', broadcast=True)

    @socketio.on('online')
    def add_online(user):
        user_id = user.get('id')
        if not user_id: return
        join_room(user_id)

    @socketio.on('chat/active')
    def activate_chat(chats):
        if not chats or not len(chats): return
        for chat in chats:
            other_user = chat.get('other_user')
            is_sender = chat.get('is_sender')
            receiver = chat.get('receiver')
            sender = chat.get('sender')
            if not other_user: return
            other_user_id = other_user.get('id')
            user_id = ''
            if is_sender: user_id = sender.get('id')
            else: user_id = receiver.get('id')
            chat_room_key = get_chat_room_key(user_id, other_user_id)
            join_room(chat_room_key)

    @socketio.on('chat/sent')
    def send_chat(new_chat):
        receiver = new_chat.get('receiver')
        sender = new_chat.get('sender')
        if not (receiver and sender): return
        receiver_id = receiver.get('id')
        sender_id = sender.get('id')
        chat_room_key = get_chat_room_key(sender_id, receiver_id)
        emit('chat/received', {**new_chat, 'other_user': sender, 'is_sender': False}, room=chat_room_key, broadcast=True)

    return app