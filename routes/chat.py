from flask import Blueprint, jsonify, request
from flask_login import current_user, login_required
from sqlalchemy import or_, and_, desc
from app import db
from config import Config
from models.User import User
from models.Chat import Chat
from utils.helpers import set_err_args, assign_res

chat = Blueprint('chat', __name__)

def get_last_chats(user_id:int):
    last_chats = Chat.query.filter(or_(Chat.sender_id == user_id, Chat.receiver_id == user_id), Chat.is_last_chat == True).all()
    return last_chats or []

@chat.route('/', methods=['POST'])
@login_required
def send_chat():
    try: 
        current_user_id = current_user.id
        receiver_id = int(request.json.get('receiverId'))
        message = request.json.get('message')

        if not receiver_id or current_user_id == receiver_id: raise Exception('Invalid receiver id.', 400)
        if not message: raise Exception('Message is empty.')

        receiver = User.query.get(receiver_id)
        if receiver is None: raise Exception('Receiver not found.', 404)

        last_chat = [chat for chat in get_last_chats(current_user.id) if chat.sender_id == receiver_id or chat.receiver_id == receiver_id]

        new_chat = Chat(sender_id=current_user_id, receiver_id=receiver_id, message=message)
        if last_chat and len(last_chat): last_chat[0].is_last_chat = False

        db.session.add(new_chat)
        db.session.commit()

        return jsonify({**assign_res(), "newChat": new_chat.to_dict(current_user_id)})
    except Exception as err:
        err_message, err_code = set_err_args(err.args)
        return jsonify({**assign_res('error'), 'message': err_message}), err_code

@chat.route('/', methods=['GET'])
@login_required
def get_recent_chats():
    try:
        last_chats = [chat.to_dict(current_user.id) for chat in get_last_chats(current_user.id)]
        return jsonify({**assign_res(), "chats": last_chats, "results": len(last_chats)})
    except Exception as err:
        err_message, err_code = set_err_args(err.args)
        return jsonify({**assign_res('error'), 'message': err_message}), err_code
    

@chat.route('/<other_user_id>', methods=['GET'])
@login_required
def get_chats_with(other_user_id):
    try:
        other_user_id = int(other_user_id)
        chats = Chat.query.filter(and_(
            or_(Chat.sender_id == current_user.id, Chat.sender_id == other_user_id),
            or_(Chat.receiver_id == current_user.id, Chat.receiver_id == other_user_id)
        )).all()

        chats = [chat.to_dict(current_user.id) for chat in chats]
        return jsonify({**assign_res(), "chats": chats, "results": len(chats)})
    except Exception as err:
        err_message, err_code = set_err_args(err.args)
        return jsonify({**assign_res('error'), 'message': err_message}), err_code

@chat.route('/<chat_id>', methods=['DELETE'])
@login_required
def delete_chat(chat_id):
    try:
        chat_id = int(chat_id)
        chat = Chat.query.get(chat_id)
        if not chat: raise Exception('Chat not found', 404)

        if chat.is_last_chat:
            other_user_id = chat.sender_id if current_user.id == chat.receiver_id else chat.receiver_id
            prev_chat = Chat.query.filter(and_(
            or_(Chat.sender_id == current_user.id, Chat.sender_id == other_user_id),
            or_(Chat.receiver_id == current_user.id, Chat.receiver_id == other_user_id))).order_by(desc(Chat.id)).offset(1).first()

            if prev_chat: prev_chat.is_last_chat = True


        db.session.delete(chat)
        db.session.commit()

        return jsonify({**assign_res(), "message": "Deleted Successfully"})
    except Exception as err:
        err_message, err_code = set_err_args(err.args)
        return jsonify({**assign_res('error'), 'message': err_message}), err_code