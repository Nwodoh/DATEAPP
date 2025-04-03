import os
import json
from flask_socketio import SocketIO, send, join_room, emit
from flask import Flask
from flask_cors import CORS
import firebase_admin
from firebase_admin import credentials, firestore
from config import config_by_name
from utils.helpers import get_chat_room_key

# Read Firebase credentials from environment variable
firebase_credentials = json.loads(os.getenv("FIREBASE_CREDENTIALS"))

# Initialize Firebase
cred = credentials.Certificate(firebase_credentials)
firebase_admin.initialize_app(cred)
db = firestore.client()

def create_app():
    app = Flask(__name__)
    socketio = SocketIO(app, cors_allowed_origins="*", cookie="True")
    CORS(app, resources={r"/*": {"supports_credentials": True}})

    app.config.from_object(config_by_name['development'])

    # Import and register blueprints
    from routes.auth import auth
    from routes.user import user
    from routes.chat import chat
    from routes.image import image
    from utils.FBQueries import FBQueries

    app.register_blueprint(auth, url_prefix='/api/v1/auth')
    app.register_blueprint(user, url_prefix='/api/v1/user')
    app.register_blueprint(chat, url_prefix='/api/v1/chat')
    app.register_blueprint(image, url_prefix='/api/v1/image')

    @socketio.on('connect')
    def handle_connect():
        send('Connected to socket', broadcast=True)

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
            receiver_id = chat.get('receiver_id')
            sender_id = chat.get('sender_id')
            is_sender = other_user['id'] != sender_id
            if not other_user: return
            other_user_id = other_user.get('id')
            user_id = sender_id if is_sender else receiver_id
            chat_room_key = get_chat_room_key(user_id, other_user_id)
            join_room(chat_room_key)

    @socketio.on('chat/sent')
    def send_chat(new_chat):
        receiver_id = new_chat.get('receiver_id')
        sender_id = new_chat.get('sender_id')

        if not (receiver_id and sender_id): return
        sender = FBQueries.get_user(sender_id)
        if not sender: return
        if "created_at" in sender:  
            sender["created_at"] = sender["created_at"].isoformat()
        new_chat['other_user'] = sender

        chat_room_key = get_chat_room_key(sender_id, receiver_id)
        emit('chat/received', new_chat, room=chat_room_key, broadcast=True)

    return app