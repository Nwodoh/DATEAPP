import requests
from flask import request, jsonify, g
from firebase_admin import auth, firestore
from google.cloud.firestore_v1.base_query import FieldFilter, Or
from email_validator import validate_email
from config import Config
from functools import wraps
import warnings
from werkzeug.security import generate_password_hash
from utils.helpers import generate_chat_id, get_chat_room_key


warnings.simplefilter("ignore", UserWarning)


db = firestore.client()
users_ref = db.collection("users")
chats_ref = db.collection("chats")

class FBQueries:
    @staticmethod
    def user_dict(user, with_password=False):
        return {
                "uid": user["uid"] if "uid" in user else '',
                "id": user["uid"] if "uid" in user else '',
                "email": user["email"] if "email" in user else '',
                "name": user["name"] if "name" in user else '',
                "username": user["username"] if "username" in user else '',
                "about": user["about"] if "about" in user else '',
                "profile_image": user["profile_image"] if "profile_image" in user else '',
                "gender": user["background_image"] if "background_image" in user else '',
                "orientation": user["background_image"] if "background_image" in user else '',
                "date_of_birth": user["date_of_birth"] if "date_of_birth" in user else '',
                "background_image": user["background_image"] if "background_image" in user else '', 
                "location": user["location"] if "location" in user else [55.1694, 23.8813], 
                "email_verified": user["email_verified"] if "email_verified" in user else False,
                "liked_users": user["liked_users"] if "liked_users" in user else [],
                "likes": user["likes"] if "likes" in user else [],
                "created_at": user["created_at"] if "created_at" in user else '',
                "password": '' if not with_password else user["password"] if "password" in user else '',
            }
    @staticmethod
    def chat_dict(chat):
        return {
            'id': chat["id"] if "id" in chat else '',
            'sender_id': chat["sender_id"] if "sender_id" in chat else '',
            'receiver_id': chat["receiver_id"] if "receiver_id" in chat else '',
            'room_key': chat["room_key"] if "room_key" in chat else '',
            'message': chat["message"] if "message" in chat else '',
            'is_last_chat': chat["is_last_chat"] if "is_last_chat" in chat else True,
            'created_at': chat["created_at"] if "created_at" in chat else firestore.SERVER_TIMESTAMP,
        }
    
    def new_user(self, email, password):
        user = auth.create_user(email=email, password=password)

        user_data = self.user_dict({
            "uid": user.uid,
            "id": user.uid,
            "email": email,
            "created_at": firestore.SERVER_TIMESTAMP,
            "password": generate_password_hash(password, method='pbkdf2:sha256'),
        }, with_password=True)
        doc_ref = users_ref.document(user.uid)  
        doc_ref.set(user_data)  
        user = doc_ref.get()

        if not user.exists:
            raise Exception('Unable to create user. please try loging in.', 400)

        return user.to_dict()

    @staticmethod
    def get_user(id, with_password=False):
        query = users_ref.where("id", "==", id).limit(1)
        results = query.stream()
        user = None
        for doc in results:
            user = doc.to_dict()
            user['password'] = user['password'] if with_password else ''
        return user

    def get_user_by_email(self, email, with_password=False, with_likes=False):
        valid = validate_email(email)
        email = valid.email
        query = users_ref.where("email", "==", email).limit(1)
        results = query.stream()
        user = None

        
        for doc in results:
            user = doc.to_dict()
            user['password'] = user['password'] if with_password else ''
            if with_likes: user['likes'] = self.get_multiple_users(user["likes"] or [])
        return user

    def login(email:str, password:str):
        payload = {"email": email, "password": password, "returnSecureToken": True}
    
        response = requests.post(Config.FIREBASE_WEB_API_URL, json=payload)

        if response.status_code == 200:
            data = response.json()
            return data["idToken"],  # Token for authentication
        else:
            raise Exception('Incorrect authentification details. Please check you email or password')

    @staticmethod
    def update_user(user_id, update_data={}):
        doc_ref = users_ref.document(user_id)
        doc_ref.update(update_data)
        user = doc_ref.get()
        return user.to_dict()

    def update_me(self, update_data={}):
        user_id = g.current_user['uid']
        user = self.update_user(user_id, update_data)
        return user
    
    def update_password(user_id, password): 
        user = auth.update_user(user_id, password=password)
        doc_ref = users_ref.document(user_id)
        doc_ref.update({"password": generate_password_hash(password, method='pbkdf2:sha256')})
        user = doc_ref.get()
        return user.to_dict()
    
    def get_all_users():
        users = users_ref.stream()
        users_list = [{**user.to_dict(), "id": user.id} for user in users]
        return users_list
    
    @staticmethod
    def get_multiple_users(id_list=[]):
        if not len(id_list): return []
        users = users_ref.where("id", "in", id_list).stream()
        users_list = [{**user.to_dict(), "id": user.id} for user in users]
        return users_list
    
    def query_users(search_str: str):        
        users = users_ref.stream()
        search_str = search_str.lower()

        results = []
        
        for doc in users:
            data = doc.to_dict()
            name = data.get("name", "").lower()
            username = data.get("username", "").lower()
            
            if name.startswith(search_str):
                results.append(data)
                continue
            if username.startswith(search_str):
                results.append(data)
        return results
    
    def verify_token():
        auth_header = request.headers.get("Authorization")

        if not auth_header or not auth_header.startswith("Bearer "):
            raise Exception('Not Logged In')
        token = auth_header.split(" ")[1]  # Extract token from "Bearer <token>"
        try:
            decoded_token = auth.verify_id_token(token)
            return decoded_token  # Returns decoded user info
        except Exception as e:
            raise Exception('Not Logged In')
        
    def like(self, other_user_id):
        user_id = g.current_user['uid']
        update_data = {"likes": firestore.ArrayUnion([user_id])}
        user = self.update_user(user_id=other_user_id, update_data=update_data)
        return user
    
    def remove_like(self, other_user_id):
        user_id = g.current_user['uid']
        update_data = {"likes": firestore.ArrayRemove([user_id])}
        user = self.update_user(user_id=other_user_id, update_data=update_data)
        return user
    
    def get_last_chats(self, user_id):
        last_chats = []
        chats_classes = chats_ref.where("is_last_chat", "==", True).where(
            filter=Or(
                [
                    FieldFilter("sender_id", "==", user_id),
                    FieldFilter("receiver_id", "==", user_id),
                ]
            )
        ).stream()

        for chat in chats_classes:
            chat_dict = chat.to_dict()
            chat_dict['other_user'] = self.get_other_user_in_chat(chat_dict)
            last_chats.append(chat_dict)

        return last_chats
    
    def get_other_user_in_chat(self, chat):
        user_id = g.current_user['uid']
        chat_sender = chat['sender_id']
        chat_receiver = chat['receiver_id']

        if chat['sender_id'] != user_id: return self.get_user(id=chat_sender)
        else: return self.get_user(chat_receiver)

    def update_chat(self, chat_id, update_data={}):
        doc_ref = chats_ref.document(chat_id)
        doc_ref.update(update_data)
        chat = doc_ref.get()
        return chat.to_dict()
    
    def new_chat(self, sender_id:str, receiver_id:str, message):
        new_chat_id = generate_chat_id(first_user=sender_id, second_user=receiver_id)
        chat_data = self.chat_dict({
            "id": new_chat_id,
            "room_key": get_chat_room_key(sender_id, receiver_id),
            "sender_id": sender_id,
            "receiver_id":receiver_id,
            "message":message,
        })
        doc_ref = chats_ref.document(new_chat_id)  
        doc_ref.set(chat_data)  
        chat = doc_ref.get()
        chat_dict = chat.to_dict()
        chat_dict['other_user'] = self.get_other_user_in_chat(chat_dict)
        return chat_dict

    def get_chats(other_user_id): 
        user_id = g.current_user['uid']
        room_key = get_chat_room_key(user_id, other_user_id)
        chats = chats_ref.where('room_key', '==', room_key).stream()
        chat_list = [chat.to_dict() for chat in chats]
        return chat_list

def firebase_auth_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        auth_header = request.headers.get("Authorization")

        if not auth_header or not auth_header.startswith("Bearer "):
            return jsonify({"error": "Unauthorized - No token provided"}), 401

        token = auth_header.split(" ")[1]  # Extract token

        try:
            decoded_token = auth.verify_id_token(token, clock_skew_seconds=5)
            g.current_user = decoded_token  # Store user info in Flask's global context
            return f(*args, **kwargs)
        except Exception as e:
            return jsonify({"error": "Unauthorized - Invalid token"}), 401

    return decorated_function